import React, { useState } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { createFarmerPlot } from '../../api/plots';

interface AddPlotModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const AddPlotModal: React.FC<AddPlotModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const { t } = useI18n();
  const { showToast } = useToast();
  const { refreshPlots } = useAuth();

  const [plotName, setPlotName] = useState('');
  const [cropType, setCropType] = useState('cotton');
  const [areaAcres, setAreaAcres] = useState(2.5);
  const [soilType, setSoilType] = useState('Medium Black');
  const [sowingDate, setSowingDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!plotName.trim()) {
      showToast('Please provide a field/plot identifier name.', 'warning');
      return;
    }

    setIsSubmitting(true);
    try {
      await createFarmerPlot({
        plot_name: plotName.trim(),
        crop_type: cropType,
        area_acres: areaAcres,
        soil_type: soilType,
        sowing_date: sowingDate || null,
      });

      showToast(`Plot '${plotName}' registered successfully!`, 'success');
      await refreshPlots();
      onSuccess();
      onClose();

      // Reset form
      setPlotName('');
      setCropType('cotton');
      setAreaAcres(2.5);
      setSoilType('Medium Black');
      setSowingDate('');
    } catch (err: any) {
      showToast(`Could not register plot: ${err.message}`, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="plot-modal-title">
      <div className="modal-card glass">
        <button className="modal-close" onClick={onClose} aria-label="Close modal">
          ✕
        </button>

        <h2 id="plot-modal-title" className="card-title">
          🌱 <span>{t('register_plot_title')}</span>
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="modal-plot-name">{t('plot_name_label')}</label>
            <input
              id="modal-plot-name"
              type="text"
              required
              placeholder="e.g. North Canal Plot, Gat No. 42"
              value={plotName}
              onChange={(e) => setPlotName(e.target.value)}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="modal-plot-crop">{t('crop_type')}</label>
              <select
                id="modal-plot-crop"
                value={cropType}
                onChange={(e) => setCropType(e.target.value)}
                required
              >
                <option value="cotton">🌱 Cotton</option>
                <option value="wheat">🌾 Wheat</option>
                <option value="maize">🌽 Maize</option>
                <option value="rice">🍚 Rice</option>
                <option value="potato">🥔 Potato</option>
                <option value="tomato">🍅 Tomato</option>
                <option value="pepper">🌶️ Pepper (Bell)</option>
                <option value="apple">🍎 Apple</option>
                <option value="grape">🍇 Grape</option>
                <option value="orange">🍊 Orange</option>
                <option value="strawberry">🍓 Strawberry</option>
                <option value="soybean">🫘 Soybean</option>
                <option value="peach">🍑 Peach</option>
                <option value="cherry">🍒 Cherry</option>
                <option value="blueberry">🫐 Blueberry</option>
                <option value="squash">🎃 Squash</option>
                <option value="raspberry">🫐 Raspberry</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="modal-plot-acres">{t('area_acres_label')}</label>
              <input
                id="modal-plot-acres"
                type="number"
                required
                min={0.1}
                step={0.1}
                value={areaAcres}
                onChange={(e) => setAreaAcres(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="modal-plot-soil">{t('soil_type_label')}</label>
              <select
                id="modal-plot-soil"
                value={soilType}
                onChange={(e) => setSoilType(e.target.value)}
              >
                <option value="Medium Black">Medium Black Soil (काळी माती)</option>
                <option value="Deep Black (Regur)">Deep Black / Regur (काळी कसदार)</option>
                <option value="Alluvial">Alluvial (गाळाची माती)</option>
                <option value="Red Sandy Loam">Red Sandy Loam (तांबडी माती)</option>
                <option value="Laterite">Laterite (जांभी माती)</option>
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="modal-plot-sowing">{t('sowing_date_label')}</label>
              <input
                id="modal-plot-sowing"
                type="date"
                value={sowingDate}
                onChange={(e) => setSowingDate(e.target.value)}
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-full mt-2"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <span className="btn-spinner" />
            ) : (
              <span className="btn-text">{t('save_plot_btn')}</span>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
