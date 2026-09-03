import React from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { RecentHistoryCard } from './RecentHistoryCard';
import { WeatherRadarCard } from './WeatherRadarCard';
import { MandiDashboardCard } from './MandiDashboardCard';
import { KVKCard } from './KVKCard';

export const DashboardPage: React.FC = () => {
  const { t } = useI18n();
  const { userPlots, isAuthenticated } = useAuth();

  const activePlotsCount = isAuthenticated ? userPlots.length.toString() : '--';
  const totalAcres = isAuthenticated
    ? userPlots.reduce((sum, p) => sum + (p.area_acres || 0), 0).toFixed(1)
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

      {/* Dashboard Body Grid */}
      <div className="dashboard-grid">
        <RecentHistoryCard />
        <WeatherRadarCard />
      </div>

      {/* Live APMC Mandi Rates Grid */}
      <MandiDashboardCard />

      {/* Krishi Vigyan Kendra Directory */}
      <KVKCard />
    </section>
  );
};
