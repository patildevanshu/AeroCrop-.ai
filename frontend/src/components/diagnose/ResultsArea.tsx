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
        <div className="ood-advisory-card" role="alert">
          <div className="ood-icon-box" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          </div>
          <div className="ood-body">
            <div className="ood-badge-row">
              <span className="ood-pill warning">
                <span aria-hidden="true">⚠️</span>
                <span>{language === 'mr' ? 'पडताळणी सूचना' : (language === 'hi' ? 'सत्यापन सूचना' : 'Validation Notice')}</span>
              </span>
              <span className="ood-pill internal">
                <span aria-hidden="true">⚡</span>
                <span>{language === 'mr' ? 'अंतर्गत मॉडेल सक्रिय' : (language === 'hi' ? 'आंतरिक मॉडल सक्रिय' : 'Internal Model Active')}</span>
              </span>
            </div>

            <h3 className="ood-title">
              {language === 'mr'
                ? 'वनस्पती किंवा रोग कदाचित डेटासेटमध्ये उपस्थित नसू शकतो'
                : (language === 'hi'
                  ? 'यह पौधा या रोग संभवतः डेटासेट में मौजूद नहीं हो सकता है'
                  : 'Specimen May Not Be in Trained Dataset')}
            </h3>

            <p className="ood-desc">
              {language === 'mr'
                ? 'आमच्या दुय्यम पडताळणीनुसार ही वनस्पती किंवा रोग आमच्या 134-रोग डेटासेटमध्ये उपस्थित नसू शकतो (याची कोणतीही खात्री नाही). आपल्या मार्गदर्शनासाठी खालील निदान आमच्या अंतर्गत न्यूरल मॉडेलच्या सर्वोत्तम संभाव्य अंदाजावर आधारित आहे.'
                : (language === 'hi'
                  ? 'सत्यापन के अनुसार यह पौधा या रोग हमारे 134-रोग डेटासेट में मौजूद नहीं हो सकता है (इसकी कोई गारंटी नहीं है)। आपकी सहायता के लिए नीचे दिया गया निदान हमारे आंतरिक न्यूरल मॉडल के सर्वोत्तम संभव अनुमान पर आधारित है।'
                  : 'Our secondary validator indicates this plant or disease specimen may not be present in our 134-class dataset (this is not guaranteed). To guide you, the diagnosis below is provided by our internal model as its closest agronomic estimate.')}
            </p>

            <div className="ood-tip-bar">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 16v-4" />
                <path d="M12 8h.01" />
              </svg>
              <span>
                {language === 'mr'
                  ? 'शेतकरी सल्ला: अचूक निदानासाठी, चांगल्या सूर्यप्रकाशात एकाच पानाचा स्वच्छ आणि स्पष्ट फोटो काढा.'
                  : (language === 'hi'
                    ? 'किसान सलाह: सटीक परिणाम के लिए, प्राकृतिक रोशनी में एक पत्ती का स्पष्ट और केंद्रित फोटो लें।'
                    : 'Farmer Tip: For highest diagnostic confidence, capture a sharp photo focused directly on leaf lesions in natural daylight.')}
              </span>
            </div>
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

