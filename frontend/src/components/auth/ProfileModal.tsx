import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { useI18n } from '../../context/I18nContext';
import { updateProfile, changeFarmerPassword } from '../../api/auth';
import { setAuthToken } from '../../api/client';
import { Language } from '../../types';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ProfileModal: React.FC<ProfileModalProps> = ({ isOpen, onClose }) => {
  const { currentUser, updateCurrentUser } = useAuth();
  const { showToast } = useToast();
  const { t, setLanguage } = useI18n();

  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile');

  // Profile Form State
  const [fullName, setFullName] = useState('');
  const [district, setDistrict] = useState('pune');
  const [talukaVillage, setTalukaVillage] = useState('');
  const [prefLang, setPrefLang] = useState<Language>('mr');
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);

  // Password Form State
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  useEffect(() => {
    if (currentUser) {
      setFullName(currentUser.full_name || '');
      setDistrict(currentUser.district || 'pune');
      setTalukaVillage(currentUser.taluka_village || '');
      setPrefLang((currentUser.preferred_language as Language) || 'mr');
    }
  }, [currentUser, isOpen]);

  if (!isOpen || !currentUser) return null;

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) {
      showToast('Farmer name cannot be empty.', 'warning');
      return;
    }

    setIsUpdatingProfile(true);
    try {
      const res = await updateProfile({
        full_name: fullName.trim(),
        district,
        taluka_village: talukaVillage.trim() || null,
        preferred_language: prefLang,
      });

      updateCurrentUser(res.user);
      setLanguage(prefLang);
      showToast(t('profile_updated', 'Profile updated successfully!'), 'success');
      onClose();
    } catch (err: any) {
      showToast(err.message || 'Could not update profile', 'error');
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentPassword) {
      showToast('Please enter your current password.', 'warning');
      return;
    }
    if (newPassword.length < 6) {
      showToast('New password must be at least 6 characters long.', 'warning');
      return;
    }
    if (newPassword !== confirmPassword) {
      showToast('New passwords do not match.', 'error');
      return;
    }

    setIsChangingPassword(true);
    try {
      const res = await changeFarmerPassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      setAuthToken(res.access_token);
      showToast(t('password_changed', 'Password updated successfully!'), 'success');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      onClose();
    } catch (err: any) {
      showToast(err.message || 'Failed to change password', 'error');
    } finally {
      setIsChangingPassword(false);
    }
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="profile-modal-title">
      <div className="modal-card glass" style={{ maxWidth: '520px', width: '92%' }}>
        <button className="modal-close" onClick={onClose} aria-label="Close modal">
          ✕
        </button>

        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <div
            style={{
              width: '46px',
              height: '46px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #10b981, #059669)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.2rem',
              fontWeight: 700,
            }}
          >
            {currentUser.full_name?.charAt(0).toUpperCase() || 'F'}
          </div>
          <div>
            <h2 id="profile-modal-title" style={{ margin: 0, fontSize: '1.3rem', color: 'var(--text-primary)' }}>
              {currentUser.full_name}
            </h2>
            <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              {currentUser.phone_number || currentUser.email || 'Registered Farmer'}
            </p>
          </div>
        </div>

        {/* Tab switcher */}
        <div className="auth-tabs" style={{ marginBottom: '20px' }}>
          <button
            type="button"
            className={`auth-tab ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            👤 {t('profile_tab', 'Farmer Profile')}
          </button>
          <button
            type="button"
            className={`auth-tab ${activeTab === 'password' ? 'active' : ''}`}
            onClick={() => setActiveTab('password')}
          >
            🔒 {t('password_tab', 'Change Password')}
          </button>
        </div>

        {activeTab === 'profile' ? (
          <form onSubmit={handleProfileSubmit}>
            <div className="form-group">
              <label htmlFor="prof-name">{t('full_name', 'Full Name')}</label>
              <input
                id="prof-name"
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="prof-district">{t('district', 'District')}</label>
                <select
                  id="prof-district"
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                >
                  <option value="pune">Pune (पुणे)</option>
                  <option value="nagpur">Nagpur (नागपूर)</option>
                  <option value="nashik">Nashik (नाशिक)</option>
                  <option value="amravati">Amravati (अमरावती)</option>
                  <option value="kolhapur">Kolhapur (कोल्हापूर)</option>
                  <option value="aurangabad">Chhatrapati Sambhajinagar / Aurangabad</option>
                  <option value="solapur">Solapur (सोलापूर)</option>
                  <option value="jalgaon">Jalgaon (जळगाव)</option>
                  <option value="ahmednagar">Ahmednagar (अहमदनगर)</option>
                  <option value="satara">Satara (सातारा)</option>
                  <option value="sangli">Sangli (सांगली)</option>
                  <option value="nanded">Nanded (नांदेड)</option>
                  <option value="yavatmal">Yavatmal (यवतमाळ)</option>
                  <option value="buldhana">Buldhana (बुलढाणा)</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="prof-lang">{t('language', 'Language')}</label>
                <select
                  id="prof-lang"
                  value={prefLang}
                  onChange={(e) => setPrefLang(e.target.value as Language)}
                >
                  <option value="mr">मराठी (Marathi)</option>
                  <option value="hi">हिन्दी (Hindi)</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="prof-village">{t('taluka_village', 'Taluka / Village')}</label>
              <input
                id="prof-village"
                type="text"
                placeholder="e.g. Baramati, Haveli"
                value={talukaVillage}
                onChange={(e) => setTalukaVillage(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ flex: 1 }}
                onClick={onClose}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                style={{ flex: 1 }}
                disabled={isUpdatingProfile}
              >
                {isUpdatingProfile ? <span className="btn-spinner" /> : <span className="btn-text">Save Profile</span>}
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handlePasswordSubmit}>
            <div className="form-group">
              <label htmlFor="curr-pwd">Current Password</label>
              <input
                id="curr-pwd"
                type="password"
                required
                placeholder="••••••••"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="new-pwd">New Password (min 6 characters)</label>
              <input
                id="new-pwd"
                type="password"
                required
                minLength={6}
                placeholder="••••••••"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="conf-pwd">Confirm New Password</label>
              <input
                id="conf-pwd"
                type="password"
                required
                minLength={6}
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ flex: 1 }}
                onClick={onClose}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                style={{ flex: 1 }}
                disabled={isChangingPassword}
              >
                {isChangingPassword ? <span className="btn-spinner" /> : <span className="btn-text">Update Password</span>}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
