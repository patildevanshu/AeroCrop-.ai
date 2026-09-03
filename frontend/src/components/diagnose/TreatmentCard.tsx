import React, { useState } from 'react';
import { DiseaseInfo } from '../../types';
import { useI18n } from '../../context/I18nContext';
import { speakText, stopSpeech } from '../../utils/speech';

interface TreatmentCardProps {
  disease: DiseaseInfo;
}

export const TreatmentCard: React.FC<TreatmentCardProps> = ({ disease }) => {
  const { t, language } = useI18n();
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const handleToggleVoice = () => {
    if (isPlayingAudio) {
      stopSpeech();
      setIsPlayingAudio(false);
      return;
    }

    const chem = (disease.chemical_treatment || []).join('. ');
    const org = (disease.organic_treatment || []).join('. ');

    let script = '';
    if (language === 'mr') {
      script = `पिकाचा रोग: ${disease.name}. ${disease.description}. रासायनिक उपाय: ${chem || 'काही नाही'}. सेंद्रिय उपाय: ${org || 'काही नाही'}.`;
    } else if (language === 'hi') {
      script = `फसल का रोग: ${disease.name}। ${disease.description}। रासायनिक उपचार: ${chem || 'कोई नहीं'}। जैविक उपाय: ${org || 'कोई नहीं'}।`;
    } else {
      script = `Crop Disease: ${disease.name}. ${disease.description}. Chemical treatment: ${chem || 'None'}. Organic treatment: ${org || 'None'}.`;
    }

    setIsPlayingAudio(true);
    speakText(
      script,
      language,
      () => setIsPlayingAudio(false),
      () => setIsPlayingAudio(false)
    );
  };

  return (
    <div className="card glass treatment-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <h2 className="card-title" style={{ margin: 0 }}>
          <span aria-hidden="true">💊</span>
          <span>{t('treatment_title')}</span>
        </h2>
        <button
          className={`btn btn-sm ${isPlayingAudio ? 'btn-primary' : 'btn-secondary'}`}
          onClick={handleToggleVoice}
          title={isPlayingAudio ? t('voice_stop') : t('voice_listen')}
          aria-label={isPlayingAudio ? t('voice_stop') : t('voice_listen')}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}
        >
          <span>{isPlayingAudio ? '⏹️' : '🔊'}</span>
          <span>{isPlayingAudio ? t('voice_stop') : t('voice_listen')}</span>
        </button>
      </div>

      <p className="disease-desc">
        {disease.description || 'No description available for this class.'}
      </p>

      <div className="treatment-section">
        <h3>⚗️ {t('chemical_treatments')}</h3>
        <ul className="treatment-list" aria-label="Chemical treatment recommendations">
          {(disease.chemical_treatment && disease.chemical_treatment.length > 0
            ? disease.chemical_treatment
            : ['No specific chemical treatment required.']
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="treatment-section">
        <h3>🌿 {t('organic_treatments')}</h3>
        <ul className="treatment-list" aria-label="Organic treatment recommendations">
          {(disease.organic_treatment && disease.organic_treatment.length > 0
            ? disease.organic_treatment
            : ['No specific organic treatment required.']
          ).map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

