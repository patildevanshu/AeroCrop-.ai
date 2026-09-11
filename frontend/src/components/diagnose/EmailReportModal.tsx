import React, { useState, useEffect } from 'react';
import { PredictionResult } from '../../types';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { sendEmailReport } from '../../api/predict';

interface EmailReportModalProps {
  isOpen: boolean;
  result: PredictionResult;
  onClose: () => void;
}

export const EmailReportModal: React.FC<EmailReportModalProps> = ({
  isOpen,
  result,
  onClose,
}) => {
  const { currentUser } = useAuth();
  const { showToast } = useToast();

  const [email, setEmail] = useState('');
  const [farmerName, setFarmerName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (currentUser) {
      if (currentUser.email) setEmail(currentUser.email);
      if (currentUser.full_name) setFarmerName(currentUser.full_name);
    }
  }, [currentUser, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !email.includes('@')) {
      showToast('Please enter a valid email address.', 'warning');
      return;
    }

    setIsSubmitting(true);
    try {
      await sendEmailReport({
        email: email.trim(),
        name: farmerName.trim() || 'Farmer',
        crop: result.crop,
        district: result.district,
        disease: result.disease,
        fertilizer: result.fertilizer,
        yield_t_ha: result.yield_t_ha,
        weather: result.weather,
      });

      showToast(`📧 Report is sent on email also (${email.trim()})!`, 'success');
      onClose();
    } catch (err: any) {
      showToast(`Failed to send email report: ${err.message}`, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="email-modal-title">
      <div className="modal-card glass" style={{ maxWidth: '480px', width: '90%' }}>
        <button className="modal-close" onClick={onClose} aria-label="Close modal">
          ✕
        </button>

        <h2 id="email-modal-title" className="card-title">
          📧 <span>Email Crop Advisory PDF</span>
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '4px 0 16px' }}>
          Dispatch an agronomic prescription & PMFBY damage report directly to your inbox.
        </p>

        <div
          className="glass"
          style={{
            padding: '10px 14px',
            borderRadius: '8px',
            marginBottom: '16px',
            fontSize: '0.85rem',
            background: 'rgba(16, 185, 129, 0.06)',
            border: '1px solid rgba(16, 185, 129, 0.2)',
          }}
        >
          <div>🌱 <strong>Crop:</strong> {result.crop.toUpperCase()} · 📍 {result.district.toUpperCase()}</div>
          <div>🦠 <strong>Diagnosis:</strong> {result.disease.name} ({result.disease.severity})</div>
          <div>🌾 <strong>Yield Forecast:</strong> {result.yield_t_ha} t/ha</div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="report-farmer-name">Farmer Name</label>
            <input
              id="report-farmer-name"
              type="text"
              placeholder="e.g. Ramesh Patil"
              value={farmerName}
              onChange={(e) => setFarmerName(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="report-email">Recipient Email Address</label>
            <input
              id="report-email"
              type="email"
              required
              placeholder="e.g. farmer@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ flex: 1 }}
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ flex: 1 }}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="btn-spinner" />
              ) : (
                <span className="btn-text">Send PDF Report</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
