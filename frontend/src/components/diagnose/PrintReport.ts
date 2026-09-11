import { PredictionResult, User } from '../../types';

export function printAdvisoryReport(
  result: PredictionResult,
  user: User | null,
  isPmfbyReport: boolean = false
): void {
  const { disease, fertilizer: fert, crop, district, yield_t_ha, weather, mock_mode, image_url } = result;
  const now = new Date().toLocaleString('en-IN');
  const farmerName = user ? user.full_name : 'Registered Farmer';
  const farmerPhone = user?.phone_number || 'N/A';
  const farmerVillage = user?.taluka_village || 'N/A';

  const title = isPmfbyReport
    ? '🇮🇳 PMFBY Crop Damage Assessment & Loss Verification Report'
    : '🌿 AeroCrop.ai — Crop Advisory & Agronomic Prescription';

  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${title}</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 28px; color: #111; max-width: 800px; margin: 0 auto; line-height: 1.5; }
    .header-bar { border-bottom: 3px solid #16a34a; padding-bottom: 10px; margin-bottom: 16px; }
    h1 { color: #15803d; margin: 0 0 4px 0; font-size: 1.5rem; }
    h2 { color: #0e7490; margin-top: 20px; font-size: 1.1rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
    .meta-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px 16px; margin-bottom: 16px; }
    .row { display: flex; gap: 24px; margin-bottom: 8px; }
    .cell { flex: 1; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 0.88rem; }
    th, td { border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; }
    th { background: #f0fdf4; color: #15803d; font-weight: 600; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 0.75rem; font-weight: 700; background: #fef9c3; color: #854d0e; }
    .badge-danger { background: #fee2e2; color: #991b1b; }
    .footer { margin-top: 32px; font-size: 0.78rem; color: #64748b; border-top: 1px solid #cbd5e1; padding-top: 10px; }
    .sign-row { display: flex; justify-content: space-between; margin-top: 48px; padding-top: 12px; }
    .sign-box { border-top: 1px dashed #64748b; width: 220px; text-align: center; font-size: 0.82rem; color: #334155; padding-top: 6px; }
    ul { padding-left: 18px; margin: 4px 0; }
    li { margin-bottom: 3px; font-size: 0.88rem; }
    @media print { body { padding: 12px; } }
  </style>
</head>
<body>
  <div class="header-bar">
    <h1>${title}</h1>
    <p style="margin:0;font-size:0.85rem;color:#475569;">
      Platform: AeroCrop.ai Precision Agriculture &bull; Timestamp: ${now} &bull; Ref: AC-${Date.now().toString().slice(-8)}
    </p>
  </div>

  <div class="meta-box">
    <div class="row">
      <div class="cell"><strong>Farmer Name:</strong> ${farmerName}</div>
      <div class="cell"><strong>Contact:</strong> ${farmerPhone}</div>
      <div class="cell"><strong>Taluka / Village:</strong> ${farmerVillage}</div>
    </div>
    <div class="row" style="margin-bottom:0">
      <div class="cell"><strong>District:</strong> ${district.toUpperCase()}</div>
      <div class="cell"><strong>Cultivated Crop:</strong> ${crop.toUpperCase()}</div>
      <div class="cell"><strong>Diagnostic Engine:</strong> ${mock_mode ? 'Smart Mock Agronomics' : 'Multi-Modal ResNet-18 (90.82%)'}</div>
    </div>
    ${image_url ? `<div style="margin-top:8px"><img src="${image_url}" style="max-height:140px;border-radius:4px;border:1px solid #cbd5e1" alt="Specimen" /></div>` : ''}
  </div>

  <h2>🦠 Pathology &amp; Disease Severity Assessment</h2>
  <table>
    <tr><th style="width:30%">Diagnosed Condition</th><td><strong>${disease.name}</strong></td></tr>
    <tr><th>AI Confidence Level</th><td>${disease.confidence.toFixed(1)}%</td></tr>
    <tr><th>Severity Rating</th><td><span class="badge ${disease.severity === 'Critical' || disease.severity === 'High' ? 'badge-danger' : ''}">${disease.severity}</span></td></tr>
    <tr><th>Pathological Description</th><td>${disease.description}</td></tr>
    <tr><th>Expected Harvest Yield</th><td><strong>${yield_t_ha} t/ha</strong> (${(yield_t_ha * 4.047).toFixed(1)} quintals/acre)</td></tr>
  </table>

  <h2>💊 Agronomic Prescription &amp; Containment Protocol</h2>
  <div class="row">
    <div class="cell">
      <strong>Recommended Chemical Spray:</strong>
      <ul>${(disease.chemical_treatment.length ? disease.chemical_treatment : ['Standard monitoring only.']).map(t => `<li>${t}</li>`).join('')}</ul>
    </div>
    <div class="cell">
      <strong>Biological / Organic Remedy:</strong>
      <ul>${(disease.organic_treatment.length ? disease.organic_treatment : ['None required.']).map(t => `<li>${t}</li>`).join('')}</ul>
    </div>
  </div>

  <h2>🧬 Soil Nutrient &amp; Commercial Fertilizer Allocation</h2>
  <table>
    <tr><th>Fertilizer</th><th>Deficit Dose (kg/ha)</th><th>Standard 50kg Bags / ha</th><th>Subsidized Approx Cost</th></tr>
    <tr><td>Urea (46% N)</td><td>${fert.fertilizers.Urea} kg</td><td>${Math.ceil(fert.fertilizers.Urea / 50)} bags</td><td>₹${Math.ceil(fert.fertilizers.Urea / 50) * 267}</td></tr>
    <tr><td>DAP (18% N, 46% P)</td><td>${fert.fertilizers.DAP} kg</td><td>${Math.ceil(fert.fertilizers.DAP / 50)} bags</td><td>₹${Math.ceil(fert.fertilizers.DAP / 50) * 1350}</td></tr>
    <tr><td>MOP (60% K)</td><td>${fert.fertilizers.MOP} kg</td><td>${Math.ceil(fert.fertilizers.MOP / 50)} bags</td><td>₹${Math.ceil(fert.fertilizers.MOP / 50) * 1700}</td></tr>
  </table>

  <h2>🌡️ Microclimate Telemetry</h2>
  <table>
    <tr>
      <th>Ambient Temperature</th><td>${weather.temperature}°C</td>
      <th>Relative Humidity</th><td>${weather.humidity}%</td>
    </tr>
    <tr>
      <th>Recorded Rainfall</th><td>${weather.rainfall} mm</td>
      <th>Telemetry Station</th><td>Open-Meteo Grid (${district})</td>
    </tr>
  </table>

  ${isPmfbyReport ? `
  <div class="sign-row">
    <div class="sign-box">Signature of Insured Farmer</div>
    <div class="sign-box">Talathi / Village Agri Officer</div>
    <div class="sign-box">Insurance Surveyor (PMFBY)</div>
  </div>
  ` : ''}

  <div class="footer">
    Verified report generated under ICAR nutrient guidelines and computer vision leaf pathology inference.<br>
    Govt of India NBS fertilizer pricing benchmarks applied. For certified claims, submit to nearest Krishi Seva Kendra / KVK office.<br>
    Agronomic &amp; Platform Support: <a href="mailto:support@devanshupatil.tech" style="color: #15803d; text-decoration: none; font-weight: 600;">support@devanshupatil.tech</a>
  </div>
</body>
</html>`;

  const win = window.open('', '_blank');
  if (win) {
    win.document.write(html);
    win.document.close();
    win.focus();
    setTimeout(() => {
      win.print();
    }, 250);
  }
}
