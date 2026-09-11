import React, { useState, useEffect } from 'react';
import { FarmPlot } from '../../types';
import { useI18n } from '../../context/I18nContext';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import { updateFarmerPlot } from '../../api/plots';

interface EditPlotModalProps {
  isOpen: boolean;
  plot: FarmPlot | null;
  onClose: () => void;
  onSuccess: () => void;
}

export const EditPlotModal: React.FC<EditPlotModalProps> = ({
  isOpen,
  plot,
  onClose,
  onSuccess,
}) => {
  const { t } = useI18n();
  const { showToast } = useToast();
  const { refreshPlots } = useAuth();

  const [plotName, setPlotName] = useState('');
  const [cropType, setCropType] = useState('tomato');
  const [areaAcres, setAreaAcres] = useState(2.5);
  const [soilType, setSoilType] = useState('Medium Black');
  const [sowingDate, setSowingDate] = useState('');
  const [baselineN, setBaselineN] = useState<number | ''>('');
  const [baselineP, setBaselineP] = useState<number | ''>('');
  const [baselineK, setBaselineK] = useState<number | ''>('');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (plot) {
      setPlotName(plot.plot_name || '');
      setCropType(plot.crop_type || 'tomato');
      setAreaAcres(plot.area_acres || 1.0);
      setSoilType(plot.soil_type || 'Medium Black');
      setSowingDate(plot.sowing_date ? plot.sowing_date.split('T')[0] : '');
      setBaselineN(plot.baseline_N ?? '');
      setBaselineP(plot.baseline_P ?? '');
      setBaselineK(plot.baseline_K ?? '');
      setNotes(plot.notes || '');
    }
  }, [plot]);

  if (!isOpen || !plot) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!plotName.trim()) {
      showToast('Please provide a field/plot identifier name.', 'warning');
      return;
    }

    setIsSubmitting(true);
    try {
      await updateFarmerPlot(plot.id, {
        plot_name: plotName.trim(),
        crop_type: cropType,
        area_acres: Number(areaAcres),
        soil_type: soilType,
        sowing_date: sowingDate || null,
        baseline_N: baselineN === '' ? null : Number(baselineN),
        baseline_P: baselineP === '' ? null : Number(baselineP),
        baseline_K: baselineK === '' ? null : Number(baselineK),
        notes: notes.trim() || null,
      });

      showToast(`Plot '${plotName}' updated successfully!`, 'success');
      await refreshPlots();
      onSuccess();
      onClose();
    } catch (err: any) {
      showToast(`Could not update plot: ${err.message}`, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="edit-plot-modal-title">
      <div className="modal-card glass" style={{ maxWidth: '560px', width: '90%' }}>
        <button className="modal-close" onClick={onClose} aria-label="Close modal">
          ✕
        </button>

        <h2 id="edit-plot-modal-title" className="card-title">
          ✏️ <span>{t('edit_plot_title', 'Edit Farm Plot')}</span>
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="edit-plot-name">{t('plot_name_label', 'Plot Name / Tag')}</label>
            <input
              id="edit-plot-name"
              type="text"
              required
              placeholder="e.g. North Canal Plot, Gat No. 42"
              value={plotName}
              onChange={(e) => setPlotName(e.target.value)}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="edit-plot-crop">{t('crop_type', 'Crop Type')}</label>
              <select
                id="edit-plot-crop"
                value={cropType}
                onChange={(e) => setCropType(e.target.value)}
                required
              >
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
            <div className="form-group">
              <label htmlFor="edit-plot-acres">{t('area_acres_label', 'Area (Acres)')}</label>
              <input
                id="edit-plot-acres"
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
              <label htmlFor="edit-plot-soil">{t('soil_type_label', 'Soil Classification')}</label>
              <select
                id="edit-plot-soil"
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
              <label htmlFor="edit-plot-sowing">{t('sowing_date_label', 'Sowing / Planting Date')}</label>
              <input
                id="edit-plot-sowing"
                type="date"
                value={sowingDate}
                onChange={(e) => setSowingDate(e.target.value)}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="edit-plot-n">Baseline N (kg/ha)</label>
              <input
                id="edit-plot-n"
                type="number"
                min={0}
                placeholder="e.g. 120"
                value={baselineN}
                onChange={(e) => setBaselineN(e.target.value === '' ? '' : Number(e.target.value))}
              />
            </div>
            <div className="form-group">
              <label htmlFor="edit-plot-p">Baseline P (kg/ha)</label>
              <input
                id="edit-plot-p"
                type="number"
                min={0}
                placeholder="e.g. 60"
                value={baselineP}
                onChange={(e) => setBaselineP(e.target.value === '' ? '' : Number(e.target.value))}
              />
            </div>
            <div className="form-group">
              <label htmlFor="edit-plot-k">Baseline K (kg/ha)</label>
              <input
                id="edit-plot-k"
                type="number"
                min={0}
                placeholder="e.g. 40"
                value={baselineK}
                onChange={(e) => setBaselineK(e.target.value === '' ? '' : Number(e.target.value))}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="edit-plot-notes">Notes / Irrigation Details</label>
            <textarea
              id="edit-plot-notes"
              rows={2}
              placeholder="e.g. Drip irrigation installed, organic compost applied last month"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 14px',
                borderRadius: '8px',
                border: '1px solid var(--glass-border)',
                background: 'var(--input-bg, rgba(255,255,255,0.7))',
                color: 'var(--text-primary)',
                fontFamily: 'inherit',
                fontSize: '0.9rem',
                resize: 'vertical',
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ flex: 1 }}
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ flex: 1 }}
              disabled={isSubmitting}
            >
              {isSubmitting ? <span className="btn-spinner" /> : <span className="btn-text">Save Changes</span>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
