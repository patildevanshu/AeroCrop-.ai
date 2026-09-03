import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useI18n } from '../../context/I18nContext';
import { useToast } from '../../context/ToastContext';
import { fetchDistricts } from '../../api/weather';

export const AuthModal: React.FC = () => {
  const { isAuthModalOpen, authModalTab, openAuthModal, closeAuthModal, login, register } = useAuth();
  const { language, t } = useI18n();
  const { showToast } = useToast();

  // Login form state
  const [loginId, setLoginId] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Register form state
  const [regName, setRegName] = useState('');
  const [regPhone, setRegPhone] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regDistrict, setRegDistrict] = useState('pune');
  const [regVillage, setRegVillage] = useState('');
  const [districts, setDistricts] = useState<string[]>([]);

  useEffect(() => {
    if (isAuthModalOpen && districts.length === 0) {
      fetchDistricts()
        .then((res) => setDistricts(res.districts))
        .catch(() => setDistricts(['pune', 'nagpur', 'nashik', 'amravati', 'kolhapur']));
    }
  }, [isAuthModalOpen, districts.length]);

  if (!isAuthModalOpen) return null;

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginId.trim() || !loginPassword) {
      showToast('Please enter both identifier and password.', 'warning');
      return;
    }
    setIsSubmitting(true);
    try {
      await login({ identifier: loginId.trim(), password: loginPassword });
      setLoginId('');
      setLoginPassword('');
    } catch (err: any) {
      showToast(err.message || 'Login failed', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!regPhone.trim() && !regEmail.trim()) {
      showToast('Please provide at least a mobile number or email.', 'warning');
      return;
    }
    if (regPassword.length < 6) {
      showToast('Password must be at least 6 characters long.', 'warning');
      return;
    }
    setIsSubmitting(true);
    try {
      await register({
        full_name: regName.trim(),
        phone_number: regPhone.trim() || null,
        email: regEmail.trim() || null,
        password: regPassword,
        district: regDistrict || 'pune',
        taluka_village: regVillage.trim() || null,
        preferred_language: language,
      });
      setRegName('');
      setRegPhone('');
      setRegEmail('');
      setRegPassword('');
      setRegVillage('');
    } catch (err: any) {
      showToast(err.message || 'Registration failed', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="auth-modal-title">
      <div className="modal-card glass">
        <button className="modal-close" onClick={closeAuthModal} aria-label="Close modal">
          ✕
        </button>

        <div className="auth-tabs">
          <button
            className={`auth-tab ${authModalTab === 'login' ? 'active' : ''}`}
            onClick={() => openAuthModal('login')}
          >
            {t('sign_in_btn')}
          </button>
          <button
            className={`auth-tab ${authModalTab === 'register' ? 'active' : ''}`}
            onClick={() => openAuthModal('register')}
          >
            {t('create_account_btn')}
          </button>
        </div>

        {authModalTab === 'login' ? (
          <form onSubmit={handleLoginSubmit}>
            <div className="form-group">
              <label htmlFor="login-id">{t('login_id_label')}</label>
              <input
                id="login-id"
                type="text"
                required
                placeholder="e.g. 9876543210 or farmer@gmail.com"
                value={loginId}
                onChange={(e) => setLoginId(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="login-password">{t('password')}</label>
              <input
                id="login-password"
                type="password"
                required
                placeholder="••••••••"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary btn-full mt-2"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="btn-spinner" />
              ) : (
                <span className="btn-text">{t('sign_in_btn')}</span>
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegisterSubmit}>
            <div className="form-group">
              <label htmlFor="reg-name">{t('full_name')}</label>
              <input
                id="reg-name"
                type="text"
                required
                placeholder="e.g. Ramesh Patil"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="reg-phone">{t('phone_number')}</label>
                <input
                  id="reg-phone"
                  type="tel"
                  placeholder="10-digit number"
                  value={regPhone}
                  onChange={(e) => setRegPhone(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="reg-email">{t('email_optional')}</label>
                <input
                  id="reg-email"
                  type="email"
                  placeholder="name@domain.com"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="reg-password">{t('password_min6')}</label>
              <input
                id="reg-password"
                type="password"
                required
                minLength={6}
                placeholder="••••••••"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="reg-district">{t('district_label')}</label>
                <select
                  id="reg-district"
                  value={regDistrict}
                  onChange={(e) => setRegDistrict(e.target.value)}
                >
                  {districts.map((d) => (
                    <option key={d} value={d}>
                      {d.charAt(0).toUpperCase() + d.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="reg-village">{t('village_label')}</label>
                <input
                  id="reg-village"
                  type="text"
                  placeholder="e.g. Haveli"
                  value={regVillage}
                  onChange={(e) => setRegVillage(e.target.value)}
                />
              </div>
            </div>
            <button
              type="submit"
              className="btn btn-primary btn-full mt-2"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <span className="btn-spinner" />
              ) : (
                <span className="btn-text">{t('create_account_btn')}</span>
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
