import React from 'react';
import { DiseaseClassItem } from '../../types';

interface DiseaseDetailModalProps {
  isOpen: boolean;
  disease: DiseaseClassItem | null;
  onClose: () => void;
  onDiagnoseCrop?: (crop: string) => void;
}

export const DiseaseDetailModal: React.FC<DiseaseDetailModalProps> = ({
  isOpen,
  disease,
  onClose,
  onDiagnoseCrop,
}) => {
  if (!isOpen || !disease) return null;

  const handleDiagnose = () => {
    onClose();
    if (onDiagnoseCrop) {
      onDiagnoseCrop(disease.crop);
    }
  };

  const getSeverityStyle = (sev: string) => {
    const s = (sev || '').toLowerCase();
    if (s === 'critical' || s === 'high') {
      return { bg: 'rgba(239, 68, 68, 0.15)', border: '#ef4444', text: '#b91c1c' };
    }
    if (s === 'moderate') {
      return { bg: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b', text: '#b45309' };
    }
    return { bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981', text: '#15803d' };
  };

  const sevStyle = getSeverityStyle(disease.severity);

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="disease-modal-title">
      <div
        className="modal-card glass"
        style={{
          maxWidth: '680px',
          width: '92%',
          maxHeight: '90vh',
          overflowY: 'auto',
          padding: '24px',
        }}
      >
        <button className="modal-close" onClick={onClose} aria-label="Close modal">
          ✕
        </button>

        {/* Header */}
        <div style={{ borderBottom: '1px solid var(--glass-border)', paddingBottom: '16px', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '8px' }}>
            <span
              style={{
                display: 'inline-block',
                padding: '3px 10px',
                borderRadius: '16px',
                fontSize: '0.78rem',
                fontWeight: 700,
                background: sevStyle.bg,
                border: `1px solid ${sevStyle.border}`,
                color: sevStyle.text,
              }}
            >
              {disease.is_healthy ? '✅ Healthy Profile' : `⚠️ ${disease.severity} Severity`}
            </span>
            <span
              style={{
                display: 'inline-block',
                padding: '3px 10px',
                borderRadius: '16px',
                fontSize: '0.78rem',
                fontWeight: 600,
                background: 'rgba(59, 130, 246, 0.1)',
                border: '1px solid rgba(59, 130, 246, 0.3)',
                color: '#1d4ed8',
              }}
            >
              🌱 {disease.crop.toUpperCase()}
            </span>
          </div>

          <h2 id="disease-modal-title" style={{ margin: 0, fontSize: '1.4rem', color: 'var(--text-primary)' }}>
            {disease.is_healthy ? '✅ ' : '🦠 '}
            {disease.name}
          </h2>
        </div>

        {/* Pathology & Description */}
        <div style={{ marginBottom: '18px' }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
            📖 Pathological Overview & Symptoms
          </h3>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
            {disease.description || 'Comprehensive agronomic taxonomy records for this pathogen specimen.'}
          </p>
        </div>

        {/* Treatments Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px', marginBottom: '20px' }}>
          {/* Chemical Treatment */}
          <div
            className="glass"
            style={{
              padding: '14px',
              borderRadius: '10px',
              borderLeft: '4px solid #ef4444',
              background: 'rgba(254, 242, 242, 0.3)',
            }}
          >
            <h4 style={{ margin: '0 0 8px', fontSize: '0.9rem', color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '6px' }}>
              💊 Chemical Treatment Protocols
            </h4>
            {disease.chemical_treatment && disease.chemical_treatment.length > 0 ? (
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {disease.chemical_treatment.map((chem, i) => (
                  <li key={i} style={{ marginBottom: '5px' }}>{chem}</li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0 }}>
                No chemical fungicide / pesticide spray required for healthy foliage.
              </p>
            )}
          </div>

          {/* Organic Treatment */}
          <div
            className="glass"
            style={{
              padding: '14px',
              borderRadius: '10px',
              borderLeft: '4px solid #16a34a',
              background: 'rgba(240, 253, 244, 0.3)',
            }}
          >
            <h4 style={{ margin: '0 0 8px', fontSize: '0.9rem', color: '#15803d', display: 'flex', alignItems: 'center', gap: '6px' }}>
              🌿 Organic & Bio-Mitigation Methods
            </h4>
            {disease.organic_treatment && disease.organic_treatment.length > 0 ? (
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {disease.organic_treatment.map((org, i) => (
                  <li key={i} style={{ marginBottom: '5px' }}>{org}</li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0 }}>
                Maintain balanced microbial soil health and optimal irrigation drainage.
              </p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onClose}
          >
            Close
          </button>
          {onDiagnoseCrop && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleDiagnose}
            >
              🚀 Diagnose {disease.crop} Now
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
