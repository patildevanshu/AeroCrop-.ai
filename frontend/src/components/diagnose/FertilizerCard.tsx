import React, { useState } from 'react';
import { PredictionResult } from '../../types';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { printAdvisoryReport } from './PrintReport';
import { EmailReportModal } from './EmailReportModal';

interface FertilizerCardProps {
  result: PredictionResult;
}

export const FertilizerCard: React.FC<FertilizerCardProps> = ({ result }) => {
  const { t } = useI18n();
  const { currentUser } = useAuth();
  const { fertilizer } = result;

  const [unit, setUnit] = useState<'acre' | 'guntha' | 'ha'>('acre');
  const [area, setArea] = useState<number>(1.0);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);

  // 1 ha = 2.47105 acres = 100 gunthas
  const multiplier = unit === 'ha' ? area : (unit === 'acre' ? area / 2.47105 : area / 100.0);

  const ureaKg = Math.max(0, fertilizer.fertilizers.Urea * multiplier);
  const dapKg = Math.max(0, fertilizer.fertilizers.DAP * multiplier);
  const mopKg = Math.max(0, fertilizer.fertilizers.MOP * multiplier);

  const ureaBags = Math.ceil(ureaKg / 50.0);
  const dapBags = Math.ceil(dapKg / 50.0);
  const mopBags = Math.ceil(mopKg / 50.0);

  const costUrea = ureaBags * 267;
  const costDap = dapBags * 1350;
  const costMop = mopBags * 1700;
  const totalCost = costUrea + costDap + costMop;

  const handlePrint = (isPmfby = false) => {
    printAdvisoryReport(result, currentUser, isPmfby);
  };

  const handleShareWhatsApp = () => {
    const msg = `*AeroCrop.ai Farmer Crop Advisory* 🌿
🌱 *Crop*: ${result.crop}
📍 *District*: ${result.district}
🦠 *Condition*: ${result.disease.name} (${result.disease.confidence}% confidence)
⚠️ *Severity*: ${result.disease.severity}
🌾 *Yield Forecast*: ${result.yield_t_ha} t/ha (${(result.yield_t_ha * 4.047).toFixed(1)} q/acre)
💊 *Chemical*: ${(result.disease.chemical_treatment || []).slice(0, 2).join(', ')}
🌿 *Organic*: ${(result.disease.organic_treatment || []).slice(0, 2).join(', ')}
🧬 *Fertilizer Plan (${area} ${unit})*:
• Urea: ${ureaBags} bags (₹${costUrea})
• DAP: ${dapBags} bags (₹${costDap})
• MOP: ${mopBags} bags (₹${costMop})
💰 *Estimated Input Cost*: ₹${totalCost.toLocaleString('en-IN')}

Generated via AeroCrop.ai Precision Agriculture Platform`;

    const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(msg)}`;
    window.open(url, '_blank');
  };

  return (
    <div className="card glass fertilizer-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h2 className="card-title" style={{ margin: 0 }}>
          <span aria-hidden="true">🧬</span>
          <span>{t('fertilizer_title')}</span>
        </h2>
        {/* Unit & Area Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
          <input
            type="number"
            min="0.1"
            step="0.5"
            value={area}
            onChange={(e) => setArea(Math.max(0.1, parseFloat(e.target.value) || 0.1))}
            style={{ width: '56px', padding: '0.2rem 0.4rem', borderRadius: '4px', border: '1px solid rgba(140,195,165,0.4)', background: '#fff', color: 'var(--text-primary)' }}
          />
          <select
            value={unit}
            onChange={(e) => setUnit(e.target.value as any)}
            style={{ padding: '0.2rem 0.4rem', borderRadius: '4px', border: '1px solid rgba(140,195,165,0.4)', background: '#fff', color: 'var(--text-primary)' }}
          >
            <option value="acre">{t('unit_acre')}</option>
            <option value="guntha">{t('unit_guntha')}</option>
            <option value="ha">{t('unit_ha')}</option>
          </select>
        </div>
      </div>

      <p className="fert-interp" style={{ marginTop: '0.6rem' }}>{fertilizer.interpretation}</p>

      {fertilizer.surplus_n_warning && (
        <div className="surplus-warning" role="alert">
          ⚠️ {fertilizer.surplus_n_warning}
        </div>
      )}

      {/* Commercial 50kg Bags Grid */}
      <div className="fert-cards" style={{ marginTop: '0.75rem' }}>
        <div className="fert-item">
          <div className="fert-icon" aria-hidden="true">🟡</div>
          <div className="fert-body">
            <p className="fert-name">Urea (46% N)</p>
            <p className="fert-qty" style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              {ureaBags} <span style={{ fontSize: '0.8rem', fontWeight: 400 }}>{t('bags_50kg')}</span>
            </p>
            <p className="fert-note">{ureaKg.toFixed(1)} kg &bull; ₹{costUrea.toLocaleString('en-IN')}</p>
          </div>
        </div>

        <div className="fert-item">
          <div className="fert-icon" aria-hidden="true">🟤</div>
          <div className="fert-body">
            <p className="fert-name">DAP (18-46-0)</p>
            <p className="fert-qty" style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              {dapBags} <span style={{ fontSize: '0.8rem', fontWeight: 400 }}>{t('bags_50kg')}</span>
            </p>
            <p className="fert-note">{dapKg.toFixed(1)} kg &bull; ₹{costDap.toLocaleString('en-IN')}</p>
          </div>
        </div>

        <div className="fert-item">
          <div className="fert-icon" aria-hidden="true">🔴</div>
          <div className="fert-body">
            <p className="fert-name">MOP (60% K)</p>
            <p className="fert-qty" style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              {mopBags} <span style={{ fontSize: '0.8rem', fontWeight: 400 }}>{t('bags_50kg')}</span>
            </p>
            <p className="fert-note">{mopKg.toFixed(1)} kg &bull; ₹{costMop.toLocaleString('en-IN')}</p>
          </div>
        </div>
      </div>

      {/* Estimated Total Fertilizer Cost Banner */}
      <div
        style={{
          marginTop: '0.75rem',
          padding: '0.6rem 0.9rem',
          borderRadius: '8px',
          background: 'rgba(240, 253, 244, 0.85)',
          border: '1px solid rgba(140, 195, 165, 0.35)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.9rem',
          color: 'var(--text-primary)',
        }}
      >
        <span>💰 {t('est_cost')} ({area} {t(`unit_${unit}` as any)}):</span>
        <strong style={{ fontSize: '1.1rem', color: '#15803d' }}>
          ₹{totalCost.toLocaleString('en-IN')}
        </strong>
      </div>

      {/* Action Buttons Row */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '1rem' }}>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => handlePrint(false)}
          aria-label="Print prescription report"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}
        >
          <span aria-hidden="true">🖨️</span>
          <span>{t('print_report')}</span>
        </button>

        <button
          className="btn btn-sm"
          onClick={handleShareWhatsApp}
          style={{ background: '#25D366', color: '#fff', border: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}
          title={t('share_whatsapp')}
          aria-label={t('share_whatsapp')}
        >
          <span aria-hidden="true">💬</span>
          <span>{t('share_whatsapp')}</span>
        </button>

        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setIsEmailModalOpen(true)}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}
          title="Email Advisory PDF"
          aria-label="Email Advisory PDF"
        >
          <span aria-hidden="true">📧</span>
          <span>Email PDF</span>
        </button>

        <button
          className="btn btn-secondary btn-sm"
          onClick={() => handlePrint(true)}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}
          title={t('pmfby_report')}
          aria-label={t('pmfby_report')}
        >
          <span aria-hidden="true">📋</span>
          <span>{t('pmfby_report')}</span>
        </button>
      </div>

      <EmailReportModal
        isOpen={isEmailModalOpen}
        result={result}
        onClose={() => setIsEmailModalOpen(false)}
      />
    </div>
  );
};
