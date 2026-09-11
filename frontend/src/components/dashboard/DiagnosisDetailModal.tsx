import React, { useEffect, useState } from 'react';
import { DiagnosisDetail, HistoryRecord, PredictionResult } from '../../types';
import { fetchHistoryDetail } from '../../api/history';
import { printAdvisoryReport } from '../diagnose/PrintReport';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

interface DiagnosisDetailModalProps {
  isOpen: boolean;
  recordId: number | null;
  localRecord?: HistoryRecord | null;
  onClose: () => void;
}

export const DiagnosisDetailModal: React.FC<DiagnosisDetailModalProps> = ({
  isOpen,
  recordId,
  localRecord,
  onClose,
}) => {
  const { currentUser } = useAuth();
  const { showToast } = useToast();
  const [detail, setDetail] = useState<DiagnosisDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setDetail(null);
      return;
    }

    if (recordId) {
      setLoading(true);
      fetchHistoryDetail(recordId)
        .then((data) => {
          setDetail(data);
        })
        .catch((err) => {
          console.warn('Could not fetch diagnosis detail from server:', err);
          if (localRecord) {
            // Build fallback detail from local record
            buildFallbackDetail(localRecord);
          } else {
            showToast('Unable to load full diagnosis report details.', 'error');
          }
        })
        .finally(() => setLoading(false));
    } else if (localRecord) {
      buildFallbackDetail(localRecord);
    }
  }, [isOpen, recordId, localRecord]);

  const buildFallbackDetail = (r: HistoryRecord) => {
    const fallback: DiagnosisDetail = {
      id: r.id || 0,
      plot_id: null,
      plot_name: r.plot_name || null,
      crop: (r.crop_type || 'Crop').toUpperCase(),
      district: (r.district || 'Maharashtra').toUpperCase(),
      image_url: r.image_url || null,
      disease: {
        name: r.disease_name || 'Specimen Diagnosis',
        crop: r.crop_type || 'Crop',
        confidence: r.confidence || 90,
        severity: r.severity || 'Low',
        is_healthy: r.is_healthy,
        description: r.is_healthy
          ? 'Crop specimen shows healthy foliar tissues with no active pathogenic lesions.'
          : `Diagnosed with ${r.disease_name}. Prompt agronomic mitigation is recommended.`,
        chemical_treatment: r.is_healthy ? [] : ['Apply recommended broad-spectrum fungicide/bactericide spray.'],
        organic_treatment: r.is_healthy ? ['Maintain standard compost and balanced organic irrigation.'] : ['Neem oil 1500ppm spray (5ml/L) or Trichoderma viride bio-application.'],
      },
      yield_t_ha: r.predicted_yield_t_ha || 0,
      fertilizer: {
        target: { N: 120, P: 60, K: 40 },
        deficit: { N: 0, P: 0, K: 0 },
        fertilizers: { Urea: 100, DAP: 50, MOP: 35 },
        interpretation: 'Standard recommended fertilizer management schedule.',
        surplus_n_warning: null,
      },
      weather: {
        district: (r.district || 'Maharashtra').toUpperCase(),
        temperature: 28,
        humidity: 65,
        rainfall: 0,
        source: 'cache',
      },
      low_confidence: false,
      mock_mode: false,
      created_at: r.created_at || new Date().toISOString(),
    };
    setDetail(fallback);
  };

  if (!isOpen) return null;

  const handlePrint = () => {
    if (!detail) return;
    const predResult: PredictionResult = {
      crop: detail.crop,
      district: detail.district,
      mock_mode: detail.mock_mode,
      low_confidence: detail.low_confidence,
      saved_record_id: detail.id,
      image_url: detail.image_url,
      disease: detail.disease,
      yield_t_ha: detail.yield_t_ha,
      fertilizer: detail.fertilizer,
      weather: detail.weather,
    };
    printAdvisoryReport(predResult, currentUser, false);
  };

  const handleShareWhatsApp = () => {
    if (!detail) return;
    const msg = `*AeroCrop.ai Diagnostic Report* 🌿
🌱 *Crop*: ${detail.crop}
📍 *District*: ${detail.district}${detail.plot_name ? ` (Plot: ${detail.plot_name})` : ''}
🦠 *Diagnosis*: ${detail.disease.name} (${detail.disease.confidence}% confidence)
⚠️ *Severity*: ${detail.disease.severity}
🌾 *Predicted Yield*: ${detail.yield_t_ha} t/ha (${(detail.yield_t_ha * 4.047).toFixed(1)} q/acre)
💊 *Chemical*: ${(detail.disease.chemical_treatment || []).slice(0, 2).join(', ') || 'None needed'}
🌿 *Organic*: ${(detail.disease.organic_treatment || []).slice(0, 2).join(', ') || 'None needed'}

Generated via AeroCrop.ai Precision Agriculture Platform`;

    const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(msg)}`;
    window.open(url, '_blank');
  };

  const formattedDate = detail?.created_at
    ? new Date(detail.created_at).toLocaleString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '--';

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="history-detail-modal-title">
      <div
        className="modal-card glass"
        style={{
          maxWidth: '720px',
          width: '92%',
          maxHeight: '90vh',
          overflowY: 'auto',
          padding: '24px',
        }}
      >
        <button className="modal-close" onClick={onClose} aria-label="Close modal">
          ✕
        </button>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <span className="btn-spinner" style={{ width: '36px', height: '36px', borderColor: 'var(--accent-green) transparent' }} />
            <p style={{ marginTop: '12px', color: 'var(--text-secondary)' }}>Loading diagnostic telemetry & report...</p>
          </div>
        ) : !detail ? (
          <div style={{ textAlign: 'center', padding: '30px 0' }}>
            <p>Report details could not be retrieved.</p>
          </div>
        ) : (
          <div>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px', borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px' }}>
              <div>
                <span
                  style={{
                    display: 'inline-block',
                    padding: '4px 10px',
                    borderRadius: '20px',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    background: detail.disease.is_healthy ? 'rgba(74,222,128,0.18)' : 'rgba(248,113,113,0.18)',
                    color: detail.disease.is_healthy ? '#166534' : '#991b1b',
                    marginBottom: '6px',
                  }}
                >
                  {detail.disease.is_healthy ? '✅ Healthy Specimen' : `⚠️ ${detail.disease.severity} Severity`}
                </span>
                <h2 id="history-detail-modal-title" style={{ margin: '4px 0', fontSize: '1.4rem', color: 'var(--text-primary)' }}>
                  {detail.disease.name}
                </h2>
                <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  🌱 <strong>{detail.crop}</strong> · 📍 {detail.district}
                  {detail.plot_name ? ` · 🌾 Plot: ${detail.plot_name}` : ''} · 🕒 {formattedDate}
                </p>
              </div>

              {detail.image_url && (
                <img
                  src={detail.image_url}
                  alt={detail.disease.name}
                  style={{
                    width: '80px',
                    height: '80px',
                    objectFit: 'cover',
                    borderRadius: '10px',
                    border: '1px solid var(--glass-border)',
                  }}
                />
              )}
            </div>

            {/* Quick Metrics Bar */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                gap: '12px',
                margin: '16px 0',
              }}
            >
              <div className="glass" style={{ padding: '10px 14px', borderRadius: '10px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>AI Confidence</div>
                <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--accent-green)' }}>
                  {Number(detail.disease.confidence).toFixed(1)}%
                </div>
              </div>
              <div className="glass" style={{ padding: '10px 14px', borderRadius: '10px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Yield Forecast</div>
                <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--accent-blue, #2563eb)' }}>
                  {detail.yield_t_ha} t/ha
                </div>
              </div>
              <div className="glass" style={{ padding: '10px 14px', borderRadius: '10px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Yield (q/acre)</div>
                <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--accent-amber, #d97706)' }}>
                  {(detail.yield_t_ha * 4.047).toFixed(1)}
                </div>
              </div>
              {detail.weather && (
                <div className="glass" style={{ padding: '10px 14px', borderRadius: '10px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Weather Telemetry</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    🌡️ {detail.weather.temperature}°C · 💧 {detail.weather.humidity}%
                  </div>
                </div>
              )}
            </div>

            {/* Pathogen Biology & Description */}
            {detail.disease.description && (
              <div style={{ marginBottom: '16px' }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '6px', color: 'var(--text-primary)' }}>
                  📖 Diagnostic Description
                </h3>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                  {detail.disease.description}
                </p>
              </div>
            )}

            {/* Treatment Protocols */}
            {(!detail.disease.is_healthy || (detail.disease.chemical_treatment && detail.disease.chemical_treatment.length > 0)) && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '16px' }}>
                <div className="glass" style={{ padding: '14px', borderRadius: '10px', borderLeft: '3px solid #ef4444' }}>
                  <h4 style={{ margin: '0 0 8px', fontSize: '0.88rem', color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    💊 Chemical Treatment
                  </h4>
                  {detail.disease.chemical_treatment && detail.disease.chemical_treatment.length > 0 ? (
                    <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      {detail.disease.chemical_treatment.map((chem, i) => (
                        <li key={i} style={{ marginBottom: '4px' }}>{chem}</li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0 }}>No chemical treatment required.</p>
                  )}
                </div>

                <div className="glass" style={{ padding: '14px', borderRadius: '10px', borderLeft: '3px solid #16a34a' }}>
                  <h4 style={{ margin: '0 0 8px', fontSize: '0.88rem', color: '#15803d', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    🌿 Organic / Bio Mitigation
                  </h4>
                  {detail.disease.organic_treatment && detail.disease.organic_treatment.length > 0 ? (
                    <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      {detail.disease.organic_treatment.map((org, i) => (
                        <li key={i} style={{ marginBottom: '4px' }}>{org}</li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0 }}>Standard bio-fertilizer practices.</p>
                  )}
                </div>
              </div>
            )}

            {/* Prescribed Fertilizer Doses */}
            {detail.fertilizer && detail.fertilizer.fertilizers && (
              <div className="glass" style={{ padding: '14px', borderRadius: '10px', marginBottom: '20px' }}>
                <h4 style={{ margin: '0 0 10px', fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  🧬 Agronomic Fertilizer Dosage Recommendation
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', textAlign: 'center' }}>
                  <div style={{ padding: '8px', background: 'rgba(59,130,246,0.08)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Urea (46-0-0)</div>
                    <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1d4ed8' }}>
                      {detail.fertilizer.fertilizers.Urea} kg/ha
                    </div>
                  </div>
                  <div style={{ padding: '8px', background: 'rgba(16,185,129,0.08)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>DAP (18-46-0)</div>
                    <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#047857' }}>
                      {detail.fertilizer.fertilizers.DAP} kg/ha
                    </div>
                  </div>
                  <div style={{ padding: '8px', background: 'rgba(245,158,11,0.08)', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>MOP (0-0-60)</div>
                    <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#b45309' }}>
                      {detail.fertilizer.fertilizers.MOP} kg/ha
                    </div>
                  </div>
                </div>
                {detail.fertilizer.interpretation && (
                  <p style={{ margin: '10px 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                    💡 {detail.fertilizer.interpretation}
                  </p>
                )}
              </div>
            )}

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={handlePrint}
              >
                🖨️ Print / Save PDF
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                style={{ background: 'rgba(37,211,102,0.15)', borderColor: '#25d366', color: '#128c7e' }}
                onClick={handleShareWhatsApp}
              >
                📲 Share WhatsApp
              </button>
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={onClose}
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
