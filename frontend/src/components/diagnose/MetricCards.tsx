import React from 'react';
import { PredictionResult } from '../../types';
import { useI18n } from '../../context/I18nContext';

interface MetricCardsProps {
  result: PredictionResult;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ result }) => {
  const { t } = useI18n();
  const { disease, yield_t_ha, crop } = result;

  const getSeverityBorderColor = (sev: string) => {
    switch (sev) {
      case 'None':
        return 'rgba(34,197,94,0.4)';
      case 'Low':
        return 'rgba(132,204,22,0.4)';
      case 'Moderate':
        return 'rgba(245,158,11,0.4)';
      case 'High':
        return 'rgba(239,68,68,0.4)';
      case 'Critical':
        return 'rgba(168,85,247,0.5)';
      default:
        return 'rgba(148,163,184,0.3)';
    }
  };

  return (
    <div className="metrics-row">
      {/* Disease Card */}
      <div className="metric-card glass">
        <div className="metric-icon" aria-hidden="true">🦠</div>
        <div className="metric-body">
          <p className="metric-label">{t('detected_disease')}</p>
          <p className="metric-value">{disease.name}</p>
          <p className="metric-sub">Crop: {disease.crop}</p>
        </div>
      </div>

      {/* Confidence Card */}
      <div className="metric-card glass">
        <div className="metric-icon" aria-hidden="true">🎯</div>
        <div className="metric-body">
          <p className="metric-label">{t('confidence')}</p>
          <p className="metric-value">{disease.confidence.toFixed(1)}%</p>
          <div className="confidence-bar" aria-hidden="true">
            <div
              className="confidence-fill"
              style={{ width: `${Math.min(disease.confidence, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Yield Card */}
      <div className="metric-card glass">
        <div className="metric-icon" aria-hidden="true">🌾</div>
        <div className="metric-body">
          <p className="metric-label">{t('predicted_yield')}</p>
          <p className="metric-value">{yield_t_ha} t/ha</p>
          <p className="metric-sub">For {crop}</p>
        </div>
      </div>

      {/* Severity Card */}
      <div
        className="metric-card glass"
        style={{ borderColor: getSeverityBorderColor(disease.severity) }}
      >
        <div className="metric-icon" aria-hidden="true">⚠️</div>
        <div className="metric-body">
          <p className="metric-label">{t('severity')}</p>
          <p className="metric-value">{disease.severity || 'None'}</p>
          <p className="metric-sub">
            {disease.is_healthy ? '✅ Healthy' : '⚠️ Diseased'}
          </p>
        </div>
      </div>
    </div>
  );
};
