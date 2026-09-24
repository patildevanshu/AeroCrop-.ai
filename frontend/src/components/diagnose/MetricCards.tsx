import React from 'react';
import { PredictionResult } from '../../types';
import { useI18n } from '../../context/I18nContext';
import { formatAgronomicYield } from '../../utils/yield';

interface MetricCardsProps {
  result: PredictionResult;
}

export const MetricCards: React.FC<MetricCardsProps> = ({ result }) => {
  const { t } = useI18n();
  const { disease, yield_t_ha, crop } = result;
  const yieldInfo = formatAgronomicYield(crop, yield_t_ha, result);

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
          <p className="metric-sub">{t('crop_label')}: {disease.crop}</p>
        </div>
      </div>

      {/* Confidence Card */}
      <div className="metric-card glass">
        <div className="metric-icon" aria-hidden="true">🎯</div>
        <div className="metric-body">
          <p className="metric-label">{t('confidence')}</p>
          <p
            className="metric-value"
            style={disease.confidence < 40 ? { color: '#d97706' } : undefined}
          >
            {disease.confidence.toFixed(1)}%
          </p>
          <div className="confidence-bar" aria-hidden="true">
            <div
              className="confidence-fill"
              style={{
                width: `${Math.min(disease.confidence, 100)}%`,
                background: disease.confidence < 40 ? 'linear-gradient(90deg, #f59e0b, #ef4444)' : undefined,
              }}
            />
          </div>
          <p
            className="metric-sub"
            style={{
              fontSize: '0.72rem',
              color: disease.confidence < 40 ? '#b45309' : 'var(--text-secondary)',
              marginTop: '4px',
              fontWeight: disease.confidence < 40 ? 600 : 400,
            }}
          >
            {disease.confidence < 40
              ? '⚠️ Low certainty (<40%): Specimen may not be in dataset'
              : t('confidence_desc', 'Certainty score for detected disease')}
          </p>
        </div>
      </div>

      {/* Yield Card */}
      <div className="metric-card glass" title={result.yield_reason || undefined}>
        <div className="metric-icon" aria-hidden="true">🌾</div>
        <div className="metric-body">
          <p className="metric-label">{t('predicted_yield')}</p>
          <p className="metric-value">{yieldInfo.primary}</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '3px', marginTop: '4px' }}>
            <span style={{ fontSize: '0.73rem', color: 'var(--text-secondary)' }}>
              {yieldInfo.secondary}
            </span>
            <span
              style={{
                fontSize: '0.70rem',
                fontWeight: 600,
                color: '#15803d',
                background: 'rgba(34,197,94,0.1)',
                padding: '2px 6px',
                borderRadius: '4px',
                display: 'inline-block',
                width: 'fit-content',
              }}
            >
              📊 {yieldInfo.benchmark}
            </span>
            {yieldInfo.categoryLabel && (
              <span style={{ fontSize: '0.70rem', opacity: 0.85 }}>
                {yieldInfo.categoryLabel}
              </span>
            )}
            {yieldInfo.lossImpactText && (
              <span style={{ fontSize: '0.72rem', color: '#b45309', fontWeight: 600 }}>
                {yieldInfo.lossImpactText}
              </span>
            )}
          </div>
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
            {disease.is_healthy ? `✅ ${t('healthy_status')}` : `⚠️ ${t('diseased_status')}`}
          </p>
        </div>
      </div>
    </div>
  );
};
