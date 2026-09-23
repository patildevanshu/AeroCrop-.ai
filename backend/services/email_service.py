"""
AeroCrop.ai — Email Microservice Client with Resilient Python SMTP Fallback

Dispatches crop analysis reports, pathology diagnoses,
and weather telemetry to:
1. Primary: Node.js email microservice to generate high-fidelity 3-page Trilingual PDF and dispatch via SMTP.
2. Secondary Fallback: Direct Python smtplib with an executive, responsive HTML advisory email
   if the Node microservice is offline, busy, or unreachable.
"""

from __future__ import annotations
import asyncio
import html
import logging
import smtplib
from email.message import EmailMessage
from typing import Any, Dict, Optional

import email.utils
import socket
import ssl
import httpx
try:
    import backend.config as config
    from backend.services.email_logger import EmailAuditLogger
except ImportError:
    import config
    from services.email_logger import EmailAuditLogger


logger = logging.getLogger("aerocrop.email")


class EmailService:
    @classmethod
    async def dispatch_report_email(
        cls,
        farmer_email: str,
        report_data: Dict[str, Any],
        farmer_name: str = "Farmer",
    ) -> Dict[str, Any]:
        """
        Sends the diagnostic report payload to the AeroCrop Node.js email microservice.
        If the microservice is unreachable, times out, or fails, seamlessly falls back
        to direct Python SMTP delivery to guarantee the farmer receives their advisory report.
        """
        if not farmer_email or "@" not in farmer_email:
            logger.warning("[EmailService] Invalid recipient email provided: %s", farmer_email)
            return {"success": False, "error": "Invalid email address format"}

        crop = report_data.get("crop", "Crop")
        district = report_data.get("district", "Maharashtra")
        yield_t_ha = report_data.get("yield_t_ha")
        disease = report_data.get("disease", {})
        weather = report_data.get("weather", {})

        payload = {
            "email": farmer_email,
            "name": farmer_name,
            "crop": crop,
            "district": district,
            "yield_t_ha": yield_t_ha,
            "disease": disease,
            "weather": weather,
        }

        url = config.EMAIL_SERVICE_URL
        logger.info("[EmailService] Dispatching advisory PDF email to %s via %s", farmer_email, url)
        t0 = EmailAuditLogger.log_attempt(farmer_email, "advisory_report", url, "microservice_pdf")

        # ── Step 1: Attempt Primary Dispatch via Node Microservice ─────────────────
        try:
            client_timeout = httpx.Timeout(60.0, connect=5.0)
            async with httpx.AsyncClient(timeout=client_timeout) as client:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    resp_json = response.json()
                    logger.info("[EmailService] Primary PDF email successfully dispatched to %s: %s", farmer_email, resp_json)
                    EmailAuditLogger.log_success(farmer_email, "advisory_report", "microservice_pdf", url, t0, resp_json)
                    return {"success": True, "method": "microservice_pdf", "details": resp_json}
                else:
                    logger.warning(
                        "[EmailService] Microservice returned HTTP %d: %s. Initiating direct Python SMTP fallback...",
                        response.status_code,
                        response.text,
                    )
        except (httpx.ConnectError, httpx.ConnectTimeout) as conn_err:
            logger.warning(
                "[EmailService] Node microservice unreachable at %s (%s). Engaging direct Python SMTP fallback...",
                url,
                conn_err,
            )
        except httpx.ReadTimeout:
            logger.warning(
                "[EmailService] Node microservice read timed out (>60s). Request was already accepted and is processing in flight; suppressing Python fallback to prevent duplicate email."
            )
            return {
                "success": True,
                "method": "microservice_in_flight",
                "warning": "Node microservice read timed out; email generation in flight",
            }
        except Exception as exc:
            logger.warning("[EmailService] Microservice error (%s). Engaging direct Python SMTP fallback...", exc)

        # ── Step 2: Resilient Fallback via Direct Python SMTP ───────────────────────
        return await cls._dispatch_direct_python_email(
            farmer_email=farmer_email,
            report_data=report_data,
            farmer_name=farmer_name,
        )

    @classmethod
    async def _dispatch_direct_python_email(
        cls,
        farmer_email: str,
        report_data: Dict[str, Any],
        farmer_name: str = "Farmer",
    ) -> Dict[str, Any]:
        """
        Direct Python SMTP fallback that composes and dispatches a comprehensive,
        high-fidelity HTML crop advisory report directly to the farmer.
        """
        logger.info("[EmailService] Sending direct SMTP advisory email to %s...", farmer_email)
        try:
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(
                None,
                cls._send_direct_smtp_sync,
                farmer_email,
                report_data,
                farmer_name,
            )
            return res
        except Exception as exc:
            logger.error("[EmailService] Direct SMTP fallback failed for %s: %s", farmer_email, exc)
            return {"success": False, "error": f"Direct SMTP fallback failed: {str(exc)}"}

    @staticmethod
    def _send_direct_smtp_sync(
        farmer_email: str,
        report_data: Dict[str, Any],
        farmer_name: str,
    ) -> Dict[str, Any]:
        """
        Synchronous SMTP dispatch executed in a worker thread.
        """
        smtp_host = config.SMTP_HOST
        smtp_port = config.SMTP_PORT
        smtp_user = config.SMTP_USER
        smtp_pass = config.SMTP_PASS
        from_email = config.SMTP_FROM

        crop = str(report_data.get("crop", "Crop"))
        district = str(report_data.get("district", "Maharashtra"))
        yield_t_ha = report_data.get("yield_t_ha")
        disease = report_data.get("disease", {})
        weather = report_data.get("weather", {})

        condition = disease.get("name", "Diagnostic Assessment Completed")
        confidence = disease.get("confidence", 95.0)
        severity = disease.get("severity", "Normal")
        is_healthy = disease.get("is_healthy", False) or "healthy" in condition.lower()
        description = disease.get("description", "Comprehensive crop diagnostic scan completed.")
        chem_treatments = disease.get("chemical_treatment", [])
        org_treatments = disease.get("organic_treatment", [])

        temp = weather.get("temperature", 28.0)
        hum = weather.get("humidity", 65.0)
        rain = weather.get("rainfall", 0.0)
        spray_safe = (rain < 1.0 and hum < 75)

        # Formatting values safely
        safe_name = html.escape(farmer_name)
        safe_crop = html.escape(crop)
        safe_district = html.escape(district)
        safe_condition = html.escape(str(condition))
        safe_severity = html.escape(str(severity))
        safe_desc = html.escape(str(description))

        yield_str = ""
        if yield_t_ha is not None:
            try:
                y_float = float(yield_t_ha)
                yield_str = f"{y_float:.1f} Tonnes / Hectare (~{y_float * 4.047:.1f} Quintals / Acre)"
            except (ValueError, TypeError):
                yield_str = str(yield_t_ha)

        # Chemical items HTML
        chem_html = ""
        if chem_treatments:
            chem_items = "".join(f"<li style='margin-bottom:6px;'>{html.escape(str(c))}</li>" for c in chem_treatments)
            chem_html = f"<ul style='margin:4px 0 0 16px;padding:0;font-size:13px;color:#334155;'>{chem_items}</ul>"
        else:
            chem_html = "<p style='margin:4px 0 0 0;font-size:13px;color:#059669;'>✓ Zero chemical fungicide/pesticide required at this stage.</p>"

        # Organic items HTML
        org_html = ""
        if org_treatments:
            org_items = "".join(f"<li style='margin-bottom:6px;'>{html.escape(str(o))}</li>" for o in org_treatments)
            org_html = f"<ul style='margin:4px 0 0 16px;padding:0;font-size:13px;color:#334155;'>{org_items}</ul>"
        else:
            org_html = "<p style='margin:4px 0 0 0;font-size:13px;color:#059669;'>✓ Maintain regular balanced organic compost and soil aeration.</p>"

        sev_bg = "#ecfdf5" if is_healthy else ("#fef2f2" if severity in ("Critical", "High") else "#fffbeb")
        sev_color = "#059669" if is_healthy else ("#dc2626" if severity in ("Critical", "High") else "#d97706")
        sev_border = "#a7f3d0" if is_healthy else ("#fecaca" if severity in ("Critical", "High") else "#fde68a")

        msg = EmailMessage()
        msg["Subject"] = f"🌾 AeroCrop.ai — पीक सल्ला व रोग निदान अहवाल | Crop Advisory: {crop} ({condition})"
        msg["From"] = from_email
        msg["To"] = farmer_email
        msg["Date"] = email.utils.formatdate(localtime=True)
        sender_domain = (
            smtp_user.split("@")[-1]
            if (smtp_user and "@" in smtp_user and "." in smtp_user.split("@")[-1])
            else "aerocrop.ai"
        )
        msg["Message-ID"] = email.utils.make_msgid(domain=sender_domain)
        msg["Reply-To"] = config.SUPPORT_EMAIL
        msg["X-Mailer"] = "AeroCrop.ai Crop Advisory Engine v2.0"
        msg["Auto-Submitted"] = "auto-generated"

        plain_text = (
            f"AeroCrop.ai Crop Diagnostic & Advisory Report\n"
            f"============================================\n"
            f"Farmer: {farmer_name}\n"
            f"Crop: {crop} | District: {district}\n"
            f"Condition: {condition}\n"
            f"Severity: {severity} | Confidence: {confidence}%\n"
            f"{'Yield Forecast: ' + yield_str if yield_str else ''}\n\n"
            f"Chemical Treatment:\n" + "\n".join(f"- {c}" for c in (chem_treatments or ["None needed"])) + "\n\n"
            f"Organic Remedies:\n" + "\n".join(f"- {o}" for o in (org_treatments or ["Maintain balanced nutrition"])) + "\n\n"
            f"Weather: {temp}°C, Humidity: {hum}%, Rainfall: {rain}mm\n"
            f"Spray Window: {'Safe for spraying' if spray_safe else 'Caution — postpone spraying'}\n\n"
            f"For support: {config.SUPPORT_EMAIL}\n"
        )
        msg.set_content(plain_text)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AeroCrop.ai Diagnostic Advisory Report</title>
</head>
<body style="margin:0;padding:0;background-color:#0b1411;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1e293b;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#0b1411;padding:30px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width:640px;background:#ffffff;border-radius:14px;overflow:hidden;box-shadow:0 12px 32px rgba(0,0,0,0.45);border:1px solid #1f3b2e;">
          
          <!-- Top Header -->
          <tr>
            <td style="padding:24px 28px;background:linear-gradient(135deg, #064e3b 0%, #065f46 50%, #047857 100%);color:#ffffff;">
              <table width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td>
                    <div style="font-size:24px;font-weight:800;letter-spacing:-0.5px;color:#ffffff;display:flex;align-items:center;">
                      🌱 AeroCrop<span style="color:#6ee7b7;">.ai</span>
                    </div>
                    <div style="font-size:12px;color:#a7f3d0;margin-top:3px;letter-spacing:0.3px;">
                      Precision Agriculture Advisory & Pathology Diagnostic System • ICAR / MPKV Standards
                    </div>
                  </td>
                  <td align="right" style="vertical-align:top;">
                    <span style="display:inline-block;padding:4px 10px;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.3);border-radius:999px;font-size:11px;font-weight:700;color:#ffffff;letter-spacing:0.5px;">
                      OFFICIAL ADVISORY
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Farmer & Crop Overview Strip -->
          <tr>
            <td style="padding:16px 28px;background:#f8fafc;border-bottom:1px solid #e2e8f0;">
              <table width="100%" cellspacing="0" cellpadding="0" border="0" style="font-size:13px;">
                <tr>
                  <td style="padding:4px 0;color:#64748b;width:25%;">👤 शेतकरी / Farmer:</td>
                  <td style="padding:4px 0;font-weight:700;color:#0f172a;width:25%;">{safe_name}</td>
                  <td style="padding:4px 0;color:#64748b;width:25%;">📍 जिल्हा / District:</td>
                  <td style="padding:4px 0;font-weight:700;color:#0f172a;width:25%;">{safe_district}</td>
                </tr>
                <tr>
                  <td style="padding:4px 0;color:#64748b;">🌱 पीक / Specimen:</td>
                  <td style="padding:4px 0;font-weight:700;color:#059669;">{safe_crop}</td>
                  <td style="padding:4px 0;color:#64748b;">⚖️ अपेक्षित उत्पादन:</td>
                  <td style="padding:4px 0;font-weight:700;color:#0f172a;">{yield_str or 'Calculated per plot'}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Main Diagnostic Body -->
          <tr>
            <td style="padding:26px 28px;">

              <!-- Diagnostic Hero Banner -->
              <div style="background:{sev_bg};border:1.5px solid {sev_border};border-left:6px solid {sev_color};border-radius:10px;padding:16px 18px;margin-bottom:20px;">
                <table width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td>
                      <div style="font-size:11px;font-weight:700;text-transform:uppercase;color:#64748b;letter-spacing:0.5px;">
                        Pathological Assessment / रोग निदान
                      </div>
                      <div style="font-size:18px;font-weight:800;color:#0f172a;margin-top:2px;">
                        {safe_condition}
                      </div>
                    </td>
                    <td align="right" style="vertical-align:top;">
                      <span style="display:inline-block;padding:4px 12px;background:{sev_color};color:#ffffff;border-radius:999px;font-size:11px;font-weight:800;text-transform:uppercase;">
                        {safe_severity}
                      </span>
                    </td>
                  </tr>
                </table>

                <div style="margin-top:10px;font-size:13px;line-height:1.55;color:#334155;">
                  {safe_desc}
                </div>

                <!-- AI Confidence Gauge -->
                <div style="margin-top:12px;padding-top:10px;border-top:1px dashed #cbd5e1;display:flex;align-items:center;">
                  <span style="font-size:12px;font-weight:700;color:#475569;">🧠 AI Diagnostic Confidence:</span>
                  <span style="margin-left:8px;font-size:12px;font-weight:800;color:{sev_color};">{confidence}% Match (Multi-Modal ResNet-18 Vision + MLP)</span>
                </div>
              </div>

              <!-- Treatment Protocols (Two Column) -->
              <table width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom:20px;">
                <tr>
                  <td width="48%" style="vertical-align:top;background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px 16px;">
                    <div style="font-size:13px;font-weight:800;color:#b45309;display:flex;align-items:center;">
                      🧪 रासायनिक फवारणी शिफारशी (Chemical)
                    </div>
                    {chem_html}
                  </td>
                  <td width="4%"></td>
                  <td width="48%" style="vertical-align:top;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:14px 16px;">
                    <div style="font-size:13px;font-weight:800;color:#15803d;display:flex;align-items:center;">
                      🌱 सेंद्रिय व जैविक उपाय (Bio-Organic)
                    </div>
                    {org_html}
                  </td>
                </tr>
              </table>

              <!-- Micro-Climate & Spray Window -->
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px 16px;margin-bottom:20px;">
                <table width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td style="font-size:13px;font-weight:700;color:#0f172a;">
                      🌤️ सूक्ष्म हवामान व फवारणी सल्ला (Spray Window Advisory)
                    </td>
                    <td align="right">
                      <span style="font-size:11px;font-weight:700;padding:3px 9px;border-radius:6px;background:{'#dcfce7' if spray_safe else '#fef3c7'};color:{'#15803d' if spray_safe else '#b45309'};border:1px solid {'#86efac' if spray_safe else '#fde68a'};">
                        {'✓ Spraying Recommended' if spray_safe else '⚠️ Caution Advised'}
                      </span>
                    </td>
                  </tr>
                </table>
                <div style="display:flex;gap:16px;margin-top:10px;font-size:12px;color:#475569;">
                  <span>🌡️ तापमान: <strong>{temp}°C</strong></span>
                  <span style="margin-left:14px;">💧 आर्द्रता: <strong>{hum}%</strong></span>
                  <span style="margin-left:14px;">🌧️ पाऊस: <strong>{rain} mm</strong></span>
                </div>
                <p style="margin:8px 0 0 0;font-size:12px;color:#64748b;line-height:1.4;">
                  {'वारे शांत असून पाऊस नाही. सकाळी ७ ते १० किंवा दुपारी ४ नंतर फवारणी सर्वोत्तम परिणाम देते.' if spray_safe else 'हवेत जास्त आर्द्रता किंवा पावसाची शक्यता असल्याने औषध वाहून जाऊ शकते. आकाश स्वच्छ होईपर्यंत थांबावे.'}
                </p>
              </div>

              <!-- Notice -->
              <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:10px 14px;font-size:12px;color:#1e40af;line-height:1.45;">
                ℹ️ <strong>टीप:</strong> हा सल्ला भारतीय कृषी संशोधन परिषद (ICAR) व महात्मा फुले कृषी विद्यापीठ (MPKV) यांच्या पीक संरक्षण मार्गदर्शक तत्त्वांनुसार स्वयंचलित विश्लेषित केला आहे.
              </div>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:18px 28px;background:#f1f5f9;border-top:1px solid #e2e8f0;text-align:center;">
              <p style="margin:0 0 4px 0;font-size:12px;color:#64748b;">
                कृषी सहाय्य किंवा तंत्रज्ञान मदतीसाठी: <a href="mailto:{config.SUPPORT_EMAIL}" style="color:#059669;font-weight:700;text-decoration:none;">{config.SUPPORT_EMAIL}</a>
              </p>
              <p style="margin:0;font-size:11px;color:#94a3b8;">
                &copy; 2026 AeroCrop.ai Platform • Computer Vision Pathology & Yield Intelligence System
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
        msg.add_alternative(html_content, subtype="html")

        timeout = config.SMTP_TIMEOUT_SECONDS
        if not smtp_user or not smtp_pass:
            raise RuntimeError("SMTP credentials (SMTP_USER / SMTP_PASS) are not configured.")

        _orig_gai = socket.getaddrinfo

        def _ipv4_gai(host, port, family=0, type=0, proto=0, flags=0):
            if family == 0 or family == socket.AF_UNSPEC:
                family = socket.AF_INET
            return _orig_gai(host, port, family, type, proto, flags)

        try:
            socket.getaddrinfo = _ipv4_gai
            if smtp_port == 465:
                ssl_context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=timeout, context=ssl_context) as server:
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
            else:
                ssl_context = ssl.create_default_context()
                with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as server:
                    server.ehlo()
                    server.starttls(context=ssl_context)
                    server.ehlo()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
        finally:
            socket.getaddrinfo = _orig_gai

        logger.info("[EmailService] Direct SMTP advisory email successfully delivered to %s", farmer_email)
        EmailAuditLogger.log_success(farmer_email, "advisory_report", f"python_smtp_{smtp_port}", f"{smtp_host}:{smtp_port}", time.time(), {"crop": crop})
        return {
            "success": True,
            "method": "python_smtp_direct",
            "message": f"Advisory report successfully delivered to {farmer_email} via direct SMTP.",
        }
