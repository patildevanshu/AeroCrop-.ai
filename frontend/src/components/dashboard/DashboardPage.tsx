import React, { useState, useEffect } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { ErrorBoundary } from '../common/ErrorBoundary';
import { CropProgressCard } from './CropProgressCard';
import { RecentHistoryCard } from './RecentHistoryCard';
import { WeatherRadarCard } from './WeatherRadarCard';
import { MandiDashboardCard } from './MandiDashboardCard';
import { KVKCard } from './KVKCard';
import { fetchFarmerAnalytics } from '../../api/history';
import { FarmerAnalytics } from '../../types';

interface DashboardPageProps {
  onQuickDiagnose?: (plotId?: number | null) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onQuickDiagnose }) => {
  const { t } = useI18n();
  const { userPlots, isAuthenticated } = useAuth();
  const [analytics, setAnalytics] = useState<FarmerAnalytics | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      fetchFarmerAnalytics()
        .then((data) => setAnalytics(data))
        .catch((err) => console.warn('Could not load farmer analytics:', err));
    } else {
      setAnalytics(null);
    }
  }, [isAuthenticated, userPlots]);

  const safePlots = Array.isArray(userPlots) ? userPlots : [];
  const activePlotsCount = isAuthenticated
    ? (analytics ? analytics.total_plots.toString() : safePlots.length.toString())
    : '--';
  const totalAcres = isAuthenticated
    ? (analytics ? analytics.total_acres.toFixed(1) : safePlots.reduce((sum, p) => sum + (p?.area_acres || 0), 0).toFixed(1))
    : '--';

  return (
    <section className="page-container" aria-labelledby="heading-dashboard">
      <header className="page-header">
        <div>
          <h1 id="heading-dashboard">{t('dashboard_title')}</h1>
          <p className="page-subtitle">{t('dashboard_subtitle')}</p>
        </div>
      </header>

      {/* Platform & Farmer Stats Row */}
      <div className="stats-row">
        <div className="stat-card glass">
          <div className="stat-icon" aria-hidden="true">
            {isAuthenticated && analytics && analytics.total_diagnoses > 0 ? '💚' : '🎯'}
          </div>
          <div className="stat-body">
            <p className="stat-value">
              {isAuthenticated && analytics && analytics.total_diagnoses > 0
                ? `${analytics.health_rate_percent}%`
                : '90.82%'}
            </p>
            <p className="stat-label">
              {isAuthenticated && analytics && analytics.total_diagnoses > 0
                ? t('crop_health_rate', 'Crop Health Rate')
                : t('stat_accuracy')}
            </p>
            <p style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', margin: '2px 0 0', lineHeight: 1.3, opacity: 0.85 }}>
              {isAuthenticated && analytics && analytics.total_diagnoses > 0
                ? '% of your diagnosed specimens classified as disease-free'
                : 'ResNet-18 disease classification model accuracy on validation dataset'}
            </p>
          </div>
        </div>

        <div className="stat-card glass">
          <div className="stat-icon" aria-hidden="true">🌱</div>
          <div className="stat-body">
            <p className="stat-value">{activePlotsCount}</p>
            <p className="stat-label">{t('stat_farmer_plots')}</p>
          </div>
        </div>

        <div className="stat-card glass">
          <div className="stat-icon" aria-hidden="true">📐</div>
          <div className="stat-body">
            <p className="stat-value">{totalAcres} {totalAcres !== '--' ? t('unit_acre', 'Ac') : ''}</p>
            <p className="stat-label">{t('stat_farmer_acres')}</p>
          </div>
        </div>

        <div className="stat-card glass">
          <div className="stat-icon" aria-hidden="true">
            {isAuthenticated && analytics && analytics.avg_yield_t_ha > 0 ? '🌾' : '🗺️'}
          </div>
          <div className="stat-body">
            <p className="stat-value">
              {isAuthenticated && analytics && analytics.avg_yield_t_ha > 0
                ? `${analytics.avg_yield_t_ha} t/ha`
                : '36'}
            </p>
            <p className="stat-label">
              {isAuthenticated && analytics && analytics.avg_yield_t_ha > 0
                ? t('stat_avg_yield', 'Avg Yield Forecast')
                : t('stat_districts')}
            </p>
          </div>
        </div>
      </div>

      {/* Top Disease Alerts if Diagnoses Recorded */}
      {isAuthenticated && analytics && analytics.top_diseases && analytics.top_diseases.length > 0 && (
        <div
          className="glass mb-4"
          style={{
            padding: '10px 16px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            flexWrap: 'wrap',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            background: 'rgba(254, 243, 199, 0.4)',
          }}
        >
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#92400e' }}>
            ⚠️ Active Pathogen Alerts:
          </span>
          {analytics.top_diseases.map((d, i) => (
            <span
              key={i}
              className="plot-stat-chip"
              style={{
                borderColor: '#d97706',
                color: '#92400e',
                background: 'rgba(255, 255, 255, 0.7)',
                fontWeight: 600,
                fontSize: '0.78rem',
              }}
            >
              🦠 {d.name} ({d.count} detected)
            </span>
          ))}
        </div>
      )}

      {/* Longitudinal Crop Health Progress per Analysis */}
      <ErrorBoundary fallbackTitle="Crop Health Progress (पिकाची प्रगती)">
        <CropProgressCard onQuickDiagnose={onQuickDiagnose} />
      </ErrorBoundary>

      {/* Dashboard Body Grid */}
      <div className="dashboard-grid">
        <ErrorBoundary fallbackTitle="Diagnostic History (निदान इतिहास)">
          <RecentHistoryCard />
        </ErrorBoundary>
        <ErrorBoundary fallbackTitle="Weather Radar (हवामान रडार)">
          <WeatherRadarCard />
        </ErrorBoundary>
      </div>

      {/* Live APMC Mandi Rates Grid */}
      <ErrorBoundary fallbackTitle="APMC Mandi Rates (बाजारभाव)">
        <MandiDashboardCard />
      </ErrorBoundary>

      {/* Krishi Vigyan Kendra Directory */}
      <ErrorBoundary fallbackTitle="KVK Agronomist Directory (कृषी विज्ञान केंद्र)">
        <KVKCard />
      </ErrorBoundary>
    </section>
  );
};
