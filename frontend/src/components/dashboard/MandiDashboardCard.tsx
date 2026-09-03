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
        setRates(res.market_rates);
        setLoading(false);
      })
      .catch((err) => {
        console.warn('Failed to load mandi overview:', err);
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
            APMC Hub:
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
        <p style={{ padding: '1rem', color: '#94a3b8' }}>Loading APMC market data…</p>
      ) : (
        <div style={{ overflowX: 'auto', marginTop: '0.75rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', textAlign: 'left' }}>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>Crop / Commodity</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>APMC Market</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>Modal Price</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>Price Range</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>7-Day Trend</th>
                <th style={{ padding: '0.6rem 0.75rem', color: '#94a3b8' }}>MSP Benchmark</th>
              </tr>
            </thead>
            <tbody>
              {rates.map((item) => {
                const name = language === 'mr' ? item.name_mr : (language === 'hi' ? item.name_hi : item.commodity_name);
                const trendColor = item.trend === 'bullish' ? '#10b981' : (item.trend === 'bearish' ? '#ef4444' : '#94a3b8');
                const trendIcon = item.trend === 'bullish' ? '📈' : (item.trend === 'bearish' ? '📉' : '➡️');

                return (
                  <tr key={item.crop} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '0.65rem 0.75rem', fontWeight: 600 }}>{name}</td>
                    <td style={{ padding: '0.65rem 0.75rem', color: '#cbd5e1', fontSize: '0.82rem' }}>{item.apmc_market}</td>
                    <td style={{ padding: '0.65rem 0.75rem', fontWeight: 700, color: '#38bdf8' }}>
                      ₹{item.modal_price_inr.toLocaleString('en-IN')}{' '}
                      <span style={{ fontSize: '0.75rem', fontWeight: 400, color: '#94a3b8' }}>/ q</span>
                    </td>
                    <td style={{ padding: '0.65rem 0.75rem', color: '#94a3b8' }}>
                      ₹{item.min_price_inr} – ₹{item.max_price_inr}
                    </td>
                    <td style={{ padding: '0.65rem 0.75rem', color: trendColor, fontWeight: 600 }}>
                      {trendIcon} {item.trend_change_pct}%
                    </td>
                    <td style={{ padding: '0.65rem 0.75rem' }}>
                      {item.msp_inr > 0 ? (
                        <span style={{ color: '#fbbf24' }}>₹{item.msp_inr.toLocaleString('en-IN')} / q</span>
                      ) : (
                        <span style={{ color: '#64748b' }}>Open Market</span>
                      )}
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
