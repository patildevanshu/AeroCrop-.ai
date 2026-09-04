/**
 * AeroCrop.ai — Frontend Application (View Layer)
 *
 * Responsibilities (MVC View):
 *  - Farmer authentication (Registration, Login, JWT session management)
 *  - Multi-crop & farm plot management (CRUD operations, quick-diagnosis linking)
 *  - Multi-modal leaf diagnosis and yield forecasting
 *  - Persistent server-synced diagnosis history with image thumbnails
 *  - Interactive Chart.js NPK visualization
 *  - Comprehensive multilingual support (EN / मराठी / हिंदी)
 *  - Advisory report export & printing
 */

'use strict';

/* ══════════════════════════════════════════════════════════════════════════
   INTERNATIONALISATION (i18n)
══════════════════════════════════════════════════════════════════════════ */
const I18N = {
  en: {
    nav_diagnose: 'Diagnose',      nav_my_crops: 'My Crops & Plots',
    nav_dashboard: 'Dashboard',   nav_diseases: 'Disease DB',   nav_about: 'About',
    btn_login_register: 'Farmer Sign In',
    diagnose_title: 'Crop Disease Diagnostics',
    diagnose_subtitle: 'Upload a leaf image to diagnose diseases, get fertilizer recommendations, and forecast your yield.',
    weather_temp: 'Temp',         weather_hum: 'Humidity',    weather_rain: 'Rainfall',
    leaf_image: 'Leaf Image',     upload_text: 'Drag & drop leaf photo', upload_hint: 'or click to browse',
    browse_file: 'Browse File',   params_title: 'Crop & Soil Parameters',
    link_plot: 'Link to My Farm Plot', optional: 'Optional',
    crop_type: 'Crop Type',       district_label: 'Maharashtra District',
    nitrogen: 'Nitrogen (N)',     phosphorus: 'Phosphorus (P)', potassium: 'Potassium (K)',
    analyze_btn: 'Analyze Crop',
    detected_disease: 'Detected Disease', confidence: 'Confidence',
    predicted_yield: 'Predicted Yield',   severity: 'Severity',
    treatment_title: 'Treatment Prescription', chemical_treatments: 'Chemical Treatments',
    organic_treatments: 'Organic / Bio Treatments', fertilizer_title: 'Fertilizer Dosage',
    print_report: 'Print / Save Report',
    npk_chart_title: 'Soil Nutrient Analysis — Current vs Target',
    my_crops_title: 'My Crops & Farm Plots',
    my_crops_subtitle: 'Manage your multiple agricultural fields, track acreages, and run quick diagnoses per plot.',
    add_plot_btn: 'Add New Crop Plot',
    dashboard_title: 'Agricultural Dashboard',
    dashboard_subtitle: 'Platform overview, recent diagnostics history, and multi-district weather telemetry.',
    stat_accuracy: 'AI Accuracy', stat_farmer_plots: 'My Active Plots',
    stat_farmer_acres: 'Monitored Acres', stat_districts: 'Districts Covered',
    recent_diagnostics: 'Recent Diagnostics', clear_history: 'Clear',
    no_history: 'No diagnostics yet. Run your first analysis to see results here.',
    weather_overview: 'Maharashtra Weather Overview', loading_weather: 'Loading district weather…',
    disease_db_title: 'Disease Knowledge Base',
    disease_db_subtitle: 'Complete 38-class PlantVillage disease taxonomy with treatments.',
    about_title: 'About AeroCrop.ai',
    about_subtitle: 'Multi-Modal Deep Learning for Maharashtra Agriculture',
    login_id_label: 'Mobile Number or Email', password: 'Password',
    sign_in_btn: 'Sign In', full_name: 'Full Name', phone_number: 'Mobile Number',
    email_optional: 'Email (Optional)', password_min6: 'Password (Min. 6 chars)',
    village_label: 'Taluka / Village', create_account_btn: 'Create Farmer Account',
    register_plot_title: 'Register New Farm Plot', plot_name_label: 'Plot Identifier / Field Name',
    area_acres_label: 'Area (Acres)', soil_type_label: 'Soil Type',
    sowing_date_label: 'Sowing Date', save_plot_btn: 'Save Plot',
  },
  mr: {
    nav_diagnose: 'निदान',         nav_my_crops: 'माझी पिके आणि शेत',
    nav_dashboard: 'डॅशबोर्ड',     nav_diseases: 'रोग DB',        nav_about: 'बद्दल',
    btn_login_register: 'शेतकरी लॉगिन',
    diagnose_title: 'पीक रोग निदान',
    diagnose_subtitle: 'पानाचा फोटो अपलोड करा, रोग शोधा, खत शिफारस मिळवा आणि उत्पन्नाचा अंदाज घ्या.',
    weather_temp: 'तापमान',        weather_hum: 'आर्द्रता',    weather_rain: 'पाऊस',
    leaf_image: 'पानाचा फोटो',    upload_text: 'पानाचा फोटो ड्रॅग करा', upload_hint: 'किंवा ब्राउझ करा',
    browse_file: 'फाइल निवडा',    params_title: 'पीक आणि माती माहिती',
    link_plot: 'माझ्या शेताशी जोडा', optional: 'ऐच्छिक',
    crop_type: 'पीक प्रकार',       district_label: 'महाराष्ट्र जिल्हा',
    nitrogen: 'नत्र (N)',          phosphorus: 'स्फुरद (P)',   potassium: 'पालाश (K)',
    analyze_btn: 'विश्लेषण करा',
    detected_disease: 'आढळलेला रोग', confidence: 'आत्मविश्वास',
    predicted_yield: 'अपेक्षित उत्पन्न', severity: 'तीव्रता',
    treatment_title: 'उपचार शिफारस', chemical_treatments: 'रासायनिक उपचार',
    organic_treatments: 'सेंद्रिय उपचार', fertilizer_title: 'खत मात्रा',
    print_report: 'अहवाल प्रिंट / सेव्ह करा',
    npk_chart_title: 'माती पोषण विश्लेषण — सध्याचे vs लक्ष्य',
    my_crops_title: 'माझी पिके आणि शेती प्लॉट्स',
    my_crops_subtitle: 'तुमची विविध पिके आणि क्षेत्र व्यवस्थापित करा व थेट निदान करा.',
    add_plot_btn: 'नवीन पीक प्लॉट जोडा',
    dashboard_title: 'कृषी डॅशबोर्ड',
    dashboard_subtitle: 'प्लॅटफॉर्म आढावा, अलीकडील निदान इतिहास आणि बहु-जिल्हा हवामान.',
    stat_accuracy: 'AI अचूकता',    stat_farmer_plots: 'माझे सक्रिय प्लॉट्स',
    stat_farmer_acres: 'निरीक्षित क्षेत्र (एकरी)', stat_districts: 'जिल्हे',
    recent_diagnostics: 'अलीकडील निदान', clear_history: 'साफ करा',
    no_history: 'अजून निदान नाही. पहिले विश्लेषण करा.',
    weather_overview: 'महाराष्ट्र हवामान आढावा', loading_weather: 'हवामान लोड होत आहे…',
    disease_db_title: 'रोग ज्ञानकोश',
    disease_db_subtitle: '38-वर्ग PlantVillage रोग ज्ञानकोश.',
    about_title: 'AeroCrop.ai बद्दल',
    about_subtitle: 'महाराष्ट्र कृषीसाठी मल्टी-मोडल डीप लर्निंग',
    login_id_label: 'मोबाईल नंबर किंवा ईमेल', password: 'पासवर्ड',
    sign_in_btn: 'लॉगिन करा', full_name: 'पूर्ण नाव', phone_number: 'मोबाईल नंबर',
    email_optional: 'ईमेल (ऐच्छिक)', password_min6: 'पासवर्ड (किमान ६ अक्षरे)',
    village_label: 'तालुका / गाव', create_account_btn: 'शेतकरी खाते तयार करा',
    register_plot_title: 'नवीन शेत प्लॉट नोंदणी', plot_name_label: 'प्लॉट नाव / गट नंबर',
    area_acres_label: 'क्षेत्रफळ (एकर)', soil_type_label: 'मातीचा प्रकार',
    sowing_date_label: 'पेरणीची तारीख', save_plot_btn: 'प्लॉट सेव्ह करा',
  },
  hi: {
    nav_diagnose: 'निदान',         nav_my_crops: 'मेरी फसलें और खेत',
    nav_dashboard: 'डैशबोर्ड',     nav_diseases: 'रोग DB',        nav_about: 'बारे में',
    btn_login_register: 'किसान साइन इन',
    diagnose_title: 'फसल रोग निदान',
    diagnose_subtitle: 'पत्ती का फोटो अपलोड करें, रोग पहचानें, खाद की सिफारिश और उपज पूर्वानुमान पाएं।',
    weather_temp: 'तापमान',        weather_hum: 'आर्द्रता',    weather_rain: 'वर्षा',
    leaf_image: 'पत्ती का फोटो',  upload_text: 'पत्ती का फोटो यहाँ खींचें', upload_hint: 'या ब्राउज़ करें',
    browse_file: 'फ़ाइल चुनें',   params_title: 'फसल और मृदा मापदंड',
    link_plot: 'अपने खेत से जोड़ें', optional: 'वैकल्पिक',
    crop_type: 'फसल का प्रकार',   district_label: 'महाराष्ट्र जिला',
    nitrogen: 'नाइट्रोजन (N)',     phosphorus: 'फॉस्फोरस (P)', potassium: 'पोटैशियम (K)',
    analyze_btn: 'विश्लेषण करें',
    detected_disease: 'पहचाना गया रोग', confidence: 'आत्मविश्वास',
    predicted_yield: 'अनुमानित उपज', severity: 'गंभीरता',
    treatment_title: 'उपचार सिफारिश', chemical_treatments: 'रासायनिक उपचार',
    organic_treatments: 'जैविक उपचार', fertilizer_title: 'उर्वरक मात्रा',
    print_report: 'रिपोर्ट प्रिंट / सेव करें',
    npk_chart_title: 'मृदा पोषण विश्लेषण — वर्तमान बनाम लक्ष्य',
    my_crops_title: 'मेरी फसलें और खेत',
    my_crops_subtitle: 'अपनी विभिन्न फसलों और खेतों का प्रबंधन करें।',
    add_plot_btn: 'नया खेत जोड़ें',
    dashboard_title: 'कृषि डैशबोर्ड',
    dashboard_subtitle: 'प्लेटफॉर्म अवलोकन, हालिया निदान इतिहास और बहु-जिला मौसम।',
    stat_accuracy: 'AI सटीकता',    stat_farmer_plots: 'सक्रिय प्लॉट्स',
    stat_farmer_acres: 'निगरानी क्षेत्र (एकड़)', stat_districts: 'जिले',
    recent_diagnostics: 'हालिया निदान', clear_history: 'साफ करें',
    no_history: 'अभी तक कोई निदान नहीं। पहला विश्लेषण करें।',
    weather_overview: 'महाराष्ट्र मौसम अवलोकन', loading_weather: 'मौसम लोड हो रहा है…',
    disease_db_title: 'रोग ज्ञानकोश',
    disease_db_subtitle: '38-वर्ग PlantVillage रोग ज्ञानकोश।',
    about_title: 'AeroCrop.ai के बारे में',
    about_subtitle: 'महाराष्ट्र कृषि के लिए मल्टी-मोडल डीप लर्निंग',
    login_id_label: 'मोबाइल नंबर या ईमेल', password: 'पासवर्ड',
    sign_in_btn: 'साइन इन करें', full_name: 'पूरा नाम', phone_number: 'मोबाइल नंबर',
    email_optional: 'ईमेल (वैकल्पिक)', password_min6: 'पासवर्ड (न्यूनतम 6 अक्षर)',
    village_label: 'तहसील / गाँव', create_account_btn: 'किसान खाता बनाएँ',
    register_plot_title: 'नया खेत पंजीकृत करें', plot_name_label: 'खेत का नाम / नंबर',
    area_acres_label: 'क्षेत्रफल (एकड़)', soil_type_label: 'मिट्टी का प्रकार',
    sowing_date_label: 'बुवाई की तारीख', save_plot_btn: 'खेत सुरक्षित करें',
  },
};

let currentLang = 'en';

function setLanguage(lang) {
  if (!I18N[lang]) return;
  currentLang = lang;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (I18N[lang][key] !== undefined) el.textContent = I18N[lang][key];
  });
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.setAttribute('aria-pressed', btn.id === `lang-${lang}` ? 'true' : 'false');
    btn.classList.toggle('active', btn.id === `lang-${lang}`);
  });
}

window.setLanguage = setLanguage;

/* ── State & Constants ─────────────────────────────────────────────────── */
const AUTH_TOKEN_KEY = 'aerocrop_jwt_token';

const state = {
  currentUser:     null,
  userPlots:       [],
  uploadedFile:    null,
  weatherCache:    {},
  npkChart:        null,
  isLoading:       false,
  lastResult:      null,
  dashboardLoaded: false,
};

function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

function setAuthToken(token) {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

function clearAuthToken() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

function getAuthHeaders() {
  const token = getAuthToken();
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

/* ── DOM References ─────────────────────────────────────────────────────── */
const $ = id => document.getElementById(id);

const els = {
  analyzeBtn:        $('analyze-btn'),
  uploadZone:        $('upload-zone'),
  uploadPlaceholder: $('upload-placeholder'),
  fileInput:         $('file-input'),
  previewImg:        $('preview-img'),
  plotSelect:        $('plot-select'),
  cropSelect:        $('crop-select'),
  districtSelect:    $('district-select'),
  inputN:            $('input-N'),
  inputP:            $('input-P'),
  inputK:            $('input-K'),
  resultsArea:       $('results-area'),
  mockBanner:        $('mock-banner'),
  lowConfBanner:     $('low-conf-banner'),
  savedBanner:       $('saved-history-banner'),
  btnText:           document.querySelector('#analyze-btn .btn-text'),
  btnSpinner:        document.querySelector('#analyze-btn .btn-spinner'),
  btnIcon:           document.querySelector('#analyze-btn .btn-icon'),
};

/* ══════════════════════════════════════════════════════════════════════════
   NAVIGATION
══════════════════════════════════════════════════════════════════════════ */
function initNavigation() {
  document.querySelectorAll('.nav-item').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const target = link.getAttribute('href').replace('#', '');
      switchPage(target);
    });
  });
}

function switchPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => {
    n.classList.remove('active');
    n.removeAttribute('aria-current');
  });

  const page = document.getElementById(`page-${name}`);
  const nav  = document.getElementById(`nav-${name}`);
  if (page) { page.classList.remove('hidden'); page.classList.add('active'); }
  if (nav)  { nav.classList.add('active'); nav.setAttribute('aria-current', 'page'); }

  if (name === 'crops')     loadFarmerPlots();
  if (name === 'diseases')  loadDiseaseDB();
  if (name === 'dashboard') initDashboard();
}

/* ══════════════════════════════════════════════════════════════════════════
   AUTHENTICATION SUBSYSTEM
══════════════════════════════════════════════════════════════════════════ */
async function checkAuthStatus() {
  const token = getAuthToken();
  if (!token) {
    renderLoggedOutUI();
    return;
  }

  try {
    const res = await fetch('/api/auth/me', { headers: { 'Authorization': `Bearer ${token}` } });
    if (!res.ok) throw new Error('Session expired');
    const user = await res.json();
    state.currentUser = user;
    renderLoggedInUI(user);
    await loadFarmerPlots();
  } catch {
    clearAuthToken();
    state.currentUser = null;
    renderLoggedOutUI();
  }
}

function renderLoggedInUI(user) {
  $('auth-logged-out').classList.add('hidden');
  $('auth-logged-in').classList.remove('hidden');
  $('user-display-name').textContent = user.full_name;
  $('user-display-district').textContent = `📍 ${user.district.charAt(0).toUpperCase() + user.district.slice(1)}`;

  if (user.preferred_language && user.preferred_language !== currentLang) {
    setLanguage(user.preferred_language);
  }
}

function renderLoggedOutUI() {
  $('auth-logged-out').classList.remove('hidden');
  $('auth-logged-in').classList.add('hidden');
  state.userPlots = [];
  renderPlotSelectOptions();
}

window.openAuthModal = function(tab = 'login') {
  $('auth-modal').classList.remove('hidden');
  populateRegisterDistricts();
  switchAuthTab(tab);
};

window.closeAuthModal = function() {
  $('auth-modal').classList.add('hidden');
};

window.switchAuthTab = function(tab) {
  $('tab-login').classList.toggle('active', tab === 'login');
  $('tab-register').classList.toggle('active', tab === 'register');
  $('form-login').classList.toggle('hidden', tab !== 'login');
  $('form-register').classList.toggle('hidden', tab !== 'register');
};

window.handleLoginSubmit = async function(e) {
  e.preventDefault();
  const identifier = $('login-id').value.trim();
  const password   = $('login-password').value;

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');

    setAuthToken(data.access_token);
    state.currentUser = data.user;
    renderLoggedInUI(data.user);
    closeAuthModal();
    showToast(`Welcome back, ${data.user.full_name}!`, 'success');
    await loadFarmerPlots();
  } catch (err) {
    showToast(err.message, 'error');
  }
};

window.handleRegisterSubmit = async function(e) {
  e.preventDefault();
  const full_name    = $('reg-name').value.trim();
  const phone_number = $('reg-phone').value.trim() || null;
  const email        = $('reg-email').value.trim() || null;
  const password     = $('reg-password').value;
  const district     = $('reg-district').value || 'pune';
  const taluka_village = $('reg-village').value.trim() || null;

  if (!phone_number && !email) {
    showToast('Please provide at least a mobile number or email.', 'warning');
    return;
  }

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        full_name, phone_number, email, password, district, taluka_village,
        preferred_language: currentLang,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed');

    setAuthToken(data.access_token);
    state.currentUser = data.user;
    renderLoggedInUI(data.user);
    closeAuthModal();
    showToast(`Account created! Welcome, ${data.user.full_name}!`, 'success');
    await loadFarmerPlots();
  } catch (err) {
    showToast(err.message, 'error');
  }
};

window.logoutFarmer = function() {
  clearAuthToken();
  state.currentUser = null;
  renderLoggedOutUI();
  showToast('Logged out successfully.', 'info');
  switchPage('diagnose');
};

function populateRegisterDistricts() {
  const regSel = $('reg-district');
  if (regSel.children.length > 0) return;
  const mainSel = $('district-select');
  Array.from(mainSel.options).forEach(opt => {
    if (opt.value) {
      const o = document.createElement('option');
      o.value = opt.value;
      o.textContent = opt.textContent;
      regSel.appendChild(o);
    }
  });
}

/* ══════════════════════════════════════════════════════════════════════════
   MULTI-CROP & PLOT MANAGEMENT
══════════════════════════════════════════════════════════════════════════ */
async function loadFarmerPlots() {
  if (!state.currentUser) return;

  try {
    const res = await fetch('/api/farmer/plots', { headers: getAuthHeaders() });
    if (!res.ok) return;
    const data = await res.json();
    state.userPlots = data.plots;
    renderPlotsGrid(data.plots);
    renderPlotSelectOptions();
    updateDashboardPlotStats();
  } catch (err) {
    console.warn('Failed to load plots:', err);
  }
}

function renderPlotsGrid(plots) {
  const container = $('plots-container');
  if (!container) return;

  if (!plots.length) {
    container.innerHTML = `
      <div class="card glass" style="grid-column: 1/-1; text-align:center; padding:40px;">
        <p style="font-size:2rem; margin-bottom:8px;">🌾</p>
        <h3>No Farm Plots Registered Yet</h3>
        <p style="color:var(--text-secondary); margin:8px 0 20px;">Register your fields to track different crops, acreages, and localized soil health.</p>
        <button class="btn btn-primary" onclick="openAddPlotModal()">➕ Add Your First Plot</button>
      </div>`;
    return;
  }

  const cropIcons = {
    cotton: '🌱', wheat: '🌾', maize: '🌽', rice: '🍚', potato: '🥔',
    tomato: '🍅', pepper: '🌶️', apple: '🍎', grape: '🍇', orange: '🍊',
    peach: '🍑', strawberry: '🍓', soybean: '🫘', cherry: '🍒',
    blueberry: '🫐', squash: '🎃', raspberry: '🫐',
  };

  container.innerHTML = plots.map(p => {
    const icon = cropIcons[p.crop_type] || '🌱';
    const diagInfo = p.latest_diagnosis
      ? `<span class="plot-stat-chip">${p.latest_diagnosis.is_healthy ? '✅ Healthy' : '⚠️ ' + p.latest_diagnosis.disease_name}</span>`
      : `<span class="plot-stat-chip">No recent diagnosis</span>`;

    return `
      <div class="card glass plot-card">
        <div>
          <div class="plot-header">
            <h3 class="plot-title">${p.plot_name}</h3>
            <span class="plot-crop-badge">${icon} ${p.crop_type.toUpperCase()}</span>
          </div>
          <p class="plot-meta mt-2">
            <strong>Area:</strong> ${p.area_acres} Acres · <strong>Soil:</strong> ${p.soil_type}<br>
            <strong>Baseline NPK:</strong> ${p.baseline_N}-${p.baseline_P}-${p.baseline_K} kg/ha
          </p>
          <div class="plot-stats-row mt-2">
            <span class="plot-stat-chip">📊 ${p.total_diagnoses} Analyses</span>
            ${diagInfo}
          </div>
        </div>
        <div class="plot-actions">
          <button class="btn btn-primary btn-sm btn-full" onclick="quickDiagnoseOnPlot(${p.id})">
            🔬 Quick Diagnose
          </button>
          <button class="btn-icon-sm" onclick="deleteFarmerPlot(${p.id})" title="Delete plot">🗑️</button>
        </div>
      </div>`;
  }).join('');
}

function renderPlotSelectOptions() {
  const sel = els.plotSelect;
  if (!sel) return;
  sel.innerHTML = '<option value="">-- No plot linked (General diagnosis) --</option>';

  state.userPlots.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.textContent = `📍 ${p.plot_name} (${p.crop_type.toUpperCase()} — ${p.area_acres} Acres)`;
    sel.appendChild(opt);
  });
}

function initPlotSelectorSync() {
  if (!els.plotSelect) return;
  els.plotSelect.addEventListener('change', e => {
    const plotId = parseInt(e.target.value);
    if (!plotId) return;
    const plot = state.userPlots.find(p => p.id === plotId);
    if (plot) {
      // Sync crop
      els.cropSelect.value = plot.crop_type;
      if (els.inputN && plot.baseline_N != null) els.inputN.value = plot.baseline_N;
      if (els.inputP && plot.baseline_P != null) els.inputP.value = plot.baseline_P;
      if (els.inputK && plot.baseline_K != null) els.inputK.value = plot.baseline_K;
      showToast(`Linked to ${plot.plot_name} (${plot.crop_type})`, 'info');
    }
  });
}

window.quickDiagnoseOnPlot = function(plotId) {
  switchPage('diagnose');
  els.plotSelect.value = plotId;
  const plot = state.userPlots.find(p => p.id === plotId);
  if (plot) {
    els.cropSelect.value = plot.crop_type;
    if (els.inputN && plot.baseline_N != null) els.inputN.value = plot.baseline_N;
    if (els.inputP && plot.baseline_P != null) els.inputP.value = plot.baseline_P;
    if (els.inputK && plot.baseline_K != null) els.inputK.value = plot.baseline_K;
  }
  els.uploadZone.scrollIntoView({ behavior: 'smooth' });
};

window.openAddPlotModal = function() {
  if (!state.currentUser) {
    openAuthModal('login');
    return;
  }
  $('form-plot').reset();
  $('plot-edit-id').value = '';
  $('plot-modal').classList.remove('hidden');
};

window.closePlotModal = function() {
  $('plot-modal').classList.add('hidden');
};

window.handlePlotSubmit = async function(e) {
  e.preventDefault();
  const plot_name  = $('modal-plot-name').value.trim();
  const crop_type  = $('modal-plot-crop').value;
  const area_acres = parseFloat($('modal-plot-acres').value);
  const soil_type  = $('modal-plot-soil').value;
  const sowing_date = $('modal-plot-sowing').value || null;
  const baseline_N = parseFloat($('modal-plot-N').value);
  const baseline_P = parseFloat($('modal-plot-P').value);
  const baseline_K = parseFloat($('modal-plot-K').value);

  try {
    const res = await fetch('/api/farmer/plots', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({
        plot_name, crop_type, area_acres, soil_type, sowing_date,
        baseline_N, baseline_P, baseline_K,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Could not save plot');

    closePlotModal();
    showToast(`Plot '${plot_name}' added successfully!`, 'success');
    await loadFarmerPlots();
  } catch (err) {
    showToast(err.message, 'error');
  }
};

window.deleteFarmerPlot = async function(plotId) {
  if (!confirm('Are you sure you want to delete this farm plot?')) return;
  try {
    const res = await fetch(`/api/farmer/plots/${plotId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!res.ok) throw new Error('Failed to delete plot');
    showToast('Plot deleted.', 'info');
    await loadFarmerPlots();
  } catch (err) {
    showToast(err.message, 'error');
  }
};

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

  const windEl = $('val-wind');
  if (windEl) {
    windEl.textContent = `${data.wind_speed || 8} km/h`;
  }

  const sprayEl = $('val-quick-spray');
  if (sprayEl && data.spray_window) {
    sprayEl.textContent = data.spray_window.safe ? '🟢 Safe' : (data.spray_window.status === 'warning' ? '🟡 Caution' : '🔴 Hold');
    sprayEl.style.color = data.spray_window.safe ? '#34d399' : (data.spray_window.status === 'warning' ? '#fbbf24' : '#f87171');
  }

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
  els.uploadZone.addEventListener('click', () => els.fileInput.click());

  els.uploadZone.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); els.fileInput.click(); }
  });

  els.fileInput.addEventListener('change', e => {
    if (e.target.files[0]) handleFileSelect(e.target.files[0]);
  });

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
  if (!state.uploadedFile) {
    showToast('Please upload a leaf image first.', 'warning');
    return;
  }

  setLoading(true);

  const form = new FormData();
  form.append('image',    state.uploadedFile);
  form.append('crop',     els.cropSelect.value);
  form.append('district', els.districtSelect.value);

  if (els.inputN && els.inputN.value) form.append('N', els.inputN.value);
  if (els.inputP && els.inputP.value) form.append('P', els.inputP.value);
  if (els.inputK && els.inputK.value) form.append('K', els.inputK.value);

  const selectedPlotId = els.plotSelect ? els.plotSelect.value : '';
  if (selectedPlotId) form.append('plot_id', selectedPlotId);

  try {
    const res  = await fetch('/api/predict', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: form,
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || 'Prediction failed');

    state.lastResult = data;
    renderResults(data);
    
    // Save to localStorage history for guest or reload server history for user
    if (!state.currentUser) saveToLocalHistory(data);
    else await loadFarmerPlots();

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
  const { disease, yield_t_ha, fertilizer, mock_mode, weather, low_confidence, saved_record_id } = data;

  // Mode banners
  els.mockBanner.classList.toggle('hidden', !mock_mode);
  if (els.lowConfBanner) els.lowConfBanner.classList.toggle('hidden', !low_confidence);
  if (els.savedBanner) els.savedBanner.classList.toggle('hidden', !saved_record_id);

  // Weather update
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

  // ── Spray Window Weather Advisory ─────────────────────────────────────
  const sprayDiv = $('spray-window-banner');
  if (sprayDiv && weather && weather.spray_window) {
    const sw = weather.spray_window;
    sprayDiv.className = `spray-window-banner ${sw.status}`;
    const reason = currentLang === 'mr' ? sw.reason_mr : (currentLang === 'hi' ? sw.reason_hi : sw.reason);
    const icon = sw.status === 'danger' ? '🚫' : (sw.status === 'warning' ? '⚠️' : '🎯');
    sprayDiv.innerHTML = `<span style="font-size:1.4rem">${icon}</span><div><strong>${sw.badge}</strong><div style="font-size:0.88rem;color:#e2e8f0;">${reason}</div></div>`;
    sprayDiv.classList.remove('hidden');
  } else if (sprayDiv) {
    sprayDiv.classList.add('hidden');
  }

  // ── Fertilizer ─────────────────────────────────────────────────────────
  $('res-fert-interpretation').textContent = fertilizer.interpretation;
  recalculateFertilizerBags();

  // Surplus N warning
  const surplusDiv = $('res-npk-surplus');
  if (surplusDiv && fertilizer.surplus_n_warning) {
    surplusDiv.textContent = `⚠️ ${fertilizer.surplus_n_warning}`;
    surplusDiv.classList.remove('hidden');
  } else if (surplusDiv) {
    surplusDiv.classList.add('hidden');
  }

  // ── Mandi Intelligence Card ────────────────────────────────────────────
  const mandiCard = $('mandi-card');
  if (mandiCard && data.mandi) {
    const m = data.mandi;
    $('mandi-market-label').textContent = `📍 ${m.apmc_market}`;
    $('mandi-modal-val').textContent = `₹${m.modal_price_inr.toLocaleString('en-IN')}`;
    $('mandi-range-val').textContent = `₹${m.min_price_inr} – ₹${m.max_price_inr}`;
    $('mandi-msp-val').textContent = m.msp_inr > 0 ? `₹${m.msp_inr.toLocaleString('en-IN')}` : `${m.arrivals_quintal} q arrivals`;
    const trendIcon = m.trend === 'bullish' ? '▲' : (m.trend === 'bearish' ? '▼' : '▬');
    $('mandi-trend-val').textContent = `${trendIcon} ${m.trend.toUpperCase()} (${m.trend_change_pct}%)`;
    if (m.revenue_projection) {
      $('mandi-revenue-val').textContent = `₹${m.revenue_projection.gross_revenue_acre_inr.toLocaleString('en-IN')} / Acre  |  ₹${m.revenue_projection.gross_revenue_ha_inr.toLocaleString('en-IN')} / Hectare`;
    }
    mandiCard.classList.remove('hidden');
  } else if (mandiCard) {
    mandiCard.classList.add('hidden');
  }

  // ── NPK Chart ──────────────────────────────────────────────────────────
  renderNPKChart(fertilizer);

  // ── Severity coloring ──────────────────────────────────────────────────
  const metricSev = $('metric-severity');
  metricSev.style.borderColor = severityColor(sev);
}

function severityColor(sev) {
  const map = {
    None:     'rgba(34,197,94,0.4)',
    Low:      'rgba(132,204,22,0.4)',
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
  const canvas = document.getElementById('npk-chart');
  if (!canvas || !fertilizer || !fertilizer.soil) return;
  const ctx = canvas.getContext('2d');
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
          borderWidth: 1, borderRadius: 6,
        },
        {
          label: 'Target Level (ICAR)',
          data: [target.N, target.P, target.K],
          backgroundColor: 'rgba(34, 197, 94, 0.4)',
          borderColor:     'rgba(34, 197, 94, 1)',
          borderWidth: 1, borderRadius: 6,
        },
        {
          label: 'Deficit',
          data: [deficit.N, deficit.P, deficit.K],
          backgroundColor: 'rgba(239, 68, 68, 0.45)',
          borderColor:     'rgba(239, 68, 68, 1)',
          borderWidth: 1, borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 800, easing: 'easeInOutQuart' },
      plugins: {
        legend: { labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 } } },
        tooltip: {
          callbacks: { label: ctx => ` ${ctx.dataset.label}: ${ctx.raw} kg/ha` },
          backgroundColor: 'rgba(13,26,32,0.92)', titleColor: '#e8f4f8',
          bodyColor: '#94a3b8', borderColor: 'rgba(6,182,212,0.3)', borderWidth: 1,
        },
      },
      scales: {
        x: { ticks: { color: '#94a3b8', font: { family: 'Inter' } }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: {
          ticks: { color: '#94a3b8', font: { family: 'Inter' }, callback: v => `${v} kg/ha` },
          grid: { color: 'rgba(255,255,255,0.04)' }, beginAtZero: true,
        },
      },
    },
  });
}

/* ══════════════════════════════════════════════════════════════════════════
   DASHBOARD & PERSISTENT HISTORY
══════════════════════════════════════════════════════════════════════════ */
async function initDashboard() {
  await loadFarmerHistory();
  if (!state.dashboardLoaded) {
    await loadWeatherRadar();
    state.dashboardLoaded = true;
  }
}

async function loadFarmerHistory() {
  const list = $('history-list');
  if (!list) return;

  if (state.currentUser) {
    // Authenticated user — fetch server-persisted database history
    const filterCrop = $('history-filter-crop')?.value || '';
    const url = filterCrop ? `/api/farmer/history?crop_type=${encodeURIComponent(filterCrop)}` : '/api/farmer/history';

    try {
      const res = await fetch(url, { headers: getAuthHeaders() });
      if (!res.ok) return;
      const data = await res.json();
      renderServerHistory(data.records);
    } catch {
      list.innerHTML = '<p class="no-history">Could not load diagnosis history.</p>';
    }
  } else {
    // Guest user — render localStorage history
    renderLocalHistoryList();
  }
}

function renderServerHistory(records) {
  const list = $('history-list');
  if (!list) return;

  if (!records || !records.length) {
    list.innerHTML = `<p class="no-history">${I18N[currentLang]?.no_history || 'No diagnostics yet.'}</p>`;
    return;
  }

  list.innerHTML = records.map(r => {
    const d = new Date(r.created_at);
    const timeStr = d.toLocaleDateString('en-IN') + ' ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    const sevClass = `severity-${(r.severity || 'none').toLowerCase()}`;
    const imgTag = r.image_url ? `<img src="${r.image_url}" class="history-thumb" alt="Leaf photo thumbnail" />` : `<div class="history-icon">${r.is_healthy ? '✅' : '🦠'}</div>`;
    const plotLabel = r.plot_name ? ` · <strong>Plot:</strong> ${r.plot_name}` : '';

    return `
      <div class="history-item glass">
        ${imgTag}
        <div class="history-body">
          <p class="history-disease">${r.disease_name}</p>
          <p class="history-meta">${r.crop_type.toUpperCase()} · ${r.district.toUpperCase()}${plotLabel} · ${timeStr}</p>
          <p class="history-meta">Yield: ${r.predicted_yield_t_ha} t/ha · Confidence: ${r.confidence.toFixed(1)}%</p>
        </div>
        <span class="severity-badge ${sevClass}">${r.severity}</span>
      </div>`;
  }).join('');
}

const LOCAL_HISTORY_KEY = 'aerocrop_history';

function saveToLocalHistory(data) {
  const history = getLocalHistory();
  const entry = {
    ts:       Date.now(),
    crop:     data.crop,
    district: data.district,
    disease:  data.disease.name,
    conf:     data.disease.confidence,
    severity: data.disease.severity,
    healthy:  data.disease.is_healthy,
    yield:    data.yield_t_ha,
  };
  history.unshift(entry);
  if (history.length > 20) history.pop();
  localStorage.setItem(LOCAL_HISTORY_KEY, JSON.stringify(history));
}

function getLocalHistory() {
  try { return JSON.parse(localStorage.getItem(LOCAL_HISTORY_KEY) || '[]'); }
  catch { return []; }
}

function renderLocalHistoryList() {
  const list = $('history-list');
  if (!list) return;
  const history = getLocalHistory();
  if (!history.length) {
    list.innerHTML = `<p class="no-history">${I18N[currentLang]?.no_history || 'No diagnostics yet.'}</p>`;
    return;
  }
  list.innerHTML = history.map(e => {
    const d = new Date(e.ts);
    const timeStr = d.toLocaleDateString('en-IN') + ' ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
    const sevClass = `severity-${(e.severity || 'none').toLowerCase()}`;
    return `
      <div class="history-item glass">
        <div class="history-icon">${e.healthy ? '✅' : '🦠'}</div>
        <div class="history-body">
          <p class="history-disease">${e.disease}</p>
          <p class="history-meta">${e.crop} · ${e.district} · ${timeStr}</p>
          <p class="history-meta">Yield: ${e.yield} t/ha · Confidence: ${e.conf.toFixed(1)}%</p>
        </div>
        <span class="severity-badge ${sevClass}">${e.severity}</span>
      </div>`;
  }).join('');
}

window.clearHistory = function() {
  localStorage.removeItem(LOCAL_HISTORY_KEY);
  if (state.currentUser) loadFarmerHistory();
  else renderLocalHistoryList();
  showToast('History cleared.', 'info');
};

function updateDashboardPlotStats() {
  if (!state.currentUser || !state.userPlots) return;
  const plotsVal = $('stat-plots-val');
  const acresVal = $('stat-acres-val');
  if (plotsVal) plotsVal.textContent = state.userPlots.length;
  if (acresVal) {
    const totalAcres = state.userPlots.reduce((acc, p) => acc + (p.area_acres || 0), 0);
    acresVal.textContent = totalAcres.toFixed(1);
  }
}

// ── Weather Radar ──────────────────────────────────────────────────────────
const RADAR_DISTRICTS = ['pune', 'nagpur', 'nashik', 'aurangabad', 'amravati', 'kolhapur', 'solapur', 'akola'];

async function loadWeatherRadar() {
  const radar = $('weather-radar');
  if (!radar) return;

  const results = await Promise.allSettled(
    RADAR_DISTRICTS.map(d =>
      state.weatherCache[d]
        ? Promise.resolve(state.weatherCache[d])
        : fetch(`/api/weather/${encodeURIComponent(d)}`).then(r => r.json())
    )
  );

  radar.innerHTML = '';
  results.forEach((res, i) => {
    const d = RADAR_DISTRICTS[i];
    const label = d.charAt(0).toUpperCase() + d.slice(1);
    if (res.status === 'fulfilled') {
      const w = res.value;
      state.weatherCache[d] = w;
      radar.innerHTML += `
        <div class="radar-card glass">
          <p class="radar-district">${label}</p>
          <p class="radar-temp">🌡️ ${w.temperature}°C</p>
          <p class="radar-hum">💧 ${w.humidity}%</p>
          <p class="radar-rain">🌧️ ${w.rainfall} mm</p>
          ${w.source === 'mock' ? '<span class="radar-mock">mock</span>' : ''}
        </div>`;
    } else {
      radar.innerHTML += `<div class="radar-card glass"><p class="radar-district">${label}</p><p class="no-history">Unavailable</p></div>`;
    }
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
   FARMER ERGONOMICS: BAGS, VOICE & SHARING
══════════════════════════════════════════════════════════════════════════ */
window.recalculateFertilizerBags = function() {
  if (!state.lastResult || !state.lastResult.fertilizer) return;
  const areaEl = $('fert-calc-area');
  const unitEl = $('fert-calc-unit');
  const area = parseFloat(areaEl ? areaEl.value : 1.0) || 1.0;
  const unit = unitEl ? unitEl.value : 'acre';

  const mult = unit === 'ha' ? area : (unit === 'acre' ? area / 2.47105 : area / 100.0);
  const ferts = state.lastResult.fertilizer.fertilizers;

  const ureaKg = ferts.Urea * mult;
  const dapKg = ferts.DAP * mult;
  const mopKg = ferts.MOP * mult;

  const ureaBags = Math.ceil(ureaKg / 50.0);
  const dapBags = Math.ceil(dapKg / 50.0);
  const mopBags = Math.ceil(mopKg / 50.0);

  const costUrea = ureaBags * 267;
  const costDap = dapBags * 1350;
  const costMop = mopBags * 1700;
  const totalCost = costUrea + costDap + costMop;

  $('val-urea').textContent = `${ureaBags} bags (50kg)`;
  $('note-urea').textContent = `${ureaKg.toFixed(1)} kg • ₹${costUrea.toLocaleString('en-IN')}`;

  $('val-dap').textContent = `${dapBags} bags (50kg)`;
  $('note-dap').textContent = `${dapKg.toFixed(1)} kg • ₹${costDap.toLocaleString('en-IN')}`;

  $('val-mop').textContent = `${mopBags} bags (50kg)`;
  $('note-mop').textContent = `${mopKg.toFixed(1)} kg • ₹${costMop.toLocaleString('en-IN')}`;

  const costBanner = $('val-fert-total-cost');
  if (costBanner) costBanner.textContent = `₹${totalCost.toLocaleString('en-IN')}`;
};

let isVoiceSpeaking = false;
window.toggleVoicePrescription = function() {
  if (!('speechSynthesis' in window)) {
    showToast('Speech synthesis is not supported on this browser.', 'warning');
    return;
  }
  if (isVoiceSpeaking) {
    window.speechSynthesis.cancel();
    isVoiceSpeaking = false;
    const btn = $('btn-voice-listen');
    if (btn) btn.innerHTML = '<span>🔊</span> <span>Listen Advisory</span>';
    return;
  }
  if (!state.lastResult) return;
  const d = state.lastResult;
  let script = '';
  if (currentLang === 'mr') {
    script = `पिकाचा रोग: ${d.disease.name}. ${d.disease.description}. रासायनिक उपाय: ${(d.disease.chemical_treatment || []).join('. ')}. सेंद्रिय उपाय: ${(d.disease.organic_treatment || []).join('. ')}.`;
  } else if (currentLang === 'hi') {
    script = `फसल का रोग: ${d.disease.name}। ${d.disease.description}। रासायनिक उपचार: ${(d.disease.chemical_treatment || []).join('. ')}। जैविक उपाय: ${(d.disease.organic_treatment || []).join('. ')}।`;
  } else {
    script = `Crop Disease: ${d.disease.name}. ${d.disease.description}. Chemical treatments: ${(d.disease.chemical_treatment || []).join('. ')}. Organic remedies: ${(d.disease.organic_treatment || []).join('. ')}.`;
  }

  const u = new SpeechSynthesisUtterance(script);
  u.lang = currentLang === 'mr' ? 'mr-IN' : (currentLang === 'hi' ? 'hi-IN' : 'en-IN');
  u.onend = () => {
    isVoiceSpeaking = false;
    const btn = $('btn-voice-listen');
    if (btn) btn.innerHTML = '<span>🔊</span> <span>Listen Advisory</span>';
  };
  u.onerror = () => {
    isVoiceSpeaking = false;
    const btn = $('btn-voice-listen');
    if (btn) btn.innerHTML = '<span>🔊</span> <span>Listen Advisory</span>';
  };

  isVoiceSpeaking = true;
  const btn = $('btn-voice-listen');
  if (btn) btn.innerHTML = '<span>⏹️</span> <span>Stop Audio</span>';
  window.speechSynthesis.speak(u);
};

window.shareWhatsApp = function() {
  if (!state.lastResult) {
    showToast('Run an analysis first to share.', 'warning');
    return;
  }
  const d = state.lastResult;
  const msg = `*AeroCrop.ai Farmer Crop Advisory* 🌿
🌱 *Crop*: ${d.crop}
📍 *District*: ${d.district}
🦠 *Condition*: ${d.disease.name} (${d.disease.confidence}% confidence)
⚠️ *Severity*: ${d.disease.severity}
🌾 *Yield Forecast*: ${d.yield_t_ha} t/ha (${(d.yield_t_ha * 4.047).toFixed(1)} q/acre)
💊 *Chemical*: ${(d.disease.chemical_treatment || []).slice(0, 2).join(', ')}
🌿 *Organic*: ${(d.disease.organic_treatment || []).slice(0, 2).join(', ')}
🧬 *Fertilizer Plan*: Urea: ${d.fertilizer.fertilizers.Urea} kg/ha, DAP: ${d.fertilizer.fertilizers.DAP} kg/ha
Generated via AeroCrop.ai Precision Agriculture Platform`;

  window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(msg)}`, '_blank');
};

/* ══════════════════════════════════════════════════════════════════════════
   PRINT / SAVE PRESCRIPTION REPORT (WITH PMFBY MODE)
══════════════════════════════════════════════════════════════════════════ */
window.printReport = function(isPmfby = false) {
  if (!state.lastResult) {
    showToast('Run an analysis first before printing.', 'warning');
    return;
  }
  const d = state.lastResult;
  const disease = d.disease;
  const fert    = d.fertilizer;
  const now     = new Date().toLocaleString('en-IN');
  const farmerName = state.currentUser ? state.currentUser.full_name : 'Guest Farmer';
  const title = isPmfby ? '🇮🇳 PMFBY Crop Damage Assessment & Loss Verification Report' : '🌿 AeroCrop.ai — Crop Advisory Report';

  const html = `<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>${title}</title>
<style>
  body { font-family: Arial, sans-serif; padding: 28px; color: #111; max-width: 800px; margin: 0 auto; line-height: 1.5; }
  h1 { color: #16a34a; border-bottom: 2px solid #16a34a; padding-bottom: 8px; margin-top: 0; }
  h2 { color: #0e7490; margin-top: 20px; font-size: 1.1rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
  .row { display: flex; gap: 24px; margin-bottom: 12px; }
  .cell { flex: 1; }
  table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 0.9rem; }
  th, td { border: 1px solid #cbd5e1; padding: 6px 10px; text-align: left; }
  th { background: #f0fdf4; color: #15803d; }
  .footer { margin-top: 32px; font-size: 0.8rem; color: #64748b; border-top: 1px solid #cbd5e1; padding-top: 8px; }
  ul { padding-left: 20px; margin: 4px 0; }
  li { margin-bottom: 4px; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 700;
           background: #fef9c3; color: #854d0e; }
  .sign-row { display: flex; justify-content: space-between; margin-top: 48px; padding-top: 12px; }
  .sign-box { border-top: 1px dashed #64748b; width: 220px; text-align: center; font-size: 0.82rem; color: #334155; padding-top: 6px; }
  @media print { body { padding: 16px; } }
</style></head><body>
  <h1>${title}</h1>
  <p><strong>Farmer:</strong> ${farmerName} | <strong>Generated:</strong> ${now}</p>
  <div class="row">
    <div class="cell"><strong>Crop:</strong> ${d.crop}</div>
    <div class="cell"><strong>District:</strong> ${d.district}</div>
    <div class="cell"><strong>Mode:</strong> ${d.mock_mode ? 'Smart Mock' : 'Neural Model (90.82% acc)'}</div>
  </div>

  <h2>🦠 Disease Diagnosis</h2>
  <table>
    <tr><th>Disease</th><td>${disease.name}</td></tr>
    <tr><th>Confidence</th><td>${disease.confidence.toFixed(1)}%</td></tr>
    <tr><th>Severity</th><td><span class="badge">${disease.severity}</span></td></tr>
    <tr><th>Status</th><td>${disease.is_healthy ? '✅ Healthy' : '⚠️ Diseased'}</td></tr>
    <tr><th>Description</th><td>${disease.description}</td></tr>
  </table>

  <h2>💊 Treatment Prescription</h2>
  <div class="row">
    <div class="cell">
      <strong>Chemical:</strong>
      <ul>${(disease.chemical_treatment || []).map(t => `<li>${t}</li>`).join('')}</ul>
    </div>
    <div class="cell">
      <strong>Organic:</strong>
      <ul>${(disease.organic_treatment || []).map(t => `<li>${t}</li>`).join('')}</ul>
    </div>
  </div>

  <h2>🧬 Fertilizer Dosage & Commercial Bags</h2>
  <table>
    <tr><th>Fertilizer</th><th>Deficit (kg/ha)</th><th>Standard 50kg Bags</th><th>Approx Subsidized Cost</th></tr>
    <tr><td>Urea</td><td>${fert.fertilizers.Urea} kg</td><td>${Math.ceil(fert.fertilizers.Urea / 50)} bags</td><td>₹${Math.ceil(fert.fertilizers.Urea / 50) * 267}</td></tr>
    <tr><td>DAP</td><td>${fert.fertilizers.DAP} kg</td><td>${Math.ceil(fert.fertilizers.DAP / 50)} bags</td><td>₹${Math.ceil(fert.fertilizers.DAP / 50) * 1350}</td></tr>
    <tr><td>MOP</td><td>${fert.fertilizers.MOP} kg</td><td>${Math.ceil(fert.fertilizers.MOP / 50)} bags</td><td>₹${Math.ceil(fert.fertilizers.MOP / 50) * 1700}</td></tr>
  </table>

  ${isPmfby ? `
  <div class="sign-row">
    <div class="sign-box">Signature of Insured Farmer</div>
    <div class="sign-box">Talathi / Village Agri Officer</div>
    <div class="sign-box">Insurance Surveyor (PMFBY)</div>
  </div>
  ` : ''}

  <div class="footer">
    AeroCrop.ai — Precision Agriculture Platform &bull; Certified under ICAR nutrient guidelines.
  </div>
</body></html>`;

  const win = window.open('', '_blank');
  if (win) {
    win.document.write(html);
    win.document.close();
    win.focus();
    setTimeout(() => { win.print(); }, 250);
  }
};

/* ══════════════════════════════════════════════════════════════════════════
   LOADING & NOTIFICATIONS
══════════════════════════════════════════════════════════════════════════ */
function setLoading(on) {
  state.isLoading = on;
  els.analyzeBtn.disabled  = on;
  els.btnText.textContent  = on ? 'Analyzing…' : (I18N[currentLang]?.analyze_btn || 'Analyze Crop');
  if (on) {
    els.btnSpinner.classList.remove('hidden');
    els.btnIcon.classList.add('hidden');
  } else {
    els.btnSpinner.classList.add('hidden');
    els.btnIcon.classList.remove('hidden');
  }
}

function showToast(msg, type = 'info') {
  document.querySelectorAll('.toast').forEach(t => t.remove());

  const colors = { success: 'var(--accent-green)', error: 'var(--accent-red)', warning: 'var(--accent-amber)', info: 'var(--accent-cyan)' };
  const icons  = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.innerHTML = `<span>${icons[type] || ''}</span><span>${msg}</span>`;
  Object.assign(toast.style, {
    position: 'fixed', bottom: '24px', right: '24px', zIndex: '99999',
    background: 'rgba(13,26,32,0.95)', border: `1px solid ${colors[type] || colors.info}`,
    borderRadius: '10px', padding: '12px 20px', display: 'flex', gap: '10px',
    alignItems: 'center', color: colors[type] || colors.info,
    fontFamily: 'Inter, sans-serif', fontSize: '0.88rem', fontWeight: '500',
    backdropFilter: 'blur(12px)', boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
    animation: 'slide-up 0.3s ease',
  });

  if (!document.head.querySelector('style[data-toast]')) {
    const s = document.createElement('style');
    s.setAttribute('data-toast', '1');
    s.textContent = '@keyframes slide-up { from { opacity:0; transform: translateY(16px); } to { opacity:1; transform:none; } }';
    document.head.appendChild(s);
  }

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
  initPlotSelectorSync();
  await loadDistricts();
  await checkAuthStatus();

  els.districtSelect.addEventListener('change', e => {
    fetchWeather(e.target.value);
  });
});
