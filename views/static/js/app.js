/**
 * AeroCrop.ai — Frontend Application (View Layer)
 *
 * Responsibilities (MVC View):
 *  - Handle user interactions (image upload, form, navigation)
 *  - Call backend API endpoints
 *  - Render results dynamically (disease, fertilizer, yield, NPK chart)
 *  - Manage Chart.js NPK visualization
 */

'use strict';

/* ── State ──────────────────────────────────────────────────────────────── */
const state = {
  uploadedFile:  null,
  weatherCache:  {},
  npkChart:      null,
  isLoading:     false,
};

/* ── DOM References ─────────────────────────────────────────────────────── */
const $ = id => document.getElementById(id);

const els = {
  analyzeBtn:     $('analyze-btn'),
  uploadZone:     $('upload-zone'),
  uploadPlaceholder: $('upload-placeholder'),
  fileInput:      $('file-input'),
  previewImg:     $('preview-img'),
  cropSelect:     $('crop-select'),
  districtSelect: $('district-select'),
  inputN:         $('input-N'),
  inputP:         $('input-P'),
  inputK:         $('input-K'),
  resultsArea:    $('results-area'),
  mockBanner:     $('mock-banner'),
  btnText:        document.querySelector('#analyze-btn .btn-text'),
  btnSpinner:     document.querySelector('#analyze-btn .btn-spinner'),
  btnIcon:        document.querySelector('#analyze-btn .btn-icon'),
};

/* ══════════════════════════════════════════════════════════════════════════
   NAVIGATION
══════════════════════════════════════════════════════════════════════════ */
function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-item');
  navLinks.forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const target = link.getAttribute('href').replace('#', '');
      switchPage(target);
    });
  });
}

function switchPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const page = document.getElementById(`page-${name}`);
  const nav  = document.getElementById(`nav-${name}`);
  if (page) page.classList.add('active');
  if (nav)  nav.classList.add('active');

  if (name === 'diseases') loadDiseaseDB();
}

/* ══════════════════════════════════════════════════════════════════════════
   DISTRICT & WEATHER
══════════════════════════════════════════════════════════════════════════ */
async function loadDistricts() {
  try {
    const res  = await fetch('/api/weather/districts');
    const data = await res.json();

    const select = els.districtSelect;
    select.innerHTML = '';

    data.districts.forEach(d => {
      const opt = document.createElement('option');
      opt.value       = d;
      opt.textContent = d.charAt(0).toUpperCase() + d.slice(1);
      select.appendChild(opt);
    });

    // Default to Pune
    const pune = Array.from(select.options).find(o => o.value === 'pune');
    if (pune) pune.selected = true;

    await fetchWeather(select.value);

  } catch (err) {
    console.warn('Could not load districts:', err);
    els.districtSelect.innerHTML = '<option value="pune">Pune</option>';
  }
}

async function fetchWeather(district) {
  if (!district) return;

  if (state.weatherCache[district]) {
    renderWeather(state.weatherCache[district]);
    return;
  }

  try {
    const res  = await fetch(`/api/weather/${encodeURIComponent(district)}`);
    const data = await res.json();
    state.weatherCache[district] = data;
    renderWeather(data);
  } catch {
    // Silently fail — UI shows '--' stubs
  }
}

function renderWeather(data) {
  $('val-temp').textContent  = `${data.temperature}°C`;
  $('val-hum').textContent   = `${data.humidity}%`;
  $('val-rain').textContent  = `${data.rainfall} mm`;

  // Animate each weather item
  document.querySelectorAll('.weather-item').forEach(el => {
    el.style.animation = 'none';
    requestAnimationFrame(() => {
      el.style.animation = 'fade-in 0.4s ease forwards';
    });
  });
}

/* ══════════════════════════════════════════════════════════════════════════
   FILE UPLOAD
══════════════════════════════════════════════════════════════════════════ */
function initUpload() {
  // Click to upload
  els.uploadZone.addEventListener('click', () => els.fileInput.click());

  // Keyboard access
  els.uploadZone.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); els.fileInput.click(); }
  });

  // File input change
  els.fileInput.addEventListener('change', e => {
    if (e.target.files[0]) handleFileSelect(e.target.files[0]);
  });

  // Drag events
  els.uploadZone.addEventListener('dragover', e => {
    e.preventDefault();
    els.uploadZone.classList.add('drag-over');
  });
  els.uploadZone.addEventListener('dragleave', () => {
    els.uploadZone.classList.remove('drag-over');
  });
}

window.handleDrop = function(e) {
  e.preventDefault();
  els.uploadZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) handleFileSelect(file);
};

function handleFileSelect(file) {
  if (file.size > 10 * 1024 * 1024) {
    showToast('Image must be under 10 MB.', 'error');
    return;
  }
  state.uploadedFile = file;

  const reader = new FileReader();
  reader.onload = ev => {
    els.previewImg.src = ev.target.result;
    els.previewImg.classList.remove('hidden');
    els.uploadPlaceholder.classList.add('hidden');
  };
  reader.readAsDataURL(file);
}

/* ══════════════════════════════════════════════════════════════════════════
   ANALYSIS — Main Action
══════════════════════════════════════════════════════════════════════════ */
function initAnalyzeButton() {
  els.analyzeBtn.addEventListener('click', runAnalysis);
}

async function runAnalysis() {
  // Validation
  if (!state.uploadedFile) {
    showToast('Please upload a leaf image first.', 'warning');
    return;
  }

  const N = parseFloat(els.inputN.value);
  const P = parseFloat(els.inputP.value);
  const K = parseFloat(els.inputK.value);

  if (isNaN(N) || isNaN(P) || isNaN(K) || N < 0 || P < 0 || K < 0) {
    showToast('Please enter valid soil N, P, K values (≥ 0).', 'warning');
    return;
  }

  setLoading(true);

  const form = new FormData();
  form.append('image',    state.uploadedFile);
  form.append('crop',     els.cropSelect.value);
  form.append('district', els.districtSelect.value);
  form.append('N',        N);
  form.append('P',        P);
  form.append('K',        K);

  try {
    const res  = await fetch('/api/predict', { method: 'POST', body: form });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || 'Prediction failed');

    renderResults(data);
    els.resultsArea.classList.remove('hidden');
    els.resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
    showToast('Analysis complete!', 'success');

  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
    console.error(err);
  } finally {
    setLoading(false);
  }
}

/* ══════════════════════════════════════════════════════════════════════════
   RENDER RESULTS
══════════════════════════════════════════════════════════════════════════ */
function renderResults(data) {
  const { disease, yield_t_ha, fertilizer, mock_mode, weather } = data;

  // Mock mode banner
  if (mock_mode) {
    els.mockBanner.classList.remove('hidden');
  } else {
    els.mockBanner.classList.add('hidden');
  }

  // Weather update (from server-validated data)
  if (weather) renderWeather(weather);

  // ── Metric cards ───────────────────────────────────────────────────────
  $('res-disease-name').textContent   = disease.name;
  $('res-disease-crop').textContent   = `Crop: ${disease.crop}`;
  $('res-confidence').textContent     = `${disease.confidence.toFixed(1)}%`;
  $('res-yield').textContent          = `${yield_t_ha} t/ha`;
  $('res-yield-crop').textContent     = `For ${data.crop}`;

  const sev = disease.severity || 'None';
  $('res-severity').textContent       = sev;
  $('res-healthy-status').textContent = disease.is_healthy ? '✅ Healthy' : '⚠️ Diseased';

  // Confidence bar
  $('confidence-fill').style.width = `${Math.min(disease.confidence, 100)}%`;

  // ── Treatment ──────────────────────────────────────────────────────────
  $('res-disease-desc').textContent = disease.description || 'No description available.';

  const chemList = $('res-chemical');
  const orgList  = $('res-organic');
  chemList.innerHTML = '';
  orgList.innerHTML  = '';

  (disease.chemical_treatment.length > 0
    ? disease.chemical_treatment
    : ['No specific chemical treatment required.']
  ).forEach(t => {
    const li = document.createElement('li');
    li.textContent = t;
    chemList.appendChild(li);
  });

  (disease.organic_treatment.length > 0
    ? disease.organic_treatment
    : ['No specific organic treatment required.']
  ).forEach(t => {
    const li = document.createElement('li');
    li.textContent = t;
    orgList.appendChild(li);
  });

  // ── Fertilizer ─────────────────────────────────────────────────────────
  $('res-fert-interpretation').textContent = fertilizer.interpretation;
  $('val-urea').textContent = `${fertilizer.fertilizers.Urea} kg/ha`;
  $('val-dap').textContent  = `${fertilizer.fertilizers.DAP} kg/ha`;
  $('val-mop').textContent  = `${fertilizer.fertilizers.MOP} kg/ha`;

  // ── NPK Chart ──────────────────────────────────────────────────────────
  renderNPKChart(fertilizer);

  // ── Severity coloring ──────────────────────────────────────────────────
  const metricSev = $('metric-severity');
  metricSev.style.borderColor = severityColor(sev);
}

function severityColor(sev) {
  const map = {
    None: 'rgba(34,197,94,0.4)',
    Low:  'rgba(132,204,22,0.4)',
    Moderate: 'rgba(245,158,11,0.4)',
    High:     'rgba(239,68,68,0.4)',
    Critical: 'rgba(168,85,247,0.5)',
    Unknown:  'rgba(148,163,184,0.3)',
  };
  return map[sev] || map['Unknown'];
}

/* ══════════════════════════════════════════════════════════════════════════
   NPK CHART (Chart.js)
══════════════════════════════════════════════════════════════════════════ */
function renderNPKChart(fertilizer) {
  const ctx = document.getElementById('npk-chart').getContext('2d');

  const { soil, target, deficit } = fertilizer;

  if (state.npkChart) state.npkChart.destroy();

  state.npkChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'],
      datasets: [
        {
          label: 'Current Soil Level',
          data: [soil.N, soil.P, soil.K],
          backgroundColor: 'rgba(6, 182, 212, 0.6)',
          borderColor:     'rgba(6, 182, 212, 1)',
          borderWidth: 1,
          borderRadius: 6,
        },
        {
          label: 'Target Level (ICAR)',
          data: [target.N, target.P, target.K],
          backgroundColor: 'rgba(34, 197, 94, 0.4)',
          borderColor:     'rgba(34, 197, 94, 1)',
          borderWidth: 1,
          borderRadius: 6,
        },
        {
          label: 'Deficit',
          data: [deficit.N, deficit.P, deficit.K],
          backgroundColor: 'rgba(239, 68, 68, 0.45)',
          borderColor:     'rgba(239, 68, 68, 1)',
          borderWidth: 1,
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      animation:           { duration: 800, easing: 'easeInOutQuart' },
      plugins: {
        legend: {
          labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 } },
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.raw} kg/ha`,
          },
          backgroundColor: 'rgba(13,26,32,0.92)',
          titleColor: '#e8f4f8',
          bodyColor:  '#94a3b8',
          borderColor: 'rgba(6,182,212,0.3)',
          borderWidth: 1,
        },
      },
      scales: {
        x: {
          ticks: { color: '#94a3b8', font: { family: 'Inter' } },
          grid:  { color: 'rgba(255,255,255,0.04)' },
        },
        y: {
          ticks: {
            color: '#94a3b8',
            font: { family: 'Inter' },
            callback: v => `${v} kg/ha`,
          },
          grid: { color: 'rgba(255,255,255,0.04)' },
          beginAtZero: true,
        },
      },
    },
  });
}

/* ══════════════════════════════════════════════════════════════════════════
   DISEASE DATABASE PAGE
══════════════════════════════════════════════════════════════════════════ */
let allDiseases = [];

async function loadDiseaseDB() {
  const grid = $('disease-db-grid');
  if (allDiseases.length > 0) { renderDiseaseGrid(allDiseases); return; }

  grid.innerHTML = '<p style="color:var(--text-secondary);padding:20px;">Loading disease database…</p>';

  try {
    const res  = await fetch('/api/disease/classes');
    const data = await res.json();
    allDiseases = data.diseases;
    renderDiseaseGrid(allDiseases);
  } catch {
    grid.innerHTML = '<p style="color:var(--accent-red);padding:20px;">Failed to load disease database.</p>';
  }
}

function renderDiseaseGrid(diseases) {
  const grid = $('disease-db-grid');
  grid.innerHTML = '';

  diseases.forEach(d => {
    const card = document.createElement('div');
    card.className = 'disease-db-card';
    const sevClass = `severity-${(d.severity || 'none').toLowerCase()}`;

    const treatments = [
      ...d.chemical_treatment.slice(0, 2),
      ...d.organic_treatment.slice(0, 1),
    ];

    card.innerHTML = `
      <div class="db-card-header">
        <div>
          <p class="db-card-name">${d.is_healthy ? '✅ ' : '🦠 '}${d.name}</p>
          <p class="db-card-crop">🌱 ${d.crop}</p>
        </div>
        <span class="severity-badge ${sevClass}">${d.severity}</span>
      </div>
      <p class="db-card-desc">${d.description}</p>
      <div class="db-card-tags">
        ${treatments.map(t => `<span class="db-tag">${t.length > 30 ? t.substring(0, 28) + '…' : t}</span>`).join('')}
      </div>
    `;
    grid.appendChild(card);
  });
}

function initDiseaseSearch() {
  $('disease-search').addEventListener('input', e => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) { renderDiseaseGrid(allDiseases); return; }
    const filtered = allDiseases.filter(d =>
      d.name.toLowerCase().includes(q) ||
      d.crop.toLowerCase().includes(q) ||
      d.description.toLowerCase().includes(q)
    );
    renderDiseaseGrid(filtered);
  });
}

/* ══════════════════════════════════════════════════════════════════════════
   LOADING STATE
══════════════════════════════════════════════════════════════════════════ */
function setLoading(on) {
  state.isLoading = on;
  els.analyzeBtn.disabled  = on;
  els.btnText.textContent  = on ? 'Analyzing…' : 'Analyze Crop';
  if (on) {
    els.btnSpinner.classList.remove('hidden');
    els.btnIcon.classList.add('hidden');
  } else {
    els.btnSpinner.classList.add('hidden');
    els.btnIcon.classList.remove('hidden');
  }
}

/* ══════════════════════════════════════════════════════════════════════════
   TOAST NOTIFICATIONS
══════════════════════════════════════════════════════════════════════════ */
function showToast(msg, type = 'info') {
  // Remove existing
  document.querySelectorAll('.toast').forEach(t => t.remove());

  const colors = {
    success: 'var(--accent-green)',
    error:   'var(--accent-red)',
    warning: 'var(--accent-amber)',
    info:    'var(--accent-cyan)',
  };
  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.innerHTML = `<span>${icons[type] || ''}</span><span>${msg}</span>`;
  Object.assign(toast.style, {
    position:   'fixed',
    bottom:     '24px',
    right:      '24px',
    zIndex:     '9999',
    background: 'rgba(13,26,32,0.95)',
    border:     `1px solid ${colors[type] || colors.info}`,
    borderRadius: '10px',
    padding:    '12px 20px',
    display:    'flex',
    gap:        '10px',
    alignItems: 'center',
    color:      colors[type] || colors.info,
    fontFamily: 'Inter, sans-serif',
    fontSize:   '0.88rem',
    fontWeight: '500',
    backdropFilter: 'blur(12px)',
    boxShadow:  '0 8px 32px rgba(0,0,0,0.4)',
    animation:  'slide-up 0.3s ease',
  });

  document.head.insertAdjacentHTML('beforeend', `
    <style>
      @keyframes slide-up { from { opacity:0; transform: translateY(16px); } to { opacity:1; transform:none; } }
    </style>
  `);

  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

/* ══════════════════════════════════════════════════════════════════════════
   INITIALISATION
══════════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', async () => {
  initNavigation();
  initUpload();
  initAnalyzeButton();
  initDiseaseSearch();
  await loadDistricts();

  // District change → fetch weather
  els.districtSelect.addEventListener('change', e => {
    fetchWeather(e.target.value);
  });
});
