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
        showToast(`Linked to ${plot.plot_name} (${plot.crop_type})`, 'info');
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
            <option value="">-- No plot linked (General diagnosis) --</option>
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
          <optgroup label="── Primary Cash Crops ──">
            <option value="cotton">Cotton (कापूस)</option>
            <option value="soybean">Soybean (सोयाबीन)</option>
            <option value="wheat">Wheat (गहू)</option>
            <option value="maize">Maize (मका)</option>
            <option value="rice">Rice (भात / धान)</option>
            <option value="potato">Potato (बटाटा)</option>
            <option value="tomato">Tomato (टोमॅटो)</option>
            <option value="grape">Grape (द्राक्षे)</option>
            <option value="pepper">Pepper (मिरची)</option>
            <option value="apple">Apple (सफरचंद)</option>
          </optgroup>
          <optgroup label="── Other PlantVillage Crops ──">
            <option value="cherry">Cherry</option>
            <option value="corn">Corn</option>
            <option value="peach">Peach</option>
            <option value="strawberry">Strawberry</option>
            <option value="orange">Orange</option>
            <option value="squash">Squash</option>
            <option value="raspberry">Raspberry</option>
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

      {/* Instant Agronomic Guidance Notice */}
      <div style={{
        padding: '0.65rem 0.85rem',
        borderRadius: '6px',
        background: 'rgba(16, 185, 129, 0.08)',
        border: '1px solid rgba(16, 185, 129, 0.25)',
        fontSize: '0.82rem',
        color: '#94a3b8',
        margin: '0.75rem 0 1.25rem 0',
        lineHeight: 1.4
      }}>
        ✨ <strong style={{ color: '#34d399' }}>Photo-First Diagnosis:</strong> Standard ICAR nutrition dosages and live microclimatic weather telemetry will be automatically computed for your selected crop and district.
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
