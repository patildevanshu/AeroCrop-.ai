"""
AeroCrop.ai — Agronomic Ensemble Verification Service

MVC Role: Service Layer
Provides a non-blocking asynchronous bridge to the distributed secondary
pathway validator microservice. If the microservice is unreachable, times out,
or is disabled, the service gracefully degrades to local model predictions
with zero user interruption.
"""

from __future__ import annotations
import logging
import time
from typing import Any, Optional

import httpx

import backend.config as config

logger = logging.getLogger(__name__)

# Lightweight circuit breaker: if validator is offline, skip pinging for 15s
_offline_until: float = 0.0


class EnsembleService:
    """
    Client for the standalone distributed agronomic validation service.
    Acts as an ensemble arbitrator for specimen pathology verification.
    """

    @classmethod
    async def verify(
        cls,
        image_bytes: bytes,
        district: str,
        weather: dict[str, Any],
        local_crop: str,
        local_class_idx: int,
        local_confidence: float,
        N: Optional[float] = None,
        P: Optional[float] = None,
        K: Optional[float] = None,
    ) -> dict[str, Any] | None:
        """
        Submits specimen imagery and environmental context to the validator microservice.

        Returns:
            dict containing arbitrated diagnostic findings if verified, or None if skipped/failed.
        """
        global _offline_until

        if not getattr(config, "ENABLE_REMOTE_VALIDATOR", True):
            return None

        # If previously determined to be offline, bypass instantly
        if time.time() < _offline_until:
            return None

        endpoint = getattr(config, "VALIDATOR_SERVICE_URL", "http://127.0.0.1:5005/api/v1/validate")
        timeout_sec = getattr(config, "VALIDATOR_TIMEOUT_SECONDS", 35.0)

        form_data = {
            "district": district,
            "temperature": str(weather.get("temperature", 28.0)),
            "humidity": str(weather.get("humidity", 65.0)),
            "rainfall": str(weather.get("rainfall", 0.0)),
            "local_crop": local_crop or "auto",
            "local_class_idx": str(local_class_idx),
            "local_confidence": str(round(local_confidence, 4)),
        }
        if N is not None:
            form_data["soil_N"] = str(N)
        if P is not None:
            form_data["soil_P"] = str(P)
        if K is not None:
            form_data["soil_K"] = str(K)

        files = {
            "image": ("specimen.jpg", image_bytes, "image/jpeg"),
        }

        # Fast connect timeout (2.5s) so offline state is caught quickly, but ample read timeout for vision model
        client_timeout = httpx.Timeout(timeout_sec, connect=2.5)

        try:
            async with httpx.AsyncClient(timeout=client_timeout) as client:
                response = await client.post(endpoint, data=form_data, files=files)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("verified") and "class_idx" in data:
                        logger.info(
                            "[EnsembleService] Consensus reached: class_idx=%s, crop=%s (confidence=%.2f%%)",
                            data.get("class_idx"),
                            data.get("crop"),
                            (data.get("confidence", 0.95) * 100),
                        )
                        return data
                    elif data.get("out_of_distribution") or data.get("is_supported") is False:
                        logger.info("[EnsembleService] Remote node flagged specimen as out-of-distribution: %s", data.get("reason"))
                        return data
                    else:
                        logger.debug("[EnsembleService] Remote service returned unverified payload: %s", data)
                else:
                    logger.debug("[EnsembleService] Validator returned HTTP %d", response.status_code)

        except (httpx.ConnectError, httpx.ConnectTimeout):
            _offline_until = time.time() + 15.0
            logger.debug("[EnsembleService] Standalone validator not reachable at %s — local pathway engaged", endpoint)
        except httpx.TimeoutException:
            _offline_until = time.time() + 10.0
            logger.debug("[EnsembleService] Standalone validator timed out (>%.1fs) — local pathway engaged", timeout_sec)
        except Exception as exc:
            logger.debug("[EnsembleService] Standalone validator error: %s — local pathway engaged", exc)

        return None
