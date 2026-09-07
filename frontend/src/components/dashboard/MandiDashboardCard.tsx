import React, { useState, useEffect } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { fetchDistrictMandiOverview } from '../../api/mandi';
import { MandiRateInfo } from '../../types';

export const MandiDashboardCard: React.FC = () => {
  const { t, language } = useI18n();
  const { currentUser } = useAuth();

  const [district, setDistrict] = useState<string>(currentUser?.district || 'pune');
  const [rates, setRates] = useState<MandiRateInfo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const districtList = [
    'pune', 'nashik', 'jalgaon', 'nagpur', 'amravati',
    'latur', 'kolhapur', 'solapur', 'aurangabad', 'akola'
  ];

  useEffect(() => {
    setLoading(true);
    fetchDistrictMandiOverview(district)
      .then((res) => {
        setRates(Array.isArray(res?.market_rates) ? res.market_rates : []);
        setLoading(false);
      })
      .catch((err) => {
        console.warn('Failed to load mandi overview:', err);
        setRates([]);
        setLoading(false);
      });
  }, [district]);

  return (
    <div className="card glass dash-card" style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
      <div className="dash-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
        <h2 className="card-title" style={{ margin: 0 }}>
          <span aria-hidden="true">🏛️</span>
          <span>{t('mandi_rates')}</span>
        </h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <label htmlFor="mandi-district-select" style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            {t('apmc_hub')}
          </label>
          <select
            id="mandi-district-select"
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            style={{
              padding: '0.3rem 0.6rem',
              borderRadius: '6px',
              border: '1px solid rgba(255,255,255,0.2)',
              background: 'rgba(0,0,0,0.3)',
              color: '#fff',
              fontSize: '0.85rem',
            }}
          >
            {districtList.map((d) => (
              <option key={d} value={d}>
                {d.toUpperCase()} APMC
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <p style={{ padding: '1rem', color: '#94a3b8' }}>{t('loading_mandi')}</p>
      ) : (
        <div style={{ overflowX: 'auto', marginTop: '0.75rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', textAlign: 'left' }}>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>{t('commodity_col')}</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>{t('market_col')}</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>{t('modal_price_col')}</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>{t('price_range_col')}</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>{t('trend_col')}</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>{t('msp_col')}</th>
              </tr>
            </thead>
            <tbody>
              {(Array.isArray(rates) ? rates : []).map((item) => {
                const name = language === 'mr' ? item.name_mr : (language === 'hi' ? item.name_hi : item.commodity_name);
                const trendColor = item.trend === 'bullish' ? '#10b981' : (item.trend === 'bearish' ? '#ef4444' : '#94a3b8');
                const trendIcon = item.trend === 'bullish' ? '📈' : (item.trend === 'bearish' ? '📉' : '➡️');
                const trendText = item.trend === 'bullish' ? t('trend_bullish') : (item.trend === 'bearish' ? t('trend_bearish') : t('trend_steady'));
                const modalPrice = item.modal_price_inr != null ? item.modal_price_inr : 0;
                const minPrice = item.min_price_inr != null ? item.min_price_inr : 0;
                const maxPrice = item.max_price_inr != null ? item.max_price_inr : 0;
                const mspPrice = item.msp_inr != null ? item.msp_inr : 0;

                return (
                  <tr key={item.crop} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '0.65rem 0.75rem', fontWeight: 600 }}>{name || item.crop}</td>
                    <td style={{ padding: '0.65rem 0.75rem', color: '#cbd5e1', fontSize: '0.82rem' }}>{item.apmc_market || 'APMC'}</td>
                    <td style={{ padding: '0.65rem 0.75rem', fontWeight: 700, color: '#38bdf8' }}>
                      ₹{modalPrice.toLocaleString('en-IN')}{' '}
                      <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#94a3b8' }}>/ q</span>
                    </td>
                    <td style={{ padding: '0.65rem 0.75rem', color: '#94a3b8' }}>
                      ₹{minPrice} – ₹{maxPrice}
                    </td>
                    <td style={{ padding: '0.65rem 0.75rem', color: trendColor, fontWeight: 600 }} title={trendText}>
                      {trendIcon} {item.trend_change_pct != null ? item.trend_change_pct : 0}%
                    </td>
                    <td style={{ padding: '0.65rem 0.75rem', color: mspPrice > 0 ? '#fbbf24' : '#94a3b8' }}>
                      {mspPrice > 0 ? `₹${mspPrice.toLocaleString('en-IN')}` : '--'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
