import React from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

interface ParamsCardProps {
  crop: string;
  setCrop: (crop: string) => void;
  district: string;
  setDistrict: (district: string) => void;
  districts: string[];
  selectedPlotId: string;
  setSelectedPlotId: (id: string) => void;
  soilN: number | '';
  setSoilN: (val: number | '') => void;
  soilP: number | '';
  setSoilP: (val: number | '') => void;
  soilK: number | '';
  setSoilK: (val: number | '') => void;
  farmerEmail: string;
  setFarmerEmail: (val: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
}

export const ParamsCard: React.FC<ParamsCardProps> = ({
  crop,
  setCrop,
  district,
  setDistrict,
  districts,
  selectedPlotId,
  setSelectedPlotId,
  soilN,
  setSoilN,
  soilP,
  setSoilP,
  soilK,
  setSoilK,
  farmerEmail,
  setFarmerEmail,
  onAnalyze,
  isLoading,
}) => {
  const { t } = useI18n();
  const { userPlots, isAuthenticated } = useAuth();
  const { showToast } = useToast();

  const handlePlotSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const plotIdStr = e.target.value;
    setSelectedPlotId(plotIdStr);

    if (plotIdStr) {
      const plot = userPlots.find((p) => p.id === parseInt(plotIdStr, 10));
      if (plot) {
        setCrop(plot.crop_type);
        if (plot.baseline_N != null) setSoilN(plot.baseline_N);
        if (plot.baseline_P != null) setSoilP(plot.baseline_P);
        if (plot.baseline_K != null) setSoilK(plot.baseline_K);
        showToast(`Linked to ${plot.plot_name} (${plot.crop_type}) — NPK baselines loaded`, 'info');
      }
    }
  };

  return (
    <div className="card glass params-card">
      <h2 className="card-title">
        <span aria-hidden="true">🌱</span>
        <span>{t('params_title')}</span>
      </h2>

      {/* Plot Quick-Selector for logged-in farmers */}
      {isAuthenticated && (
        <div className="form-group">
          <label htmlFor="plot-select">
            <span>{t('link_plot')}</span>
            <span className="badge-optional">{t('optional')}</span>
          </label>
          <select
            id="plot-select"
            value={selectedPlotId}
            onChange={handlePlotSelectChange}
            aria-label="Select farm plot"
          >
            <option value="">{t('no_plot_linked')}</option>
            {userPlots.map((p) => (
              <option key={p.id} value={p.id.toString()}>
                📍 {p.plot_name} ({p.crop_type.toUpperCase()} — {p.area_acres} Acres)
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Crop Selector */}
      <div className="form-group">
        <label htmlFor="crop-select">{t('crop_type')}</label>
        <select
          id="crop-select"
          value={crop}
          onChange={(e) => setCrop(e.target.value)}
          aria-label="Select crop type"
        >
          <option value="auto">{t('crop_auto_detect')}</option>
          <optgroup label={t('cash_crops_group', 'Crops')}>
            <option value="cotton">🌱 Cotton (कापूस / कपास)</option>
            <option value="sugarcane">🎋 Sugarcane (ऊस / गन्ना)</option>
            <option value="banana">🍌 Banana (केळी / केला)</option>
            <option value="turmeric">🌿 Turmeric / Haldi (हळद / हल्दी)</option>
            <option value="soybean">🌱 Soybean (सोयाबीन)</option>
            <option value="maize">🌽 Corn / Maize (मका / मक्का)</option>
            <option value="rice">🌾 Rice / Paddy (भात / धान)</option>
            <option value="potato">🥔 Potato (बटाटा / आलू)</option>
            <option value="wheat">🌾 Wheat (गहू / गेहूं)</option>
            <option value="tomato">🍅 Tomato (टोमॅटो / टमाटर)</option>
            <option value="orange">🍊 Orange / Citrus (संत्रे / संतरा)</option>
          </optgroup>
        </select>
      </div>

      {/* District Selector */}
      <div className="form-group">
        <label htmlFor="district-select">{t('district')}</label>
        <select
          id="district-select"
          value={district}
          onChange={(e) => setDistrict(e.target.value)}
          aria-label="Select district"
        >
          {districts.map((d) => (
            <option key={d} value={d}>
              {d.charAt(0).toUpperCase() + d.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Precision Soil Test NPK (Optional) */}
      <div className="form-group" style={{ marginBottom: '0.85rem' }}>
        <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>🧪 Soil Test N-P-K (kg/ha)</span>
          <span className="badge-optional">{t('optional', 'Optional')}</span>
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
          <div>
            <input
              type="number"
              placeholder="N (kg/ha)"
              min={0}
              value={soilN}
              onChange={(e) => setSoilN(e.target.value === '' ? '' : Number(e.target.value))}
              aria-label="Soil Nitrogen in kg/ha"
              style={{ fontSize: '0.85rem', padding: '6px 8px' }}
            />
          </div>
          <div>
            <input
              type="number"
              placeholder="P (kg/ha)"
              min={0}
              value={soilP}
              onChange={(e) => setSoilP(e.target.value === '' ? '' : Number(e.target.value))}
              aria-label="Soil Phosphorus in kg/ha"
              style={{ fontSize: '0.85rem', padding: '6px 8px' }}
            />
          </div>
          <div>
            <input
              type="number"
              placeholder="K (kg/ha)"
              min={0}
              value={soilK}
              onChange={(e) => setSoilK(e.target.value === '' ? '' : Number(e.target.value))}
              aria-label="Soil Potassium in kg/ha"
              style={{ fontSize: '0.85rem', padding: '6px 8px' }}
            />
          </div>
        </div>
        <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', margin: '4px 0 0' }}>
          Auto-filled from plot baseline or enter laboratory soil report values.
        </p>
      </div>

      {/* Optional Email for Direct PDF Report */}
      <div className="form-group" style={{ marginBottom: '0.75rem' }}>
        <label htmlFor="farmer-email" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>📧 {t('email_optional') || 'Email (for PDF Report)'}</span>
          <span className="optional-tag" style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{t('optional')}</span>
        </label>
        <input
          id="farmer-email"
          type="email"
          placeholder="e.g. farmer@example.com"
          value={farmerEmail}
          onChange={(e) => setFarmerEmail(e.target.value)}
          style={{ fontSize: '0.85rem' }}
        />
      </div>

      {/* Instant Agronomic Guidance Notice */}
      <div style={{
        padding: '0.65rem 0.85rem',
        borderRadius: '6px',
        background: 'rgba(16, 185, 129, 0.08)',
        border: '1px solid rgba(16, 185, 129, 0.25)',
        fontSize: '0.82rem',
        color: 'var(--text-secondary)',
        margin: '0.75rem 0 1.25rem 0',
        lineHeight: 1.4
      }}>
        ✨ {t('photo_first_notice')}
      </div>

      {/* Analyze Button */}
      <button
        id="analyze-btn"
        className="btn btn-primary"
        onClick={onAnalyze}
        disabled={isLoading}
        aria-label="Analyze crop"
      >
        {isLoading ? (
          <>
            <span className="btn-spinner" aria-hidden="true" />
            <span className="btn-text">{t('analyzing_btn')}</span>
          </>
        ) : (
          <>
            <span className="btn-icon" aria-hidden="true">🚀</span>
            <span className="btn-text">{t('analyze_btn')}</span>
          </>
        )}
      </button>
    </div>
  );
};
