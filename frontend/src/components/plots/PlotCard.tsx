import React from 'react';
import { FarmPlot } from '../../types';
import { useI18n } from '../../context/I18nContext';

interface PlotCardProps {
  plot: FarmPlot;
  onQuickDiagnose: (plot: FarmPlot) => void;
  onDelete: (plotId: number) => void;
}

const CROP_ICONS: Record<string, string> = {
  cotton: '🌱',
  sugarcane: '🎋',
  banana: '🍌',
  turmeric: '🌿',
  haldi: '🌿',
  onion: '🧅',
  wheat: '🌾',
  maize: '🌽',
  rice: '🍚',
  potato: '🥔',
  tomato: '🍅',
  pepper: '🌶️',
  apple: '🍎',
  grape: '🍇',
  orange: '🍊',
  peach: '🍑',
  strawberry: '🍓',
  soybean: '🫘',
  cherry: '🍒',
  blueberry: '🫐',
  squash: '🎃',
  raspberry: '🫐',
};

export const PlotCard: React.FC<PlotCardProps> = ({ plot, onQuickDiagnose, onDelete }) => {
  const { t } = useI18n();
  const icon = CROP_ICONS[plot.crop_type.toLowerCase()] || '🌱';

  const healthScore = plot.health_score ?? (plot.latest_diagnosis ? (plot.latest_diagnosis.is_healthy ? 100 : 50) : null);
  const healthColor = healthScore != null ? (healthScore >= 80 ? 'var(--accent-green)' : healthScore >= 50 ? 'var(--accent-amber)' : 'var(--accent-red)') : 'inherit';

  const diagInfo = plot.latest_diagnosis ? (
    <span className="plot-stat-chip">
      {plot.latest_diagnosis.is_healthy ? `✅ ${t('healthy_status')}` : `⚠️ ${plot.latest_diagnosis.disease_name}`}
    </span>
  ) : (
    <span className="plot-stat-chip">{t('no_recent_diagnosis')}</span>
  );

  return (
    <div className="card glass plot-card">
      <div>
        <div className="plot-header">
          <h3 className="plot-title">{plot.plot_name}</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            {healthScore != null && (
              <span
                className="plot-stat-chip"
                style={{
                  borderColor: healthColor,
                  color: healthColor,
                  fontWeight: 600,
                  fontSize: '0.72rem',
                }}
              >
                💚 {healthScore}% Health
              </span>
            )}
            <span className="plot-crop-badge">
              {icon} {plot.crop_type.toUpperCase()}
            </span>
          </div>
        </div>
        <p className="plot-meta mt-2">
          <strong>{t('area_label')}</strong> {plot.area_acres} {t('unit_acre')} · <strong>{t('soil_label')}</strong> {plot.soil_type}<br />
          <strong>{t('baseline_npk')}</strong> {plot.baseline_N}-{plot.baseline_P}-{plot.baseline_K} kg/ha
        </p>
        <div className="plot-stats-row mt-2">
          <span className="plot-stat-chip">📊 {plot.total_diagnoses} {t('analyses_count')}</span>
          {diagInfo}
        </div>

        {plot.recent_analyses && plot.recent_analyses.length > 0 && (
          <div className="plot-recent-progression mt-2">
            <span className="plot-progression-title">Progression ({plot.recent_analyses.length} analyses):</span>
            <div className="plot-progression-chips">
              {plot.recent_analyses.map((a, idx) => (
                <span
                  key={a.id || idx}
                  className={`plot-mini-chip ${a.is_healthy ? 'chip-healthy' : 'chip-disease'}`}
                  title={`${a.disease_name} (${a.confidence}% conf, ${a.predicted_yield_t_ha} t/ha)`}
                >
                  #{idx + 1} {a.is_healthy ? '✅' : '🦠'} {a.predicted_yield_t_ha} t/ha
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="plot-actions">
        <button
          type="button"
          className="btn btn-primary btn-sm btn-full"
          onClick={() => onQuickDiagnose(plot)}
        >
          {t('quick_diagnose')}
        </button>
        <button
          type="button"
          className="btn-icon-sm"
          onClick={() => onDelete(plot.id)}
          title={t('delete_plot')}
          aria-label={t('delete_plot')}
        >
          🗑️
        </button>
      </div>
    </div>
  );
};
