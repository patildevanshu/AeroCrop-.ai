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

const SUPPORTED_CROPS = [
  { icon: '🍅', en: 'Tomato', mr: 'टोमॅटो', hi: 'टमाटर' },
  { icon: '🥔', en: 'Potato', mr: 'बटाटा', hi: 'आलू' },
  { icon: '🌿', en: 'Cotton', mr: 'कापूस', hi: 'कपास' },
  { icon: '🌾', en: 'Wheat', mr: 'गहू', hi: 'गेहूं' },
  { icon: '🎋', en: 'Sugarcane', mr: 'ऊस', hi: 'गन्ना' },
  { icon: '🫘', en: 'Soybean', mr: 'सोयाबीन', hi: 'सोयाबीन' },
  { icon: '🍌', en: 'Banana', mr: 'केळी', hi: 'केला' },
  { icon: '🌽', en: 'Maize / Corn', mr: 'मका', hi: 'मक्का' },
  { icon: '🍚', en: 'Rice / Paddy', mr: 'भात', hi: 'चावल' },
  { icon: '🧅', en: 'Onion', mr: 'कांदा', hi: 'प्याज' },
  { icon: '🌶️', en: 'Chili / Pepper', mr: 'मिरची', hi: 'मिर्च' },
  { icon: '🍊', en: 'Orange', mr: 'संत्रा', hi: 'संतरा' },
  { icon: '🍇', en: 'Grape', mr: 'द्राक्षे', hi: 'अंगूर' },
  { icon: '🍎', en: 'Apple', mr: 'सफरचंद', hi: 'सेब' },
  { icon: '🟡', en: 'Turmeric', mr: 'हळद', hi: 'हल्दी' },
];

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

  const handleRetryUpload = () => {
    const uploadElem = document.getElementById('upload-card') || document.querySelector('.upload-card');
    if (uploadElem) {
      uploadElem.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

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

      {/* Out of Distribution / Unrecognized Specimen: Dedicated No Match Display */}
      {isOod ? (
        <div className="ood-no-match-card" role="alert">
          <div className="ood-header-row">
            <div className="ood-header-icon" aria-hidden="true">
              🔍❌
            </div>
            <div className="ood-header-content">
              <div className="ood-badge-row">
                <span className="ood-pill warning">
                  <span aria-hidden="true">⚠️</span>
                  <span>{t('ood_no_match_badge')}</span>
                </span>
                <span className="ood-pill internal">
                  <span aria-hidden="true">🔬</span>
                  <span>
                    {language === 'mr'
                      ? '१३४-रोग डेटासेट तपासणी'
                      : (language === 'hi' ? '134-रोग डेटासेट जांच' : '134-Class Dataset Screened')}
                  </span>
                </span>
              </div>

              <h3 className="ood-main-title">{t('ood_no_match_title')}</h3>
              <p className="ood-main-desc">{t('ood_no_match_desc')}</p>
            </div>
          </div>

          {/* Supported Crops Badges */}
          <div className="ood-supported-section">
            <div className="ood-section-title">
              <span aria-hidden="true">🌾</span>
              <span>{t('ood_supported_crops_heading')}</span>
            </div>
            <div className="ood-crops-grid">
              {SUPPORTED_CROPS.map((c, idx) => (
                <div key={idx} className="ood-crop-chip">
                  <span aria-hidden="true">{c.icon}</span>
                  <span>
                    {language === 'mr' ? `${c.mr} (${c.en})` : (language === 'hi' ? `${c.hi} (${c.en})` : c.en)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Guidance / Tips Box */}
          <div className="ood-tips-section">
            <div className="ood-section-title">
              <span aria-hidden="true">💡</span>
              <span>{t('ood_how_to_capture_heading')}</span>
            </div>
            <ul className="ood-tips-list">
              <li>{t('ood_tip_1')}</li>
              <li>{t('ood_tip_2')}</li>
            </ul>
          </div>

          {/* Try Again Action Button */}
          <div className="ood-actions">
            <button
              type="button"
              className="btn-ood-retry"
              onClick={handleRetryUpload}
            >
              <span aria-hidden="true">🔄</span>
              <span>{t('ood_try_again_btn')}</span>
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Low Confidence Notice for supported crops with blurry/unclear leaves */}
          {low_confidence && (
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
        </>
      )}

      {/* On-Demand Email Report Modal */}
      <EmailReportModal
        isOpen={isEmailModalOpen}
        result={result}
        onClose={() => setIsEmailModalOpen(false)}
      />
    </div>
  );
};


