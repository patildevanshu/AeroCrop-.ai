"""
AeroCrop.ai — Dedicated Email Runtime Logging & Auditing Subsystem

Guarantees:
  1. Persistent file logging to logs/email_runtime.log with auto-rotation (5MB x 5 backups).
  2. Clear console output with high-visibility tags for every dispatch attempt.
  3. In-memory circular buffer for immediate live API inspection via GET /api/auth/email-logs.
  4. Asynchronous MongoDB audit trail in email_logs collection.
"""

from __future__ import annotations
import collections
import logging
from logging.handlers import RotatingFileHandler
import os
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    import backend.config as config
except ImportError:
    import config


# ── Ensure Log Directory & Handlers ───────────────────────────────────────────
os.makedirs(config.LOGS_DIR, exist_ok=True)

dispatcher_logger = logging.getLogger("aerocrop.email.dispatcher")

_formatter = logging.Formatter(
    fmt="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_file_handler_exists = any(
    isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", "") == os.path.abspath(config.EMAIL_RUNTIME_LOG_PATH)
    for h in dispatcher_logger.handlers
)

if not _file_handler_exists:
    try:
        file_handler = RotatingFileHandler(
            config.EMAIL_RUNTIME_LOG_PATH,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(_formatter)
        dispatcher_logger.addHandler(file_handler)
        dispatcher_logger.setLevel(logging.INFO)
    except Exception as exc:
        print(f"[EmailLogger] Warning: Could not initialize rotating file handler: {exc}")


# ── In-Memory Audit Buffer (Most recent 100 dispatch events) ───────────────────
_RECENT_EMAIL_LOGS: collections.deque = collections.deque(maxlen=100)


class EmailAuditLogger:
    @staticmethod
    def log_attempt(
        recipient: str,
        purpose: str,
        provider: str,
        method: str,
    ) -> float:
        """
        Logs the initiation of an email delivery try. Returns start time epoch for latency tracking.
        """
        start_time = time.time()
        msg = f"[EMAIL_DISPATCH_ATTEMPT] Recipient: {recipient} | Purpose: {purpose} | Provider: {provider} | Method: {method}"
        dispatcher_logger.info(msg)

        _RECENT_EMAIL_LOGS.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "attempt",
            "recipient": recipient,
            "purpose": purpose,
            "provider": provider,
            "method": method,
            "status": "pending",
        })
        return start_time

    @staticmethod
    def log_success(
        recipient: str,
        purpose: str,
        method: str,
        provider: str,
        start_time: float,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Logs successful delivery with latency and provider details.
        """
        duration_ms = round((time.time() - start_time) * 1000, 1)
        msg = (
            f"[EMAIL_DISPATCH_SUCCESS] Successfully delivered to {recipient} [{purpose}] "
            f"via {method} ({provider}) in {duration_ms}ms"
        )
        dispatcher_logger.info(msg)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "success",
            "recipient": recipient,
            "purpose": purpose,
            "method": method,
            "provider": provider,
            "duration_ms": duration_ms,
            "status": "delivered",
            "details": details or {},
        }
        _RECENT_EMAIL_LOGS.append(entry)
        return entry

    @staticmethod
    def log_retry(
        recipient: str,
        purpose: str,
        failed_method: str,
        next_method: str,
        error: str,
    ) -> None:
        """
        Logs a transient failure and indicates the switch to a fallback channel.
        """
        msg = (
            f"[EMAIL_DISPATCH_RETRY] Delivery to {recipient} via {failed_method} failed: {error}. "
            f"Flipping to secondary fallback {next_method}..."
        )
        dispatcher_logger.warning(msg)

        _RECENT_EMAIL_LOGS.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "retry",
            "recipient": recipient,
            "purpose": purpose,
            "failed_method": failed_method,
            "next_method": next_method,
            "error": str(error),
            "status": "retrying",
        })

    @staticmethod
    def log_failure(
        recipient: str,
        purpose: str,
        method: str,
        provider: str,
        start_time: float,
        error: str,
        exc_info: Optional[Exception] = None,
        code_for_dev_fallback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Logs a final delivery failure with full stack trace and optional DEV_FALLBACK code.
        """
        duration_ms = round((time.time() - start_time) * 1000, 1) if start_time else 0.0
        tb_str = "".join(traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__)) if exc_info else None
        
        msg = (
            f"[EMAIL_DISPATCH_FAILED] Delivery failed for {recipient} [{purpose}] via {method} ({provider}) "
            f"after {duration_ms}ms. Error: {error}"
        )
        dispatcher_logger.error(msg)
        if tb_str:
            dispatcher_logger.debug(f"[EMAIL_DISPATCH_TRACEBACK]\n{tb_str}")

        if code_for_dev_fallback:
            dev_msg = f"[DEV_FALLBACK] Generated OTP for {recipient} is [{code_for_dev_fallback}]. Note: External delivery failed."
            dispatcher_logger.warning(dev_msg)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "failure",
            "recipient": recipient,
            "purpose": purpose,
            "method": method,
            "provider": provider,
            "duration_ms": duration_ms,
            "status": "failed",
            "error": str(error),
            "traceback": tb_str,
        }
        _RECENT_EMAIL_LOGS.append(entry)
        return entry

    @staticmethod
    async def record_to_mongodb(
        db: Any,
        log_entry: Dict[str, Any],
    ) -> None:
        """
        Asynchronously persists the log entry to MongoDB email_logs collection.
        Fails silently to avoid impeding request execution.
        """
        if db is None:
            return
        try:
            doc = {**log_entry, "created_at": datetime.now(timezone.utc)}
            await db.email_logs.insert_one(doc)
        except Exception as exc:
            dispatcher_logger.debug("[EmailLogger] Non-critical: Could not record email log to MongoDB: %s", exc)

    @classmethod
    def get_recent_logs(cls, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Returns recent in-memory log entries in reverse chronological order.
        """
        items = list(_RECENT_EMAIL_LOGS)
        items.reverse()
        return items[:limit]

    @classmethod
    def get_runtime_log_tail(cls, max_lines: int = 150) -> str:
        """
        Reads the tail of logs/email_runtime.log directly from disk for raw runtime log inspection.
        """
        log_file = config.EMAIL_RUNTIME_LOG_PATH
        if not os.path.exists(log_file):
            return f"Log file {log_file} does not exist yet."
        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                return "".join(lines[-max_lines:])
        except Exception as exc:
            return f"Error reading runtime log: {exc}"
