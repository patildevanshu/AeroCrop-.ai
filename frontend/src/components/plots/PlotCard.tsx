import React from 'react';
import { FarmPlot } from '../../types';

interface PlotCardProps {
  plot: FarmPlot;
  onQuickDiagnose: (plot: FarmPlot) => void;
  onDelete: (plotId: number) => void;
}

const CROP_ICONS: Record<string, string> = {
  cotton: '🌱',
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
  const icon = CROP_ICONS[plot.crop_type.toLowerCase()] || '🌱';

  const diagInfo = plot.latest_diagnosis ? (
    <span className="plot-stat-chip">
      {plot.latest_diagnosis.is_healthy ? '✅ Healthy' : `⚠️ ${plot.latest_diagnosis.disease_name}`}
    </span>
  ) : (
    <span className="plot-stat-chip">No recent diagnosis</span>
  );

  return (
    <div className="card glass plot-card">
      <div>
        <div className="plot-header">
          <h3 className="plot-title">{plot.plot_name}</h3>
          <span className="plot-crop-badge">
            {icon} {plot.crop_type.toUpperCase()}
          </span>
        </div>
        <p className="plot-meta mt-2">
          <strong>Area:</strong> {plot.area_acres} Acres · <strong>Soil:</strong> {plot.soil_type}<br />
          <strong>Baseline NPK:</strong> {plot.baseline_N}-{plot.baseline_P}-{plot.baseline_K} kg/ha
        </p>
        <div className="plot-stats-row mt-2">
          <span className="plot-stat-chip">📊 {plot.total_diagnoses} Analyses</span>
          {diagInfo}
        </div>
      </div>

      <div className="plot-actions">
        <button
          type="button"
          className="btn btn-primary btn-sm btn-full"
          onClick={() => onQuickDiagnose(plot)}
        >
          🔬 Quick Diagnose
        </button>
        <button
          type="button"
          className="btn-icon-sm"
          onClick={() => onDelete(plot.id)}
          title="Delete plot"
          aria-label="Delete plot"
        >
          🗑️
        </button>
      </div>
    </div>
  );
};
