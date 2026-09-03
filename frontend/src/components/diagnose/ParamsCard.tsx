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
  N: number;
  setN: (n: number) => void;
  P: number;
  setP: (p: number) => void;
  K: number;
  setK: (k: number) => void;
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
  N,
  setN,
  P,
  setP,
  K,
  setK,
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
        setN(plot.baseline_N);
        setP(plot.baseline_P);
        setK(plot.baseline_K);
        showToast(`Linked to ${plot.plot_name} (${plot.crop_type})`, 'info');
      }
    }
  };

  return (
    <div className="card glass params-card">
      <h2 className="card-title">
        <span aria-hidden="true">🧪</span>
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
            <option value="cotton">🌱 Cotton</option>
            <option value="wheat">🌾 Wheat</option>
            <option value="maize">🌽 Maize</option>
            <option value="rice">🍚 Rice</option>
            <option value="potato">🥔 Potato</option>
            <option value="soybean">🫘 Soybean</option>
          </optgroup>
          <optgroup label="── Vegetables ──">
            <option value="tomato">🍅 Tomato</option>
            <option value="pepper">🌶️ Pepper (Bell)</option>
            <option value="squash">🎃 Squash</option>
          </optgroup>
          <optgroup label="── Fruits ──">
            <option value="apple">🍎 Apple</option>
            <option value="grape">🍇 Grape</option>
            <option value="orange">🍊 Orange</option>
            <option value="peach">🍑 Peach</option>
            <option value="strawberry">🍓 Strawberry</option>
            <option value="cherry">🍒 Cherry</option>
            <option value="blueberry">🫐 Blueberry</option>
            <option value="raspberry">🫐 Raspberry</option>
          </optgroup>
        </select>
      </div>

      {/* Maharashtra District Selector */}
      <div className="form-group">
        <label htmlFor="district-select">{t('district_label')}</label>
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

      {/* Soil Macronutrients NPK */}
      <div className="npk-grid">
        <div className="form-group">
          <label htmlFor="input-N">
            <span>{t('nitrogen')}</span>
            <span className="unit">kg/ha</span>
          </label>
          <input
            id="input-N"
            type="number"
            min={0}
            max={300}
            step={1}
            value={N}
            onChange={(e) => setN(Number(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label htmlFor="input-P">
            <span>{t('phosphorus')}</span>
            <span className="unit">kg/ha</span>
          </label>
          <input
            id="input-P"
            type="number"
            min={0}
            max={200}
            step={1}
            value={P}
            onChange={(e) => setP(Number(e.target.value))}
          />
        </div>
        <div className="form-group">
          <label htmlFor="input-K">
            <span>{t('potassium')}</span>
            <span className="unit">kg/ha</span>
          </label>
          <input
            id="input-K"
            type="number"
            min={0}
            max={200}
            step={1}
            value={K}
            onChange={(e) => setK(Number(e.target.value))}
          />
        </div>
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
