const express = require('express');
const nodemailer = require('nodemailer');
const cors = require('cors');
require('dotenv').config();

const { generateTrilingualPDF } = require('./reportGenerator');

const app = express();
app.use(cors());
app.use(express.json({ limit: '15mb' }));

const SENDER_EMAIL = process.env.FROM;
const SENDER_PASS  = process.env.PASS;
const PORT         = process.env.PORT || 5000;

if (!SENDER_EMAIL || !SENDER_PASS) {
    console.warn('⚠️  FROM or PASS not set in .env — email sending will fail.');
}

// ── Nodemailer Transporter (Singleton) ──────────────────────────────────────
const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: { user: SENDER_EMAIL, pass: SENDER_PASS },
});

transporter.verify((err) => {
    if (err) {
        console.error('❌ SMTP Connection Error:', err.message);
        console.warn('💡 Tip: Ensure 2-Step Verification is ON and use a 16-character App Password.');
    } else {
        console.log(`✅ SMTP Server connected successfully as: ${SENDER_EMAIL}`);
    }
});

// ── Health Check ────────────────────────────────────────────────────────────
app.get('/health', (_req, res) => {
    res.json({
        status: 'ok',
        service: 'AeroCrop.ai Trilingual Email Microservice v3',
        smtp: SENDER_EMAIL ? SENDER_EMAIL.replace(/(.{3})(.*)(@.*)/, '$1***$3') : 'Not Configured',
        capabilities: ['Marathi', 'English', 'Hindi', 'PDF-Rendering-Chromium-Engine'],
    });
});

function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ── POST /send-email ─────────────────────────────────────────────────────────
app.post('/send-email', async (req, res) => {
    try {
        const {
            email,
            name          = 'शेतकरी / Farmer',
            farmerPhone   = '',
            farmerVillage = '',
            crop          = 'Crop',
            district      = '',
            disease       = {},
            fertilizer    = {},
            yield_t_ha,
            weather       = {},
            pdfBase64,
        } = req.body;

        if (!email) {
            return res.status(400).json({ success: false, error: "Missing required field: 'email'." });
        }
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            return res.status(400).json({ success: false, error: `Invalid email address format: ${email}` });
        }

        if (!process.env.FROM || !process.env.PASS) {
            return res.status(500).json({
                success: false,
                error: 'SMTP credentials (FROM and PASS) are not configured in .env.',
            });
        }

        // 1. Generate High-Fidelity Trilingual PDF
        let pdfBuffer;
        if (pdfBase64) {
            pdfBuffer = Buffer.from(pdfBase64.replace(/^data:application\/pdf;base64,/, ''), 'base64');
        } else {
            console.log(`📄 Generating Trilingual PDF Advisory for ${name} (${crop}, ${district})...`);
            pdfBuffer = await generateTrilingualPDF({
                farmerName: name,
                farmerPhone,
                farmerVillage,
                district,
                crop,
                disease,
                fertilizer,
                yield_t_ha,
                weather,
            });
            console.log(`✅ PDF generated successfully (${pdfBuffer.length} bytes)`);
        }

        const conditionName = disease?.name || 'Diagnostic Completed';
        const severity      = disease?.severity || 'Normal';
        const confidence    = disease?.confidence != null ? `${disease.confidence}%` : 'N/A';

        // Sanitize values for HTML rendering
        const safeName      = escapeHtml(name);
        const safeCrop      = escapeHtml(crop);
        const safeDistrict  = escapeHtml(district);
        const safeCondition = escapeHtml(conditionName);
        const safeSeverity  = escapeHtml(severity);
        const safeConfidence= escapeHtml(confidence);

        // 2. Compose High-Quality Email Body
        const mailOptions = {
            from: `"AeroCrop.ai Advisory" <${process.env.FROM}>`,
            to: email,
            subject: `🌾 पीक सल्ला व रोग निदान अहवाल | Crop Advisory Report — ${crop} (${conditionName})`,
            text: `Namaste ${name},\n\nYour crop diagnostic report for ${crop} (${district}) is attached.\n\nCondition: ${conditionName}\nConfidence: ${confidence}\nSeverity: ${severity}\n\nThe PDF contains complete details in 3 comprehensive sections:\n1. Marathi (मराठी अहवाल)\n2. English (English Report)\n3. Hindi (हिंदी रिपोर्ट)\n\nRegards,\nAeroCrop.ai Team`,
            html: `
<div style="font-family:'Segoe UI',Arial,sans-serif;color:#0f172a;max-width:620px;margin:auto;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.05)">
  <div style="background:linear-gradient(135deg, #15803d, #16a34a);color:#ffffff;padding:22px 28px">
    <h2 style="margin:0;font-size:22px;font-weight:800;letter-spacing:-0.5px">🌿 AeroCrop.ai</h2>
    <p style="margin:4px 0 0;font-size:13px;opacity:0.95">अचूक शेती आणि बहु-माध्यमी पीक आरोग्य निदान • Precision Agriculture Advisory</p>
  </div>
  <div style="padding:24px 28px;background:#ffffff">
    <p style="font-size:15px;margin-top:0">नमस्कार / Greetings <strong>${safeName}</strong>,</p>
    <p style="font-size:13.5px;color:#334155;line-height:1.5">
      तुमच्या <strong>${safeCrop}</strong> पिकाचे (जिल्हा: <strong>${safeDistrict}</strong>) सविस्तर निदान पूर्ण झाले आहे. खालील तक्त्यात मुख्य निष्कर्ष दिले आहेत:
    </p>
    
    <table style="width:100%;border-collapse:collapse;font-size:13px;margin:16px 0;border-radius:8px;overflow:hidden;border:1px solid #e2e8f0">
      <tr style="background:#f8fafc">
        <td style="padding:10px 14px;font-weight:700;color:#64748b;width:40%;border-bottom:1px solid #e2e8f0">आढळलेला रोग / Condition</td>
        <td style="padding:10px 14px;color:#15803d;font-weight:700;border-bottom:1px solid #e2e8f0">${safeCondition}</td>
      </tr>
      <tr>
        <td style="padding:10px 14px;font-weight:700;color:#64748b;border-bottom:1px solid #e2e8f0">AI विश्वासार्हता / Confidence</td>
        <td style="padding:10px 14px;font-weight:700;border-bottom:1px solid #e2e8f0">${safeConfidence}</td>
      </tr>
      <tr style="background:#f8fafc">
        <td style="padding:10px 14px;font-weight:700;color:#64748b;border-bottom:1px solid #e2e8f0">रोगाची तीव्रता / Severity</td>
        <td style="padding:10px 14px;font-weight:700;border-bottom:1px solid #e2e8f0">${safeSeverity}</td>
      </tr>
      ${yield_t_ha ? `
      <tr>
        <td style="padding:10px 14px;font-weight:700;color:#64748b">अपेक्षित उत्पादन / Yield</td>
        <td style="padding:10px 14px;font-weight:700">${yield_t_ha} टन/हे (~${(yield_t_ha*4.047).toFixed(1)} क्विंटल/एकर)</td>
      </tr>` : ''}
    </table>

    <div style="background:#f0fdf4;border-left:5px solid #16a34a;padding:14px 16px;border-radius:6px;margin:18px 0">
      <p style="margin:0;font-size:13px;color:#166534;font-weight:600">
        📎 संपूर्ण सविस्तर अहवाल PDF स्वरूपात सोबत जोडला आहे:
      </p>
      <ul style="margin:6px 0 0 18px;padding:0;font-size:12px;color:#14532d">
        <li><strong>विभाग १ : मराठी अहवाल</strong> — रासायनिक व सेंद्रिय फवारणी, खतांचे डोस, हवामान व विमा पडताळणी</li>
        <li><strong>Section 2 : English Report</strong> — Comprehensive scientific advisory & dosage calculations</li>
        <li><strong>खंड ३ : हिंदी रिपोर्ट</strong> — पूर्ण उपचार सिफारिशें, संतुलित उर्वरक मात्रा एवं मौसम परामर्श</li>
      </ul>
    </div>

    <p style="font-size:11.5px;color:#64748b;margin-top:24px;border-top:1px solid #f1f5f9;padding-top:12px">
      हा अहवाल ICAR आणि महात्मा फुले कृषी विद्यापीठ (MPKV) मानकांवर आधारित आहे. तांत्रिक व कृषी मदतीसाठी संपर्क: <a href="mailto:support@devanshupatil.tech" style="color:#16a34a;text-decoration:none;font-weight:bold">support@devanshupatil.tech</a>
    </p>
  </div>
</div>`,
            attachments: [{
                filename: `AeroCrop_Advisory_${crop}_${Date.now()}.pdf`,
                content: pdfBuffer,
                contentType: 'application/pdf',
            }],
        };

        const info = await transporter.sendMail(mailOptions);
        console.log(`✉️  Advisory email with PDF report successfully sent to ${email} [${info.messageId}]`);

        return res.status(200).json({
            success: true,
            message: `Trilingual advisory report PDF successfully sent to ${email}`,
            messageId: info.messageId,
        });
    } catch (err) {
        console.error('❌ Email dispatch error:', err);
        return res.status(500).json({ success: false, error: err.message });
    }
});

// ── Start ────────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
    console.log(`🚀 AeroCrop Trilingual Email Microservice v3 running on http://localhost:${PORT}`);
});
