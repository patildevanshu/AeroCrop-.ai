"""
AeroCrop.ai — Unit & Integration Tests for Email Service & Report Endpoints
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport, Response
from main import app
from services.email_service import EmailService


@pytest.mark.anyio
async def test_email_service_invalid_email():
    res = await EmailService.dispatch_report_email(
        farmer_email="invalid-email-string",
        report_data={"crop": "Tomato"},
    )
    assert res["success"] is False
    assert "Invalid email" in res["error"]


@pytest.mark.anyio
async def test_email_service_fallback_when_microservice_unreachable():
    with patch("config.EMAIL_SERVICE_URL", "http://127.0.0.1:59999/send-email"):
        with patch.object(
            EmailService,
            "_send_direct_smtp_sync",
            return_value={
                "success": True,
                "method": "python_smtp_direct",
                "message": "Fallback report delivered",
            },
        ) as mock_smtp:
            res = await EmailService.dispatch_report_email(
                farmer_email="farmer@example.com",
                report_data={"crop": "Tomato", "district": "Pune"},
                farmer_name="Ramesh",
            )
            assert res["success"] is True
            assert res["method"] == "python_smtp_direct"
            assert mock_smtp.called


@pytest.mark.anyio
async def test_email_service_read_timeout_suppresses_duplicate():
    import httpx
    with patch("httpx.AsyncClient.post", side_effect=httpx.ReadTimeout("Timed out waiting for response")):
        with patch.object(EmailService, "_send_direct_smtp_sync") as mock_smtp:
            res = await EmailService.dispatch_report_email(
                farmer_email="farmer@example.com",
                report_data={"crop": "Tomato", "district": "Pune"},
                farmer_name="Ramesh",
            )
            assert res["success"] is True
            assert res["method"] == "microservice_in_flight"
            assert not mock_smtp.called


@pytest.mark.anyio
async def test_email_service_both_services_fail_gracefully():
    with patch("config.EMAIL_SERVICE_URL", "http://127.0.0.1:59999/send-email"):
        with patch.object(
            EmailService,
            "_send_direct_smtp_sync",
            side_effect=RuntimeError("SMTP Authentication Error"),
        ):
            res = await EmailService.dispatch_report_email(
                farmer_email="farmer@example.com",
                report_data={"crop": "Tomato", "district": "Pune"},
            )
            assert res["success"] is False
            assert "fallback failed" in res["error"].lower()


@pytest.mark.anyio
async def test_email_service_mock_success():
    with patch.object(
        EmailService,
        "dispatch_report_email",
        return_value={"success": True, "details": {"messageId": "msg-12345"}},
    ):
        res = await EmailService.dispatch_report_email(
            farmer_email="farmer.test@example.com",
            report_data={
                "crop": "Tomato",
                "district": "Pune",
                "yield_t_ha": 25.0,
                "disease": {"name": "Healthy", "confidence": 98.0},
            },
            farmer_name="Test Farmer",
        )
        assert res["success"] is True
        assert res["details"]["messageId"] == "msg-12345"


@pytest.mark.anyio
async def test_email_report_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch(
            "controllers.predict_controller.EmailService.dispatch_report_email",
            new_callable=AsyncMock,
            return_value={"success": True, "details": {"messageId": "msg-999"}},
        ):
            payload = {
                "email": "farmer@example.com",
                "name": "Devanshu",
                "crop": "Tomato",
                "district": "Pune",
                "disease": {"name": "Early Blight", "confidence": 95.0, "severity": "High"},
                "yield_t_ha": 22.4,
            }
            res = await client.post("/api/predict/email-report", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "success"
            assert "farmer@example.com" in data["message"]
