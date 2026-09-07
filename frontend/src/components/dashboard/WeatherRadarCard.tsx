import React, { useState, useEffect } from 'react';
import { useI18n } from '../../context/I18nContext';
import { fetchWeatherForDistrict } from '../../api/weather';
import { WeatherData } from '../../types';

const RADAR_DISTRICTS = [
  'pune',
  'nagpur',
  'nashik',
  'aurangabad',
  'amravati',
  'kolhapur',
  'solapur',
  'akola',
];

export const WeatherRadarCard: React.FC = () => {
  const { t, language } = useI18n();
  const [radarData, setRadarData] = useState<Record<string, WeatherData | null>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    Promise.allSettled(
      RADAR_DISTRICTS.map((d) => fetchWeatherForDistrict(d))
    ).then((results) => {
      if (!isMounted) return;
      const dataMap: Record<string, WeatherData | null> = {};
      results.forEach((res, index) => {
        const district = RADAR_DISTRICTS[index];
        if (res.status === 'fulfilled') {
          dataMap[district] = res.value;
        } else {
          dataMap[district] = null;
        }
      });
      setRadarData(dataMap);
      setLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, []);

  const DISTRICT_NAMES_MR: Record<string, string> = {
    pune: 'पुणे',
    nagpur: 'नागपूर',
    nashik: 'नाशिक',
    aurangabad: 'छ. संभाजीनगर',
    amravati: 'अमरावती',
    kolhapur: 'कोल्हापूर',
    solapur: 'सोलापूर',
    akola: 'अकोला',
  };

  const DISTRICT_NAMES_HI: Record<string, string> = {
    pune: 'पुणे',
    nagpur: 'नागपुर',
    nashik: 'नासिक',
    aurangabad: 'छ. संभाजीनगर',
    amravati: 'अमरावती',
    kolhapur: 'कोल्हापुर',
    solapur: 'सोलापुर',
    akola: 'अकोला',
  };

  return (
    <div className="card glass dash-card">
      <h2 className="card-title">
        <span aria-hidden="true">🗺️</span>
        <span>{t('weather_overview')}</span>
      </h2>

      <div className="weather-radar">
        {loading ? (
          <p className="loading-text" style={{ gridColumn: '1/-1' }}>
            {t('loading_weather')}
          </p>
        ) : (
          RADAR_DISTRICTS.map((district) => {
            const data = radarData[district];
            const localizedDistrict = language === 'mr'
              ? (DISTRICT_NAMES_MR[district] || district)
              : (language === 'hi' ? (DISTRICT_NAMES_HI[district] || district) : (district.charAt(0).toUpperCase() + district.slice(1)));

            if (!data) {
              return (
                <div key={district} className="radar-card glass">
                  <p className="radar-district">{localizedDistrict}</p>
                  <p className="no-history" style={{ fontSize: '0.75rem' }}>
                    {t('unavailable')}
                  </p>
                </div>
              );
            }

            const temp = data.temperature != null ? `${data.temperature}°C` : '--';
            const hum = data.humidity != null ? `${data.humidity}%` : '--';
            const rain = data.rainfall != null ? `${data.rainfall} mm` : '--';
            const wind = data.wind_speed != null ? `${data.wind_speed} km/h` : '8 km/h';

            return (
              <div key={district} className="radar-card glass">
                <p className="radar-district">{localizedDistrict}</p>
                <p className="radar-temp">🌡️ {temp} &bull; 💧 {hum}</p>
                <p className="radar-rain">🌧️ {rain} &bull; 💨 {wind}</p>
                {data.spray_window && (
                  <span style={{
                    display: 'inline-block',
                    marginTop: '0.25rem',
                    fontSize: '0.72rem',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontWeight: 600,
                    background: data.spray_window.safe ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    color: data.spray_window.safe ? '#34d399' : '#f87171'
                  }}>
                    {data.spray_window.safe ? t('spray_safe') : t('spray_hold')}
                  </span>
                )}
                {data.source === 'mock' && (
                  <span className="radar-mock">mock</span>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
