const PDFDocument = require('pdfkit');
const fs = require('fs');
const path = require('path');
const { getCropNames, getLocalizedPathology } = require('./reportGenerator');

function generateNativePDF(data) {
    return new Promise((resolve, reject) => {
        try {
            const {
                farmerName = 'राजेश बाबुराव पाटील / Rajesh B. Patil',
                farmerPhone = '',
                farmerVillage = 'पुणे',
                district = 'Pune',
                crop = 'Tomato',
                disease = {},
                fertilizer = {},
                yield_t_ha = 28.5,
                weather = {},
            } = data;

            const doc = new PDFDocument({
                size: 'A4',
                margin: 32,
                autoFirstPage: false,
                info: {
                    Title: `AeroCrop Trilingual Advisory — ${crop}`,
                    Author: 'AeroCrop.ai Agricultural Intelligence',
                    Subject: 'Foliar Pathology Diagnosis & Trilingual Treatment Plan',
                }
            });

            const fontPath = path.join(__dirname, 'fonts', 'NotoSansDevanagari.ttf');
            const hasDeva = fs.existsSync(fontPath);
            if (hasDeva) {
                doc.registerFont('DevaFont', fontPath);
            }

            const setHeading = (size = 13) => {
                if (hasDeva) doc.font('DevaFont');
                else doc.font('Helvetica-Bold');
                doc.fontSize(size);
            };

            const setBody = (size = 8.5) => {
                if (hasDeva) doc.font('DevaFont');
                else doc.font('Helvetica');
                doc.fontSize(size);
            };

            const buffers = [];
            doc.on('data', buffers.push.bind(buffers));
            doc.on('end', () => resolve(Buffer.concat(buffers)));

            const cropObj = getCropNames(crop);
            const localized = getLocalizedPathology(disease, cropObj);
            const dateStr = new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
            const refId = 'AC-' + Date.now().toString().slice(-8);

            const ferts = fertilizer?.fertilizers || {};
            const ureaKg = ferts.Urea || 100;
            const dapKg = ferts.DAP || 50;
            const mopKg = ferts.MOP || 40;
            const ureaBags = Math.ceil(ureaKg / 50);
            const dapBags = Math.ceil(dapKg / 50);
            const mopBags = Math.ceil(mopKg / 50);
            const totalFertCost = (ureaBags * 267) + (dapBags * 1350) + (mopBags * 1700);

            const temp = weather?.temperature || 28.0;
            const hum = weather?.humidity || 65.0;
            const rain = weather?.rainfall || 0.0;
            const spraySafe = weather?.spray_window ? weather.spray_window.safe : (hum < 80 && rain === 0);

            const confidenceVal = disease.confidence ? parseFloat(disease.confidence) : 95.4;
            const isHealthy = disease.is_healthy === true;

            const languages = [
                {
                    lang: 'mr',
                    pageTitle: 'विभाग १ : मराठी अहवाल (Comprehensive Marathi Advisory)',
                    subtitle: 'अचूक शेती आणि बहु-माध्यमी पीक आरोग्य निदान • ICAR व MPKV मानके',
                    farmerLabel: 'शेतकऱ्याचे नाव',
                    villageLabel: 'गाव व जिल्हा',
                    cropLabel: 'तपासलेले पीक',
                    yieldLabel: 'अपेक्षित उत्पादन',
                    diagHead: 'रोग निदान व सद्यस्थिती (Pathological Findings)',
                    statusLabel: 'सद्यस्थिती',
                    confLabel: 'AI विश्वासार्हता',
                    pathogenLabel: 'रोगकारक घटक',
                    chemHead: 'रासायनिक फवारणी शिफारशी (Chemical Treatment)',
                    orgHead: 'सेंद्रिय व जैविक पर्याय (Bio-Organic Remedies)',
                    fertHead: 'संतुलित खत व्यवस्थापन (ICAR Balanced Fertilizer Dosage)',
                    weatherHead: 'हवामान व फवारणी सल्ला (Spray Window Advisory)',
                    pageFoot: 'पृष्ठ १ / ३ (मराठी अहवाल)',
                    safeSprayText: 'फवारणीसाठी अनुकूल हवामान — सकाळी ७ ते १० किंवा संध्याकाळी ४ नंतर फवारणी करावी.',
                    cautionSprayText: 'सावधगिरी — हवेत जास्त ओलावा किंवा पावसाची शक्यता असल्याने फवारणी लांबणीवर टाकावी.',
                    sig1: 'शेतकऱ्याची सही / अंगठा',
                    sig2: 'ग्राम कृषी सहाय्यक / तलाठी',
                    sig3: 'कृषी विज्ञान केंद्र (KVK) शास्त्रज्ञ शिक्का',
                    t_data: localized.mr,
                    fertHeaders: ['खताचा प्रकार', 'डोस (हेक्टरी)', '५० किलो पोती', 'अंदाजित खर्च'],
                },
                {
                    lang: 'hi',
                    pageTitle: 'खंड २ : हिंदी रिपोर्ट (Comprehensive Hindi Advisory)',
                    subtitle: 'सटीक कृषि एवं बहु-आयामी फसल स्वास्थ्य निदान • ICAR मानक सिफारिशें',
                    farmerLabel: 'किसान का नाम',
                    villageLabel: 'गाँव एवं ज़िला',
                    cropLabel: 'निरीक्षित फसल',
                    yieldLabel: 'अनुमानित उपज',
                    diagHead: 'रोग निदान एवं स्थिति (Diagnostic Assessment)',
                    statusLabel: 'रोग स्थिति',
                    confLabel: 'AI विश्वसनीयता',
                    pathogenLabel: 'रोगजनक घटक',
                    chemHead: 'रासायनिक छिड़काव सिफारिशें (Chemical Treatment)',
                    orgHead: 'जैविक एवं प्राकृतिक विकल्प (Bio-Organic Alternatives)',
                    fertHead: 'संतुलित उर्वरक प्रबंधन (ICAR Balanced Nutrient Dosage)',
                    weatherHead: 'मौसम एवं छिड़काव परामर्श (Weather & Spray Window)',
                    pageFoot: 'पृष्ठ २ / ३ (हिंदी रिपोर्ट)',
                    safeSprayText: 'छिड़काव हेतु अनुकूल मौसम — शांत हवा, सुबह ७ से १० अथवा शाम को छिड़काव करें।',
                    cautionSprayText: 'सावधानी — नमी अधिक अथवा वर्षा की संभावना, छिड़काव कुछ समय के लिए स्थगित रखें।',
                    sig1: 'किसान के हस्ताक्षर / अंगूठा',
                    sig2: 'ग्राम कृषि अधिकारी / पटवारी',
                    sig3: 'कृषि विज्ञान केंद्र (KVK) विशेषज्ञ मुहर',
                    t_data: localized.hi,
                    fertHeaders: ['उर्वरक का नाम', 'मात्रा (हेक्टेयर)', '५० कि.ग्रा. बैग', 'अनुमानित लागत'],
                },
                {
                    lang: 'en',
                    pageTitle: 'Section 3 : English Scientific & Agronomic Advisory',
                    subtitle: 'Precision Multi-Modal Agricultural Intelligence & Pathology Advisory',
                    farmerLabel: 'Farmer Name',
                    villageLabel: 'Location & District',
                    cropLabel: 'Inspected Crop',
                    yieldLabel: 'Yield Forecast',
                    diagHead: 'Pathological Diagnostic Findings',
                    statusLabel: 'Diagnostic Status',
                    confLabel: 'Vision Confidence',
                    pathogenLabel: 'Causal Organism',
                    chemHead: 'Chemical Formulations & Tank-Mix Protocols',
                    orgHead: 'Bio-Organic & Integrated Pest Management (IPM)',
                    fertHead: 'Balanced Macronutrient Management (ICAR / MPKV Standards)',
                    weatherHead: 'Micrometeorology & Spray Window Optimization',
                    pageFoot: 'Page 3 / 3 (English Report)',
                    safeSprayText: 'OPTIMAL SPRAY WINDOW — Favorable ambient conditions. Recommend early morning (7–10 AM) foliar spray.',
                    cautionSprayText: 'CAUTION / POSTPONE — Elevated humidity or precipitation probability. Chemical wash-off risk high.',
                    sig1: 'Signature of Cultivator',
                    sig2: 'Village Agriculture Officer / Talathi',
                    sig3: 'KVK Agronomist / PMFBY Surveyor Seal',
                    t_data: localized.en,
                    fertHeaders: ['Fertilizer Type', 'Dosage (kg/ha)', '50kg Bags', 'Estimated Cost'],
                }
            ];

            languages.forEach((cfg) => {
                doc.addPage({ size: 'A4', margin: 32 });
                const pw = doc.page.width;
                const cw = pw - 64; // 32 on each side

                // ── Top Brand Banner ───────────────────────────────────────────
                doc.rect(0, 0, pw, 72).fill('#15803d');
                doc.fillColor('#ffffff');
                setHeading(18);
                doc.text('AeroCrop.ai', 32, 14);
                setBody(9);
                doc.text(cfg.subtitle, 32, 38);
                doc.fontSize(7.5).text(`Ref ID: ${refId}  |  Date: ${dateStr}  |  ${cfg.pageTitle}`, 32, 53);

                let y = 82;

                // ── Telemetry Grid ─────────────────────────────────────────────
                doc.rect(32, y, cw, 50).fillAndStroke('#f8fafc', '#cbd5e1');
                doc.fillColor('#0f172a');
                setHeading(9);
                doc.text(`${cfg.farmerLabel}: ${farmerName}`, 42, y + 8);
                setBody(8);
                doc.fillColor('#475569');
                const loc = [farmerVillage, district].filter(Boolean).join(', ') || district;
                doc.text(`${cfg.villageLabel}: ${loc}  |  Phone: ${farmerPhone || '+91 98220 12345'}`, 42, y + 22);
                const yieldStr = yield_t_ha ? `${yield_t_ha} t/ha (~${(yield_t_ha*4.047).toFixed(1)} q/acre)` : 'Standard';
                doc.text(`${cfg.cropLabel}: ${cropObj[cfg.lang] || crop}  |  ${cfg.yieldLabel}: ${yieldStr}`, 42, y + 34);

                y += 58;

                // ── Section 1: Diagnostic Finding ──────────────────────────────
                const tData = cfg.t_data;
                const statusColor = isHealthy ? '#15803d' : '#b91c1c';
                const statusBg = isHealthy ? '#f0fdf4' : '#fef2f2';

                doc.rect(32, y, cw, 68).fillAndStroke(statusBg, statusColor);
                doc.fillColor(statusColor);
                setHeading(11);
                doc.text(tData.condition || `${crop} Diagnosis`, 42, y + 8);

                setBody(8);
                doc.fillColor('#334155');
                doc.text(`${cfg.statusLabel}: ${tData.status}   |   ${cfg.confLabel}: ${confidenceVal}%   |   ${cfg.pathogenLabel}: ${tData.pathogen}`, 42, y + 24);
                
                const descText = (tData.description || '').slice(0, 240);
                doc.text(descText, 42, y + 37, { width: cw - 20, lineGap: 1.5 });

                y += 76;

                // ── Section 2: Chemical & Organic Treatments (2-Column) ─────────
                setHeading(10);
                doc.fillColor('#15803d').text(cfg.chemHead, 32, y);
                doc.text(cfg.orgHead, 32 + (cw / 2) + 6, y);
                y += 16;

                const colW = (cw / 2) - 6;

                // Chemical Column Box
                doc.rect(32, y, colW, 94).fillAndStroke('#ffffff', '#cbd5e1');
                setBody(7.8);
                doc.fillColor('#1e293b');
                let cy = y + 8;
                (tData.chem || []).slice(0, 3).forEach((item, idx) => {
                    doc.text(`${idx + 1}. ${item}`, 40, cy, { width: colW - 16, lineGap: 1 });
                    cy += 24;
                });
                if (tData.phi) {
                    doc.fillColor('#b91c1c').text(`* ${tData.phi}`, 40, y + 80, { width: colW - 16 });
                }

                // Organic Column Box
                const col2X = 32 + (cw / 2) + 6;
                doc.rect(col2X, y, colW, 94).fillAndStroke('#ffffff', '#cbd5e1');
                setBody(7.8);
                doc.fillColor('#15803d');
                let oy = y + 8;
                (tData.org || []).slice(0, 3).forEach((item, idx) => {
                    doc.text(`${idx + 1}. ${item}`, col2X + 8, oy, { width: colW - 16, lineGap: 1 });
                    oy += 24;
                });
                if (tData.cultural && tData.cultural[0]) {
                    doc.fillColor('#475569').text(`* ${tData.cultural[0]}`, col2X + 8, y + 80, { width: colW - 16 });
                }

                y += 102;

                // ── Section 3: ICAR Fertilizer Dosage Table ────────────────────
                setHeading(10);
                doc.fillColor('#15803d').text(cfg.fertHead, 32, y);
                y += 16;

                doc.rect(32, y, cw, 50).fillAndStroke('#f8fafc', '#cbd5e1');
                doc.fillColor('#0f172a');
                setHeading(8.5);
                const h = cfg.fertHeaders;
                doc.text(h[0], 42, y + 6);
                doc.text(h[1], 175, y + 6);
                doc.text(h[2], 295, y + 6);
                doc.text(h[3], 420, y + 6);

                doc.moveTo(32, y + 18).lineTo(pw - 32, y + 18).stroke('#e2e8f0');

                setBody(8);
                doc.fillColor('#334155');
                doc.text('Urea (युरिया / यूरिया 46% N)', 42, y + 22);
                doc.text(`${ureaKg} kg/ha`, 175, y + 22);
                doc.text(`${ureaBags} bags`, 295, y + 22);
                doc.text(`Rs. ${ureaBags * 267}`, 420, y + 22);

                doc.text('DAP (डीएपी 18:46:0)', 42, y + 34);
                doc.text(`${dapKg} kg/ha`, 175, y + 34);
                doc.text(`${dapBags} bags`, 295, y + 34);
                doc.text(`Rs. ${dapBags * 1350}`, 420, y + 34);

                y += 58;

                // ── Section 4: Weather & Spray Advisory ────────────────────────
                setHeading(10);
                doc.fillColor('#15803d').text(cfg.weatherHead, 32, y);
                y += 16;

                const sprayBg = spraySafe ? '#f0fdf4' : '#fffbeb';
                const sprayBorder = spraySafe ? '#16a34a' : '#d97706';
                doc.rect(32, y, cw, 46).fillAndStroke(sprayBg, sprayBorder);
                doc.fillColor(spraySafe ? '#166534' : '#b45309');
                setHeading(9);
                doc.text(`Telemetry: ${temp} deg C  |  Humidity: ${hum}%  |  Rainfall: ${rain} mm`, 42, y + 8);
                setBody(8);
                doc.text(spraySafe ? cfg.safeSprayText : cfg.cautionSprayText, 42, y + 23, { width: cw - 20 });

                y += 56;

                // ── Signatures Section ─────────────────────────────────────────
                const boxW = (cw / 3) - 8;
                doc.rect(32, y, boxW, 40).fillAndStroke('#ffffff', '#cbd5e1');
                setBody(7);
                doc.fillColor('#64748b').text(cfg.sig1, 36, y + 14, { align: 'center', width: boxW - 8 });

                doc.rect(32 + boxW + 12, y, boxW, 40).fillAndStroke('#ffffff', '#cbd5e1');
                doc.text(cfg.sig2, 32 + boxW + 16, y + 14, { align: 'center', width: boxW - 8 });

                doc.rect(32 + (boxW * 2) + 24, y, boxW, 40).fillAndStroke('#ffffff', '#cbd5e1');
                doc.text(cfg.sig3, 32 + (boxW * 2) + 28, y + 14, { align: 'center', width: boxW - 8 });

                // Footer
                doc.fillColor('#94a3b8').fontSize(7).text(
                    `AeroCrop.ai • ICAR & MPKV Norms  |  Contact: support@devanshupatil.tech  |  ${cfg.pageFoot}`,
                    32,
                    doc.page.height - 24,
                    { align: 'center', width: cw }
                );
            });

            doc.end();
        } catch (err) {
            reject(err);
        }
    });
}

module.exports = { generateNativePDF };
