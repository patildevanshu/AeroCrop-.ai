import React from 'react';
import { WeatherData } from '../../types';
import { useI18n } from '../../context/I18nContext';

interface WeatherStripProps {
  weather: WeatherData | null;
}

export const WeatherStrip: React.FC<WeatherStripProps> = ({ weather }) => {
  const { t } = useI18n();

  const sprayBadge = weather?.spray_window
    ? (weather.spray_window.safe ? '🟢 Safe to Spray' : (weather.spray_window.status === 'warning' ? '🟡 Caution' : '🔴 Hold Spray'))
    : null;

  return (
    <div className="weather-strip glass" aria-live="polite" aria-label="Live weather information">
      <div className="weather-item">
        <span className="weather-icon" aria-hidden="true">🌡️</span>
        <span className="weather-val">
          {weather ? `${weather.temperature}°C` : '--°C'}
        </span>
        <span className="weather-lbl">{t('weather_temp')}</span>
      </div>
      <div className="weather-item">
        <span className="weather-icon" aria-hidden="true">💧</span>
        <span className="weather-val">
          {weather ? `${weather.humidity}%` : '--%'}
        </span>
        <span className="weather-lbl">{t('weather_hum')}</span>
      </div>
      <div className="weather-item">
        <span className="weather-icon" aria-hidden="true">🌧️</span>
        <span className="weather-val">
          {weather ? `${weather.rainfall} mm` : '-- mm'}
        </span>
        <span className="weather-lbl">{t('weather_rain')}</span>
      </div>
      <div className="weather-item">
        <span className="weather-icon" aria-hidden="true">💨</span>
        <span className="weather-val">
          {weather?.wind_speed ? `${weather.wind_speed} km/h` : '-- km/h'}
        </span>
        <span className="weather-lbl">Wind</span>
      </div>
      {sprayBadge && (
        <div className="weather-item" style={{ borderLeft: '1px solid rgba(255,255,255,0.1)', paddingLeft: '0.6rem' }}>
          <span className="weather-val" style={{
            fontSize: '0.82rem',
            fontWeight: 700,
            color: weather?.spray_window?.safe ? '#34d399' : (weather?.spray_window?.status === 'warning' ? '#fbbf24' : '#f87171')
          }}>
            {sprayBadge}
          </span>
          <span className="weather-lbl">{t('spray_advisory')}</span>
        </div>
      )}
    </div>
  );
};

