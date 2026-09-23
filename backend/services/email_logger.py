"""
AeroCrop.ai — Dedicated Email Runtime Terminal Logging Subsystem

Pure in-memory and runtime terminal logging.
No persistent files or database records are stored on disk.
Prints rich, structured diagnostic details for every email attempt, retry, success, and failure.
Guarantees full compatibility across Windows cmd, PowerShell, Linux, and macOS terminals.
"""

from __future__ import annotations
import collections
import logging
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    import backend.config as config
except ImportError:
    import config

logger = logging.getLogger("aerocrop.email")

# Try to ensure UTF-8 on Windows stdout if supported
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# In-memory circular buffer for active runtime inspection (last 100 events in RAM only)
_RECENT_EMAIL_LOGS: collections.deque = collections.deque(maxlen=100)


def _print_box(title: str, lines: List[str], border_char: str = "=", width: int = 78) -> None:
    """Print a clean visual box to terminal stdout safely across all encodings."""
    border = border_char * width
    output = [
        "",
        border,
        f" {title}",
        "-" * width,
    ]
    for line in lines:
        output.append(f"   {line}")
    output.append(border)
    output.append("")
    text = "\n".join(output) + "\n"
    try:
        sys.stdout.write(text)
        sys.stdout.flush()
    except (UnicodeEncodeError, Exception):
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        safe_text = text.encode(encoding, errors="replace").decode(encoding)
        sys.stdout.write(safe_text)
        sys.stdout.flush()


class EmailAuditLogger:
    @staticmethod
    def log_attempt(
        recipient: str,
        purpose: str,
        provider: str,
        method: str,
    ) -> float:
        """
        Logs initiation of an email delivery attempt with full runtime parameters to terminal.
        """
        start_time = time.time()
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [
            f"Timestamp    : {now_str}",
            f"Recipient    : {recipient}",
            f"Purpose      : {purpose}",
            f"Channel      : {method}",
            f"Server Host  : {provider}",
            f"Sender User  : {config.SMTP_USER}",
            f"Timeout      : {config.SMTP_TIMEOUT_SECONDS}s",
            f"Status       : INITIATING CONNECTION...",
        ]
        _print_box("[EMAIL RUNTIME ATTEMPT] - Dispatching Verification Message", lines, border_char="=")

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
    def log_retry(
        recipient: str,
        purpose: str,
        failed_method: str,
        next_method: str,
        error: str,
    ) -> None:
        """
        Logs a transient connection failure and switch to alternate fallback channel in terminal.
        """
        lines = [
            f"Recipient    : {recipient}",
            f"Purpose      : {purpose}",
            f"Failed Via   : {failed_method}",
            f"Failure Cause: {error}",
            f"Action Taken : [RETRY] Switching immediately to fallback -> [{next_method}]",
        ]
        _print_box("[EMAIL RUNTIME RETRY] - Channel Failed, Engaging Fallback", lines, border_char="-")

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
    def log_success(
        recipient: str,
        purpose: str,
        method: str,
        provider: str,
        start_time: float,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Logs successful delivery with duration in ms and relay info in terminal.
        """
        duration_ms = round((time.time() - start_time) * 1000, 1)
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [
            f"Timestamp    : {now_str}",
            f"Recipient    : {recipient}",
            f"Purpose      : {purpose}",
            f"Delivered Via: {method} ({provider})",
            f"Latency      : {duration_ms} ms ({duration_ms/1000:.2f}s)",
            f"Delivery Res : [SUCCESS] Accepted by remote mail server (DELIVERED)",
        ]
        if details:
            msg_id = details.get("details", {}).get("messageId") or details.get("messageId")
            if msg_id:
                lines.append(f"Message-ID   : {msg_id}")

        _print_box("[EMAIL RUNTIME SUCCESS] - Delivery Succeeded", lines, border_char="=")

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
        Logs final failure with error type, message, traceback, and OTP recovery in terminal.
        """
        duration_ms = round((time.time() - start_time) * 1000, 1) if start_time else 0.0
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        tb_lines = traceback.format_exception(type(exc_info), exc_info, exc_info.__traceback__) if exc_info else []

        lines = [
            f"Timestamp    : {now_str}",
            f"Recipient    : {recipient}",
            f"Purpose      : {purpose}",
            f"Exhausted On : {method} ({provider})",
            f"Elapsed Time : {duration_ms} ms",
            f"Error Type   : {type(exc_info).__name__ if exc_info else 'UnknownError'}",
            f"Error Details: {error}",
        ]

        if tb_lines:
            lines.append("Traceback    :")
            for tb_l in "".join(tb_lines).strip().splitlines()[-4:]:
                lines.append(f"   {tb_l}")

        if code_for_dev_fallback:
            lines.append("-" * 72)
            lines.append(f"[DEV / RECOVERY OTP CODE] : [{code_for_dev_fallback}]")
            lines.append("   (Use this code to sign in/verify if external SMTP is offline)")

        _print_box("[EMAIL RUNTIME FAILURE] - All Channels Failed", lines, border_char="=")

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
        }
        _RECENT_EMAIL_LOGS.append(entry)
        return entry

    @staticmethod
    async def record_to_mongodb(db: Any, log_entry: Dict[str, Any]) -> None:
        """No-op: persistent database storage is disabled per user preference."""
        pass

    @classmethod
    def get_recent_logs(cls, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent in-memory log entries in reverse chronological order (RAM only)."""
        items = list(_RECENT_EMAIL_LOGS)
        items.reverse()
        return items[:limit]

    @classmethod
    def get_runtime_log_tail(cls, max_lines: int = 50) -> str:
        """Returns recent in-memory log summary."""
        items = cls.get_recent_logs(max_lines)
        if not items:
            return "No runtime email events logged in current session."
        return "\n".join(
            f"[{item['timestamp']}] {item['event'].upper()}: {item.get('recipient')} ({item.get('purpose')}) - {item.get('status')} [{item.get('method', '')}]"
            for item in items
        )
