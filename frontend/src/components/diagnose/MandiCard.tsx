import React from 'react';
import { MandiRateInfo } from '../../types';
import { useI18n } from '../../context/I18nContext';

interface MandiCardProps {
  mandi: MandiRateInfo;
}

export const MandiCard: React.FC<MandiCardProps> = ({ mandi }) => {
  const { t, language } = useI18n();

  const displayName = language === 'mr' ? mandi.name_mr : (language === 'hi' ? mandi.name_hi : mandi.commodity_name);
  const trendColor = mandi.trend === 'bullish' ? '#10b981' : (mandi.trend === 'bearish' ? '#ef4444' : '#6b7280');
  const trendArrow = mandi.trend === 'bullish' ? '▲' : (mandi.trend === 'bearish' ? '▼' : '▬');

  return (
    <div className="card glass mandi-card" style={{ marginTop: '1.25rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
        <h2 className="card-title" style={{ margin: 0 }}>
          <span aria-hidden="true">🏛️</span>
          <span>{t('mandi_rates')}</span>
        </h2>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
          📍 {mandi.apmc_market}
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
        {/* Modal Price */}
        <div className="metric-card glass" style={{ padding: '0.85rem' }}>
          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('modal_price')}</p>
          <p style={{ margin: '0.2rem 0', fontSize: '1.4rem', fontWeight: 700, color: '#0369a1' }}>
            ₹{mandi.modal_price_inr.toLocaleString('en-IN')}
          </p>
          <p style={{ margin: 0, fontSize: '0.75rem', color: trendColor }}>
            {trendArrow} {mandi.trend.toUpperCase()} ({mandi.trend_change_pct > 0 ? `+${mandi.trend_change_pct}%` : `${mandi.trend_change_pct}%`})
          </p>
        </div>

        {/* Min - Max Range */}
        <div className="metric-card glass" style={{ padding: '0.85rem' }}>
          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{t('min_max_price')}</p>
          <p style={{ margin: '0.2rem 0', fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            ₹{mandi.min_price_inr.toLocaleString('en-IN')} – ₹{mandi.max_price_inr.toLocaleString('en-IN')}
          </p>
          <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {mandi.unit}
          </p>
        </div>

        {/* MSP Comparison or Arrivals */}
        <div className="metric-card glass" style={{ padding: '0.85rem' }}>
          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            {mandi.msp_inr > 0 ? t('msp_col') : t('daily_arrivals')}
          </p>
          <p style={{ margin: '0.2rem 0', fontSize: '1.1rem', fontWeight: 600, color: mandi.msp_inr > 0 ? '#d97706' : '#7c3aed' }}>
            {mandi.msp_inr > 0 ? `₹${mandi.msp_inr.toLocaleString('en-IN')}` : `${mandi.arrivals_quintal} q`}
          </p>
          <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {mandi.msp_inr > 0 ? t('goi_msp') : t('market_inflow')}
          </p>
        </div>
      </div>

      {/* Revenue Projection Banner */}
      {mandi.revenue_projection && (
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(56, 189, 248, 0.08))',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            borderRadius: '8px',
            padding: '0.85rem 1.1rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '0.75rem',
          }}
        >
          <div>
            <span style={{ fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#15803d', fontWeight: 600 }}>
              🌾 {t('projected_revenue')} ({displayName})
            </span>
            <div style={{ marginTop: '0.2rem', fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              ₹{mandi.revenue_projection.gross_revenue_acre_inr.toLocaleString('en-IN')}{' '}
              <span style={{ fontSize: '0.85rem', fontWeight: 400, color: 'var(--text-secondary)' }}>/ {t('unit_acre')}</span>
              {'  '}
              <span style={{ fontSize: '1rem', color: 'rgba(140, 195, 165, 0.5)' }}>|</span>
              {'  '}
              <span style={{ fontSize: '1.05rem', color: 'var(--text-secondary)' }}>
                ₹{mandi.revenue_projection.gross_revenue_ha_inr.toLocaleString('en-IN')}
              </span>{' '}
              <span style={{ fontSize: '0.85rem', fontWeight: 400, color: 'var(--text-secondary)' }}>/ {t('unit_ha')}</span>
            </div>
          </div>
          <div style={{ textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <span>{t('est_harvest')} {mandi.revenue_projection.yield_quintals_per_acre} q/acre</span>
            <br />
            <span>({mandi.revenue_projection.yield_t_ha} t/ha)</span>
          </div>
        </div>
      )}
    </div>
  );
};
