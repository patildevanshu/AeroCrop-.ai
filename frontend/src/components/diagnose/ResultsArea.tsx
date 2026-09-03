import React from 'react';
import { PredictionResult } from '../../types';
import { useI18n } from '../../context/I18nContext';
import { MetricCards } from './MetricCards';
import { TreatmentCard } from './TreatmentCard';
import { FertilizerCard } from './FertilizerCard';
import { MandiCard } from './MandiCard';
import { NPKChart } from './NPKChart';

interface ResultsAreaProps {
  result: PredictionResult;
}

export const ResultsArea: React.FC<ResultsAreaProps> = ({ result }) => {
  const { language } = useI18n();
  const { mock_mode, low_confidence, saved_record_id, disease, fertilizer, weather, mandi } = result;

  const sprayWindow = weather?.spray_window;
  const sprayReason = sprayWindow
    ? (language === 'mr' ? sprayWindow.reason_mr : (language === 'hi' ? sprayWindow.reason_hi : sprayWindow.reason))
    : '';

  return (
    <div id="results-area" className="results-area" aria-live="polite" aria-label="Analysis results">
      {/* Mock Mode Banner */}
      {mock_mode && (
        <div className="mock-banner" role="alert">
          <span aria-hidden="true">⚡</span>
          <span>
            Running in <strong>Smart Mock Mode</strong> — results are agronomically derived estimates.
            Train and load neural weights for live neural inference.
          </span>
        </div>
      )}

      {/* Saved to History Badge */}
      {saved_record_id && (
        <div className="saved-history-banner" role="status">
          <span aria-hidden="true">💾</span>
          <span>
            <strong>Saved to Your Farm Records</strong> — Successfully linked to your farmer account history.
          </span>
        </div>
      )}

      {/* Low Confidence Warning */}
      {low_confidence && (
        <div className="low-conf-banner" role="alert">
          <span aria-hidden="true">⚠️</span>
          <span>
            <strong>Low Confidence</strong> — The model is uncertain about this leaf image. Ensure the leaf is clearly photographed against a neutral background.
          </span>
        </div>
      )}

      {/* Smart Spraying Window Weather Advisory Banner */}
      {sprayWindow && (
        <div
          className={`spray-window-banner ${sprayWindow.status}`}
          role="status"
          style={{
            padding: '0.85rem 1.15rem',
            borderRadius: '8px',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
            border: sprayWindow.status === 'danger'
              ? '1px solid rgba(239, 68, 68, 0.5)'
              : (sprayWindow.status === 'warning' ? '1px solid rgba(245, 158, 11, 0.5)' : '1px solid rgba(16, 185, 129, 0.5)'),
            background: sprayWindow.status === 'danger'
              ? 'rgba(239, 68, 68, 0.15)'
              : (sprayWindow.status === 'warning' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)'),
          }}
        >
          <span style={{ fontSize: '1.4rem' }}>
            {sprayWindow.status === 'danger' ? '🚫' : (sprayWindow.status === 'warning' ? '⚠️' : '🎯')}
          </span>
          <div style={{ flex: 1 }}>
            <strong style={{
              display: 'block',
              fontSize: '0.95rem',
              color: sprayWindow.status === 'danger' ? '#f87171' : (sprayWindow.status === 'warning' ? '#fbbf24' : '#34d399')
            }}>
              {sprayWindow.badge}
            </strong>
            <span style={{ fontSize: '0.88rem', color: '#e2e8f0' }}>{sprayReason}</span>
          </div>
        </div>
      )}

      {/* Metric Cards Row */}
      <MetricCards result={result} />

      {/* Treatment + Fertilizer Row */}
      <div className="detail-row">
        <TreatmentCard disease={disease} />
        <FertilizerCard result={result} />
      </div>

      {/* Mandi Intelligence Card */}
      {mandi && <MandiCard mandi={mandi} />}

      {/* NPK Chart */}
      <NPKChart fertilizer={fertilizer} />
    </div>
  );
};

