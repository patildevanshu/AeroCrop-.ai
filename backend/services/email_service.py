"""
AeroCrop.ai — Email Microservice Client

Dispatches crop analysis reports, pathology diagnoses, fertilizer advice,
and weather telemetry to the Node.js email service to generate a PDF and
email it directly to the farmer.
"""

from __future__ import annotations
import logging
import httpx
from typing import Any, Dict, Optional

import config

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    async def dispatch_report_email(
        farmer_email: str,
        report_data: Dict[str, Any],
        farmer_name: str = "Farmer",
    ) -> Dict[str, Any]:
        """
        Sends the diagnostic report payload to the AeroCrop Node.js email microservice.
        The microservice generates the PDF advisory and dispatches it via Gmail SMTP to farmer_email.
        
        This method is designed to be safe for background execution and never raises an unhandled
        exception that would crash the main application.
        """
        if not farmer_email or "@" not in farmer_email:
            logger.warning("[EmailService] Invalid recipient email provided: %s", farmer_email)
            return {"success": False, "error": "Invalid email address"}

        payload = {
            "email": farmer_email,
            "name": farmer_name,
            "crop": report_data.get("crop", "Crop"),
            "district": report_data.get("district", "Maharashtra"),
            "yield_t_ha": report_data.get("yield_t_ha"),
            "disease": report_data.get("disease", {}),
            "fertilizer": report_data.get("fertilizer", {}),
            "weather": report_data.get("weather", {}),
        }

        url = config.EMAIL_SERVICE_URL
        logger.info("[EmailService] Dispatching advisory PDF email to %s via %s", farmer_email, url)

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    resp_json = response.json()
                    logger.info("[EmailService] Email successfully dispatched to %s: %s", farmer_email, resp_json)
                    return {"success": True, "details": resp_json}
                else:
                    logger.warning(
                        "[EmailService] Email service responded with HTTP %d: %s",
                        response.status_code,
                        response.text,
                    )
                    return {
                        "success": False,
                        "error": f"Email service HTTP {response.status_code}",
                        "details": response.text,
                    }
        except httpx.ConnectError:
            logger.warning(
                "[EmailService] Could not connect to email service at %s. Ensure 'npm start' is running in email_service/.",
                url,
            )
            return {
                "success": False,
                "error": f"Email service unreachable at {url}. Ensure email_service microservice is running.",
            }
        except Exception as exc:
            logger.error("[EmailService] Exception while dispatching email to %s: %s", farmer_email, exc)
            return {"success": False, "error": str(exc)}
