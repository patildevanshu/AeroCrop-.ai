import React from 'react';
import { WeatherData } from '../../types';
import { useI18n } from '../../context/I18nContext';

interface WeatherStripProps {
  weather: WeatherData | null;
}

export const WeatherStrip: React.FC<WeatherStripProps> = ({ weather }) => {
  const { t } = useI18n();

  const sprayBadge = weather?.spray_window
    ? (weather.spray_window.safe ? t('spray_safe') : (weather.spray_window.status === 'warning' ? t('spray_caution') : t('spray_hold')))
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
        <span className="weather-lbl">{t('weather_wind')}</span>
      </div>
      {sprayBadge && (
        <div className="weather-item" style={{ borderLeft: '1px solid rgba(140, 195, 165, 0.35)', paddingLeft: '0.6rem' }}>
          <span className="weather-val" style={{
            fontSize: '0.82rem',
            fontWeight: 700,
            color: weather?.spray_window?.safe ? '#15803d' : (weather?.spray_window?.status === 'warning' ? '#b45309' : '#b91c1c')
          }}>
            {sprayBadge}
          </span>
          <span className="weather-lbl">{t('spray_advisory')}</span>
        </div>
      )}
    </div>
  );
};

