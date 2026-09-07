import React from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { ErrorBoundary } from '../common/ErrorBoundary';
import { CropProgressCard } from './CropProgressCard';
import { RecentHistoryCard } from './RecentHistoryCard';
import { WeatherRadarCard } from './WeatherRadarCard';
import { MandiDashboardCard } from './MandiDashboardCard';
import { KVKCard } from './KVKCard';

interface DashboardPageProps {
  onQuickDiagnose?: (plotId?: number | null) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onQuickDiagnose }) => {
  const { t } = useI18n();
  const { userPlots, isAuthenticated } = useAuth();

  const safePlots = Array.isArray(userPlots) ? userPlots : [];
  const activePlotsCount = isAuthenticated ? safePlots.length.toString() : '--';
  const totalAcres = isAuthenticated
    ? safePlots.reduce((sum, p) => sum + (p?.area_acres || 0), 0).toFixed(1)
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
          <div className="stat-icon" aria-hidden="true">🎯</div>
          <div className="stat-body">
            <p className="stat-value">90.82%</p>
            <p className="stat-label">{t('stat_accuracy')}</p>
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
            <p className="stat-value">{totalAcres}</p>
            <p className="stat-label">{t('stat_farmer_acres')}</p>
          </div>
        </div>

        <div className="stat-card glass">
          <div className="stat-icon" aria-hidden="true">🗺️</div>
          <div className="stat-body">
            <p className="stat-value">36</p>
            <p className="stat-label">{t('stat_districts')}</p>
          </div>
        </div>
      </div>

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
