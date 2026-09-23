import React, { useState, useEffect, useRef } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { WeatherStrip } from '../layout/WeatherStrip';
import { UploadCard } from './UploadCard';
import { ParamsCard } from './ParamsCard';
import { ResultsArea } from './ResultsArea';
import { fetchDistricts, fetchWeatherForDistrict } from '../../api/weather';
import { submitCropPrediction } from '../../api/predict';
import { saveToLocalHistory } from '../../api/history';
import { WeatherData, PredictionResult } from '../../types';

interface DiagnosePageProps {
  initialPlotId?: string;
  initialCrop?: string;
}

export const DiagnosePage: React.FC<DiagnosePageProps> = ({ initialPlotId = '', initialCrop = '' }) => {
  const { t, language } = useI18n();
  const { currentUser, refreshPlots } = useAuth();
  const { showToast } = useToast();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [crop, setCrop] = useState<string>(initialCrop ? initialCrop.toLowerCase() : 'auto');
  const [district, setDistrict] = useState<string>(
    currentUser?.district ? currentUser.district.toLowerCase() : 'pune'
  );
  const [districts, setDistricts] = useState<string[]>([]);
  const [selectedPlotId, setSelectedPlotId] = useState<string>(initialPlotId);
  const [farmerEmail, setFarmerEmail] = useState<string>(currentUser?.email || '');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PredictionResult | null>(null);

  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (currentUser?.email) {
      setFarmerEmail(currentUser.email);
    }
    if (currentUser?.district) {
      setDistrict(currentUser.district.toLowerCase());
    }
  }, [currentUser]);

  useEffect(() => {
    setSelectedPlotId(initialPlotId);
  }, [initialPlotId]);

  useEffect(() => {
    if (initialCrop) {
      setCrop(initialCrop.toLowerCase());
    }
  }, [initialCrop]);

  // Load districts on mount & prioritize user's signup district
  useEffect(() => {
    fetchDistricts()
      .then((data) => {
        setDistricts(data.districts);
        if (currentUser?.district && data.districts.includes(currentUser.district.toLowerCase())) {
          setDistrict(currentUser.district.toLowerCase());
        } else if (data.districts.length > 0 && !data.districts.includes(district)) {
          setDistrict(data.districts[0]);
        }
      })
      .catch((err) => {
        console.warn('Failed to load districts:', err);
        const fallback = ['pune', 'nagpur', 'nashik', 'amravati', 'kolhapur', 'aurangabad', 'solapur', 'jalgaon'];
        setDistricts(fallback);
        if (currentUser?.district && fallback.includes(currentUser.district.toLowerCase())) {
          setDistrict(currentUser.district.toLowerCase());
        }
      });
  }, [currentUser]);

  // Fetch weather when district changes
  useEffect(() => {
    if (!district) return;
    fetchWeatherForDistrict(district)
      .then((data) => setWeather(data))
      .catch((err) => console.warn('Weather fetch failed:', err));
  }, [district]);

  // Handle analysis submission
  const handleAnalyze = async () => {
    if (!selectedFile) {
      showToast('Please upload a leaf photograph first.', 'warning');
      return;
    }

    setIsLoading(true);
    setResult(null);          // ← Clear previous analysis immediately so stale data never persists
    try {
      const data = await submitCropPrediction({
        image: selectedFile,
        crop,
        district,
        plot_id: selectedPlotId ? parseInt(selectedPlotId, 10) : null,
        email: farmerEmail.trim() || null,
      });

      setResult(data);
      if (data.weather) {
        setWeather(data.weather);
      }

      // If not persisted to server records, save to local storage history (skip if OOD / no match)
      if (!data.saved_record_id && !data.out_of_distribution) {
        saveToLocalHistory({
          created_at: new Date().toISOString(),
          crop_type: data.crop,
          district: data.district,
          disease_name: data.disease.name,
          confidence: data.disease.confidence,
          predicted_yield_t_ha: data.yield_t_ha,
          severity: data.disease.severity,
          is_healthy: data.disease.is_healthy,
          image_url: data.image_url,
        });
      } else if (data.saved_record_id) {
        await refreshPlots();
      }

      if (data.out_of_distribution) {
        showToast('⚠️ Crop specimen not found in trained dataset (No Match).', 'warning');
      } else {
        showToast('Analysis completed successfully!', 'success');
      }

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err: any) {
      showToast(`Analysis failed: ${err.message}`, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="page-container" aria-labelledby="heading-diagnose">
      <header className="page-header">
        <div>
          <h1 id="heading-diagnose">{t('diagnose_title')}</h1>
          <p className="page-subtitle">{t('diagnose_subtitle')}</p>
        </div>
        <WeatherStrip weather={weather} />
      </header>

      {/* Input Grid: Upload + Parameters */}
      <div className="input-grid">
        <UploadCard selectedFile={selectedFile} onFileSelect={setSelectedFile} />
        <ParamsCard
          crop={crop}
          setCrop={setCrop}
          district={district}
          setDistrict={setDistrict}
          districts={districts}
          selectedPlotId={selectedPlotId}
          setSelectedPlotId={setSelectedPlotId}
          farmerEmail={farmerEmail}
          setFarmerEmail={setFarmerEmail}
          onAnalyze={handleAnalyze}
          isLoading={isLoading}
        />
      </div>

      {/* Results Area with Clean Spinning Wheel Loader */}
      <div ref={resultsRef}>
        {isLoading && (
          <div
            className="card glass spinning-wheel-loader"
            role="status"
            aria-live="polite"
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '44px 20px',
              marginTop: '24px',
              textAlign: 'center',
              borderRadius: '16px',
              border: '1.5px solid rgba(16, 185, 129, 0.35)',
              background: 'rgba(255, 255, 255, 0.9)',
              boxShadow: '0 8px 24px rgba(16, 185, 129, 0.1)',
            }}
          >
            <div
              className="spinning-wheel"
              style={{
                width: '48px',
                height: '48px',
                border: '4px solid rgba(16, 185, 129, 0.2)',
                borderTopColor: '#10b981',
                borderRadius: '50%',
                animation: 'spin 0.8s linear infinite',
                marginBottom: '16px',
              }}
            />
            <h3 style={{ margin: '0 0 6px 0', fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {t('analyzing_btn')}...
            </h3>
            <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              {language === 'mr'
                ? 'कृपया प्रतीक्षा करा, पानाचे विश्लेषण सुरू आहे...'
                : (language === 'hi' ? 'कृपया प्रतीक्षा करें, पत्ती का विश्लेषण जारी है...' : 'Please wait, analyzing leaf specimen...')}
            </p>
          </div>
        )}

        {result && <ResultsArea result={result} />}
      </div>
    </section>
  );
};
