import React from 'react';
import { FertilizerAdvice } from '../../types';
import { useI18n } from '../../context/I18nContext';

interface NPKChartProps {
  fertilizer: FertilizerAdvice;
}

export const NPKChart: React.FC<NPKChartProps> = ({ fertilizer }) => {
  const { t } = useI18n();
  const ferts = fertilizer.fertilizers;

  const ureaKg = ferts.Urea || 0;
  const dapKg = ferts.DAP || 0;
  const mopKg = ferts.MOP || 0;

  // Split calculation
  const basalUrea = Math.round(ureaKg * 0.33);
  const vegUrea = Math.round(ureaKg * 0.33);
  const flowerUrea = Math.round(ureaKg * 0.34);

  return (
    <div className="card glass chart-card" style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
        <h2 className="card-title" style={{ margin: 0 }}>
          <span aria-hidden="true">📅</span>
          <span>{t('fertilizer_schedule') || 'Crop Nutrient Application Schedule (खत व्यवस्थापन वेळापत्रक)'}</span>
        </h2>
        <span style={{ fontSize: '0.8rem', color: '#10b981', background: 'rgba(16,185,129,0.1)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(16,185,129,0.2)' }}>
          ✓ Certified ICAR Package of Practices
        </span>
      </div>

      <p style={{ margin: '0 0 1.25rem 0', fontSize: '0.86rem', color: '#94a3b8', lineHeight: 1.5 }}>
        To prevent nitrogen leaching and maximize root absorption, standard scientific guidelines recommend splitting fertilizer doses across key growth stages rather than applying all at once.
      </p>

      {/* Stage Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
        
        {/* Stage 1 */}
        <div className="metric-card glass" style={{ padding: '1rem', borderLeft: '3px solid #38bdf8' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#38bdf8' }}>
              🌱 STAGE 1: BASAL (पेरणीच्या वेळी)
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Day 0</span>
          </div>
          <p style={{ margin: '0.4rem 0', fontSize: '0.95rem', fontWeight: 600 }}>
            Full Phosphorus &amp; Potash + 1/3rd Nitrogen
          </p>
          <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.82rem', margin: '0.5rem 0' }}>
            <div>• <strong>DAP:</strong> {dapKg} kg/ha (100% dose)</div>
            <div>• <strong>MOP:</strong> {mopKg} kg/ha (100% dose)</div>
            <div>• <strong>Urea:</strong> {basalUrea} kg/ha (33% dose)</div>
          </div>
          <p style={{ margin: '0.4rem 0 0 0', fontSize: '0.78rem', color: '#94a3b8' }}>
            Apply directly into the root furrow at the time of sowing or transplanting for deep root establishment.
          </p>
        </div>

        {/* Stage 2 */}
        <div className="metric-card glass" style={{ padding: '1rem', borderLeft: '3px solid #10b981' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#10b981' }}>
              🌿 STAGE 2: VEGETATIVE (वाढीची अवस्था)
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>30–35 DAS</span>
          </div>
          <p style={{ margin: '0.4rem 0', fontSize: '0.95rem', fontWeight: 600 }}>
            1st Top-Dressing (नायट्रोजन पहिला हप्ता)
          </p>
          <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.82rem', margin: '0.5rem 0' }}>
            <div>• <strong>Urea:</strong> {vegUrea} kg/ha (33% dose)</div>
            <div style={{ color: '#94a3b8' }}>• DAP / MOP: Not required</div>
          </div>
          <p style={{ margin: '0.4rem 0 0 0', fontSize: '0.78rem', color: '#94a3b8' }}>
            Top-dress along the plant rows followed immediately by light irrigation to support stem elongation and leaf branching.
          </p>
        </div>

        {/* Stage 3 */}
        <div className="metric-card glass" style={{ padding: '1rem', borderLeft: '3px solid #fbbf24' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fbbf24' }}>
              🌸 STAGE 3: FLOWERING (फुलोरा अवस्था)
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>60–65 DAS</span>
          </div>
          <p style={{ margin: '0.4rem 0', fontSize: '0.95rem', fontWeight: 600 }}>
            2nd Top-Dressing (नायट्रोजन दुसरा हप्ता)
          </p>
          <div style={{ background: 'rgba(0,0,0,0.2)', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.82rem', margin: '0.5rem 0' }}>
            <div>• <strong>Urea:</strong> {flowerUrea} kg/ha (remaining 34% dose)</div>
            <div style={{ color: '#94a3b8' }}>• DAP / MOP: Not required</div>
          </div>
          <p style={{ margin: '0.4rem 0 0 0', fontSize: '0.78rem', color: '#94a3b8' }}>
            Apply remaining Nitrogen to nourish boll/pod development and maximize final harvest yield.
          </p>
        </div>

      </div>
    </div>
  );
};
