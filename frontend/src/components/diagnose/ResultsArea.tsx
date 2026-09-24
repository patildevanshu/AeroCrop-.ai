import React, { useState } from 'react';
import { PredictionResult } from '../../types';
import { useI18n } from '../../context/I18nContext';
import { MetricCards } from './MetricCards';
import { TreatmentCard } from './TreatmentCard';
import { MandiCard } from './MandiCard';
import { EmailReportModal } from './EmailReportModal';

interface ResultsAreaProps {
  result: PredictionResult;
}

export const ResultsArea: React.FC<ResultsAreaProps> = ({ result }) => {
  const { language, t } = useI18n();
  const { mock_mode, low_confidence, saved_record_id, disease, weather, mandi } = result;

  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);

  const isOod = Boolean(result.out_of_distribution || disease?.name?.includes('No Match'));

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
      {mock_mode && !isOod && (
        <div className="mock-banner" role="alert">
          <span aria-hidden="true">⚡</span>
          <span>{t('mock_mode_notice')}</span>
        </div>
      )}

      {/* Saved to History Badge */}
      {saved_record_id && !isOod && (
        <div className="saved-history-banner" role="status">
          <span aria-hidden="true">💾</span>
          <span>{t('saved_records_notice')}</span>
        </div>
      )}

      {/* Smart Spraying Window Weather Advisory Banner (Always relevant for farmer's district) */}
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

      {/* Out of Distribution / Unrecognized Specimen: Formal Notice Banner */}
      {isOod && (
        <div
          className="ood-formal-notice-banner"
          role="alert"
          style={{
            background: 'linear-gradient(135deg, rgba(254, 243, 199, 0.95) 0%, rgba(255, 251, 235, 0.98) 100%)',
            border: '1.5px solid rgba(245, 158, 11, 0.5)',
            borderRadius: '12px',
            padding: '14px 18px',
            marginBottom: '18px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px',
            boxShadow: '0 4px 12px rgba(245, 158, 11, 0.1)',
          }}
        >
          <span style={{ fontSize: '1.5rem', lineHeight: 1 }} aria-hidden="true">⚠️</span>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '4px' }}>
              <strong style={{ fontSize: '0.98rem', color: '#92400e', fontWeight: 700 }}>
                {language === 'mr'
                  ? 'सूचना: नमुना डेटासेटमध्ये उपलब्ध नाही (मॉडेलचा जवळचा अंदाज)'
                  : (language === 'hi'
                    ? 'सूचना: नमूना डेटासेट में उपलब्ध नहीं (मॉडल का निकटतम अनुमान)'
                    : 'Notice: Specimen May Not Be in Trained Dataset (Closest Model Match)')}
              </strong>
              <span
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: '12px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  color: '#b91c1c',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                }}
              >
                Confidence &lt; 50%
              </span>
              <span
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  padding: '2px 8px',
                  borderRadius: '12px',
                  background: 'rgba(245, 158, 11, 0.2)',
                  color: '#b45309',
                  border: '1px solid rgba(245, 158, 11, 0.35)',
                }}
              >
                134-Class Dataset
              </span>
            </div>
            <p style={{ margin: 0, fontSize: '0.86rem', color: '#78350f', lineHeight: 1.5 }}>
              {result.ood_reason || (language === 'mr'
                ? 'हा वनस्पतीच्या पानाचा नमुना आमच्या १३४-रोग डेटासेटमध्ये समाविष्ट नसू शकतो (याची हमी नाही). खाली दर्शविलेले रोग निदान, औषधोपचार आणि उत्पादन हे AI मॉडेलचे सर्वात जवळचे वर्गीकरण आहे.'
                : (language === 'hi'
                  ? 'यह पत्ती नमूना हमारे 134-रोग डेटासेट में शामिल नहीं हो सकता है (इसकी गारंटी नहीं है)। नीचे दर्शाया गया रोग निदान, उपचार एवं उत्पादन AI मॉडल का निकटतम वर्गीकरण है।'
                  : 'This plant or disease specimen may not be present in our dataset (this is not guaranteed). The diagnosis below is based on our internal model\'s closest estimate.'))}
            </p>
          </div>
        </div>
      )}

      {/* Low Confidence Notice for supported crops with blurry/unclear leaves */}
      {low_confidence && !isOod && (
        <div className="low-conf-banner" role="alert">
          <span aria-hidden="true">⚠️</span>
          <span>{t('low_confidence_notice')}</span>
        </div>
      )}

          {/* Action Bar: Create Report & Send to Email Button */}
          <div
            className="report-email-action-bar"
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '14px',
              marginBottom: '20px',
              background: 'linear-gradient(135deg, rgba(240, 253, 244, 0.95) 0%, rgba(255, 255, 255, 0.98) 100%)',
              border: '1.5px solid rgba(16, 185, 129, 0.35)',
              borderRadius: '14px',
              padding: '14px 20px',
              boxShadow: '0 4px 16px rgba(16, 185, 129, 0.08)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  fontSize: '1.25rem',
                  boxShadow: '0 4px 10px rgba(16, 185, 129, 0.25)',
                }}
              >
                📄
              </div>
              <div>
                <strong style={{ fontSize: '0.98rem', color: '#166534', display: 'block', fontWeight: 700 }}>
                  {language === 'mr'
                    ? 'सविस्तर कृषी सल्लागार अहवाल (Trilingual Advisory PDF)'
                    : (language === 'hi' ? 'विस्तृत कृषि परामर्श रिपोर्ट (Trilingual Advisory PDF)' : 'Comprehensive Crop Advisory PDF')}
                </strong>
                <span style={{ fontSize: '0.82rem', color: '#475569' }}>
                  {language === 'mr'
                    ? 'मराठी, हिंदी व इंग्रजीमधील संपूर्ण फवारणी व खत व्यवस्थापन अहवाल'
                    : (language === 'hi'
                      ? 'मराठी, हिंदी एवं अंग्रेजी में संपूर्ण छिड़काव व उर्वरक प्रबंधन रिपोर्ट'
                      : '3-Page trilingual report with chemical dosages, organic remedies, and weather window')}
                </span>
              </div>
            </div>

            <button
              type="button"
              className="btn btn-primary"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 22px',
                fontSize: '0.92rem',
                fontWeight: 700,
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                boxShadow: '0 4px 14px rgba(5, 150, 105, 0.3)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
              onClick={() => setIsEmailModalOpen(true)}
            >
              <span>📩</span>
              <span>{t('btn_create_send_report')}</span>
            </button>
          </div>

          {/* Metric Cards Row */}
          <MetricCards result={result} />

          {/* Treatment Row */}
          <div style={{ marginBottom: '20px' }}>
            <TreatmentCard disease={disease} />
          </div>

          {/* Mandi Intelligence Card */}
          {mandi && <MandiCard mandi={mandi} />}

      {/* On-Demand Email Report Modal */}
      <EmailReportModal
        isOpen={isEmailModalOpen}
        result={result}
        onClose={() => setIsEmailModalOpen(false)}
      />
    </div>
  );
};


