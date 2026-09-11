import React, { useState, useEffect, useRef } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { WeatherStrip } from '../layout/WeatherStrip';
import { UploadCard } from './UploadCard';
import { ParamsCard } from './ParamsCard';
import { ResultsArea } from './ResultsArea';
import { AnalyzingOverlay } from './AnalyzingOverlay';
import { fetchDistricts, fetchWeatherForDistrict } from '../../api/weather';
import { submitCropPrediction } from '../../api/predict';
import { saveToLocalHistory } from '../../api/history';
import { WeatherData, PredictionResult } from '../../types';

interface DiagnosePageProps {
  initialPlotId?: string;
  initialCrop?: string;
}

export const DiagnosePage: React.FC<DiagnosePageProps> = ({ initialPlotId = '', initialCrop = '' }) => {
  const { t } = useI18n();
  const { currentUser, refreshPlots } = useAuth();
  const { showToast } = useToast();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [crop, setCrop] = useState<string>(initialCrop ? initialCrop.toLowerCase() : 'auto');
  const [district, setDistrict] = useState<string>('pune');
  const [districts, setDistricts] = useState<string[]>([]);
  const [selectedPlotId, setSelectedPlotId] = useState<string>(initialPlotId);
  const [farmerEmail, setFarmerEmail] = useState<string>('');
  const [soilN, setSoilN] = useState<number | ''>('');
  const [soilP, setSoilP] = useState<number | ''>('');
  const [soilK, setSoilK] = useState<number | ''>('');
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PredictionResult | null>(null);

  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (currentUser?.email) {
      setFarmerEmail(currentUser.email);
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

  // Load districts on mount
  useEffect(() => {
    fetchDistricts()
      .then((data) => {
        setDistricts(data.districts);
        if (data.districts.length > 0 && !data.districts.includes(district)) {
          setDistrict(data.districts[0]);
        }
      })
      .catch((err) => {
        console.warn('Failed to load districts:', err);
        setDistricts(['pune', 'nagpur', 'nashik', 'amravati', 'kolhapur', 'aurangabad', 'solapur', 'jalgaon']);
      });
  }, []);

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
    const startTime = Date.now();
    try {
      const data = await submitCropPrediction({
        image: selectedFile,
        crop,
        district,
        plot_id: selectedPlotId ? parseInt(selectedPlotId, 10) : null,
        N: soilN === '' ? null : Number(soilN),
        P: soilP === '' ? null : Number(soilP),
        K: soilK === '' ? null : Number(soilK),
        email: farmerEmail.trim() || null,
      });

      // Ensure the user gets to experience the ISRO/NASA satellite telemetry scanner for at least 2.8s
      const elapsed = Date.now() - startTime;
      const minDisplayTimeMs = 2800;
      if (elapsed < minDisplayTimeMs) {
        await new Promise((resolve) => setTimeout(resolve, minDisplayTimeMs - elapsed));
      }

      setResult(data);
      if (data.weather) {
        setWeather(data.weather);
      }

      // If not persisted to server records, save to local storage history
      if (!data.saved_record_id) {
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
      } else {
        await refreshPlots();
      }

      showToast('Analysis completed successfully!', 'success');

      if (data.email_status === 'queued' || data.email_recipient) {
        setTimeout(() => {
          showToast(`📧 Report is sent on email also (${data.email_recipient || farmerEmail.trim()})!`, 'success');
        }, 800);
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
          soilN={soilN}
          setSoilN={setSoilN}
          soilP={soilP}
          setSoilP={setSoilP}
          soilK={soilK}
          setSoilK={setSoilK}
          farmerEmail={farmerEmail}
          setFarmerEmail={setFarmerEmail}
          onAnalyze={handleAnalyze}
          isLoading={isLoading}
        />
      </div>

      {/* Results Area */}
      <div ref={resultsRef}>
        {result && <ResultsArea result={result} />}
      </div>

      {/* Futuristic Satellite & ISRO/NASA Telemetry Scanner Overlay */}
      <AnalyzingOverlay
        isOpen={isLoading}
        selectedFile={selectedFile}
        crop={crop}
        district={district}
      />
    </section>
  );
};
