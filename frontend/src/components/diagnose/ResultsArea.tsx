import React from 'react';
import { PredictionResult } from '../../types';
import { useI18n } from '../../context/I18nContext';
import { MetricCards } from './MetricCards';
import { TreatmentCard } from './TreatmentCard';
import { MandiCard } from './MandiCard';

interface ResultsAreaProps {
  result: PredictionResult;
}

export const ResultsArea: React.FC<ResultsAreaProps> = ({ result }) => {
  const { language, t } = useI18n();
  const { mock_mode, low_confidence, saved_record_id, disease, weather, mandi } = result;

  const sprayWindow = weather?.spray_window;
  const sprayReason = sprayWindow
    ? (language === 'mr' ? sprayWindow.reason_mr : (language === 'hi' ? sprayWindow.reason_hi : sprayWindow.reason))
    : '';
  const sprayBadgeLocalized = sprayWindow
    ? (sprayWindow.safe ? t('spray_safe') : (sprayWindow.status === 'warning' ? t('spray_caution') : t('spray_hold')))
    : '';

  return (
    <div id="results-area" className="results-area" aria-live="polite" aria-label="Analysis results">
      {/* Mock Mode Banner */}
      {mock_mode && (
        <div className="mock-banner" role="alert">
          <span aria-hidden="true">⚡</span>
          <span>{t('mock_mode_notice')}</span>
        </div>
      )}

      {/* Saved to History Badge */}
      {saved_record_id && (
        <div className="saved-history-banner" role="status">
          <span aria-hidden="true">💾</span>
          <span>{t('saved_records_notice')}</span>
        </div>
      )}

      {/* Out of Distribution / Unrecognized Specimen Advisory */}
      {result.out_of_distribution ? (
        <div
          className="low-conf-banner"
          role="alert"
          style={{
            padding: '1rem 1.25rem',
            borderRadius: '10px',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.85rem',
            background: 'rgba(245, 158, 11, 0.14)',
            border: '1px solid rgba(245, 158, 11, 0.45)',
          }}
        >
          <span style={{ fontSize: '1.5rem', flexShrink: 0 }}>⚠️</span>
          <div>
            <strong style={{ display: 'block', fontSize: '0.95rem', color: '#fbbf24', marginBottom: '3px' }}>
              {language === 'mr'
                ? 'मॉडेल सूचना — वनस्पती कदाचित डेटासेटमध्ये उपस्थित नसू शकते'
                : (language === 'hi'
                  ? 'मॉडल सलाह — यह पौधा संभवतः डेटासेट में मौजूद नहीं हो सकता है'
                  : 'Model Advisory — Specimen May Not Be in Dataset')}
            </strong>
            <span style={{ fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: '1.45' }}>
              {language === 'mr'
                ? 'अपलोड केलेली वनस्पती किंवा रोग आमच्या डेटासेटमध्ये उपस्थित नसू शकतो (याची कोणतीही खात्री नाही). खालील निकाल आमच्या अंतर्गत मॉडेलच्या अंदाजावर आधारित आहे. अचूकतेसाठी कृपया पानावरील स्पष्ट फोटो अपलोड करा.'
                : (language === 'hi'
                  ? 'यह पौधा या रोग हमारे डेटासेट में मौजूद नहीं हो सकता है (इसकी कोई गारंटी नहीं है)। नीचे दिया गया परिणाम हमारे आंतरिक मॉडल के सर्वोत्तम अनुमान पर आधारित है। कृपया स्पष्ट पत्ती की फोटो अपलोड करें।'
                  : 'This plant or disease specimen may not be present in our dataset (this is not guaranteed). The output below is based on our internal model\'s closest estimate. For best accuracy, please upload a clear, focused leaf photo.')}
            </span>
          </div>
        </div>
      ) : (
        low_confidence && (
          <div className="low-conf-banner" role="alert">
            <span aria-hidden="true">⚠️</span>
            <span>{t('low_confidence_notice')}</span>
          </div>
        )
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
              ? 'rgba(239, 68, 68, 0.12)'
              : (sprayWindow.status === 'warning' ? 'rgba(245, 158, 11, 0.12)' : 'rgba(16, 185, 129, 0.12)'),
          }}
        >
          <span style={{ fontSize: '1.4rem' }}>
            {sprayWindow.status === 'danger' ? '🚫' : (sprayWindow.status === 'warning' ? '⚠️' : '🎯')}
          </span>
          <div style={{ flex: 1 }}>
            <strong style={{
              display: 'block',
              fontSize: '0.95rem',
              color: sprayWindow.status === 'danger' ? '#b91c1c' : (sprayWindow.status === 'warning' ? '#b45309' : '#15803d')
            }}>
              {sprayBadgeLocalized || sprayWindow.badge}
            </strong>
            <span style={{ fontSize: '0.88rem', color: 'var(--text-primary)' }}>{sprayReason}</span>
          </div>
        </div>
      )}

      {/* Metric Cards Row */}
      <MetricCards result={result} />

      {/* Treatment Row */}
      <div style={{ marginBottom: '20px' }}>
        <TreatmentCard disease={disease} />
      </div>

      {/* Mandi Intelligence Card */}
      {mandi && <MandiCard mandi={mandi} />}
    </div>
  );
};

