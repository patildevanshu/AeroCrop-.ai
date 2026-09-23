import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useI18n } from '../../context/I18nContext';
import { useToast } from '../../context/ToastContext';
import { sendEmailOtp } from '../../api/auth';
import { fetchDistricts } from '../../api/weather';

export const AuthModal: React.FC = () => {
  const { isAuthModalOpen, authModalTab, openAuthModal, closeAuthModal, login, registerWithOtp } = useAuth();
  const { language, t } = useI18n();
  const { showToast } = useToast();

  // Login form state
  const [loginId, setLoginId] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Register form state
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regOtp, setRegOtp] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regPhone, setRegPhone] = useState('');
  const [regDistrict, setRegDistrict] = useState('');
  const [regVillage, setRegVillage] = useState('');
  const [districts, setDistricts] = useState<string[]>([]);

  // OTP state
  const [isSendingOtp, setIsSendingOtp] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (isAuthModalOpen && districts.length === 0) {
      fetchDistricts()
        .then((res) => setDistricts(res.districts))
        .catch(() => setDistricts(['pune', 'nagpur', 'nashik', 'amravati', 'kolhapur']));
    }
  }, [isAuthModalOpen, districts.length]);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => setCooldown((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  if (!isAuthModalOpen) return null;

  const handleSendOtp = async () => {
    const cleanEmail = regEmail.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      showToast('Please enter a valid email address first.', 'warning');
      return;
    }
    if (cooldown > 0) return;

    setIsSendingOtp(true);
    try {
      const res = await sendEmailOtp({ email: cleanEmail, purpose: 'register' });
      setOtpSent(true);
      setCooldown(res.cooldown_seconds || 60);
      showToast(`Verification code sent to ${cleanEmail}! Please check your Inbox and Spam/Junk folder.`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to send verification code.', 'error');
    } finally {
      setIsSendingOtp(false);
    }
  };

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
    const cleanEmail = regEmail.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      showToast('A valid email address is compulsory.', 'warning');
      return;
    }
    if (!otpSent && (!regOtp.trim() || regOtp.trim().length !== 6)) {
      showToast(`Sending 6-digit verification code to ${cleanEmail}...`, 'info');
      await handleSendOtp();
      return;
    }
    if (!regOtp.trim() || regOtp.trim().length !== 6) {
      showToast('Please enter the 6-digit verification code sent to your email.', 'warning');
      return;
    }
    if (regPassword.length < 6) {
      showToast('Password must be at least 6 characters long.', 'warning');
      return;
    }
    if (!regDistrict.trim()) {
      showToast('Please select your district.', 'warning');
      return;
    }
    setIsSubmitting(true);
    try {
      await registerWithOtp({
        full_name: regName.trim(),
        email: cleanEmail,
        otp: regOtp.trim(),
        password: regPassword,
        district: regDistrict.trim().toLowerCase(),
        phone_number: regPhone.trim() || null,
        taluka_village: regVillage.trim() || null,
        preferred_language: language,
      });
      setRegName('');
      setRegEmail('');
      setRegOtp('');
      setRegPassword('');
      setRegPhone('');
      setRegVillage('');
      setOtpSent(false);
    } catch (err: any) {
      showToast(err.message || 'Registration failed', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="auth-modal-title">
      <div className="modal-card glass" style={{ maxWidth: '500px' }}>
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
              <label htmlFor="reg-name">{t('full_name')} *</label>
              <input
                id="reg-name"
                type="text"
                required
                placeholder="e.g. Ramesh Patil"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
              />
            </div>

            <div className="form-group">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <label htmlFor="reg-email" style={{ margin: 0 }}>Compulsory Email Address *</label>
                <button
                  type="button"
                  onClick={handleSendOtp}
                  disabled={isSendingOtp || cooldown > 0 || !regEmail.includes('@')}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: cooldown > 0 || !regEmail.includes('@') ? '#64748b' : '#38a169',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: cooldown > 0 || !regEmail.includes('@') ? 'default' : 'pointer',
                    textDecoration: 'underline',
                    padding: 0,
                  }}
                >
                  {isSendingOtp ? 'Sending...' : cooldown > 0 ? `Resend in ${cooldown}s` : otpSent ? 'Resend Code' : 'Send Code'}
                </button>
              </div>
              <input
                id="reg-email"
                type="email"
                required
                placeholder="name@domain.com"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="reg-otp">6-Digit Email Verification Code *</label>
              <input
                id="reg-otp"
                type="text"
                required={otpSent}
                maxLength={6}
                placeholder="Enter 6-digit code"
                value={regOtp}
                onChange={(e) => setRegOtp(e.target.value.replace(/\D/g, ''))}
                style={{
                  fontFamily: 'monospace',
                  fontSize: '1.15rem',
                  letterSpacing: '3px',
                  textAlign: 'center',
                }}
              />
              {otpSent && (
                <span style={{ display: 'block', marginTop: '4px', fontSize: '0.74rem', color: '#94a3b8', textAlign: 'center' }}>
                  {language === 'mr'
                    ? 'कोड थेट ईमेलवर पाठवला आहे. (न दिसल्यास स्पॅम फोल्डरही तपासा)'
                    : language === 'hi'
                    ? 'कोड सीधे ईमेल पर भेजा गया है। (न दिखने पर स्पैम फ़ोल्डर भी देखें)'
                    : 'Code sent to your email inbox. (Also check Spam folder if delayed)'}
                </span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="reg-password">{t('password_min6')} *</label>
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
                <label htmlFor="reg-district">{t('district_label')} *</label>
                <select
                  id="reg-district"
                  required
                  value={regDistrict}
                  onChange={(e) => setRegDistrict(e.target.value)}
                >
                  <option value="" disabled>
                    {language === 'mr' ? '-- आपला जिल्हा निवडा (आवश्यक) --' : language === 'hi' ? '-- अपना जिला चुनें (अनिवार्य) --' : '-- Select District (Required) --'}
                  </option>
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

            <div className="form-group">
              <label htmlFor="reg-phone">{t('phone_number')} (Optional)</label>
              <input
                id="reg-phone"
                type="tel"
                placeholder="10-digit number"
                value={regPhone}
                onChange={(e) => setRegPhone(e.target.value)}
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
                <span className="btn-text">
                  {otpSent ? 'Verify OTP & Register' : 'Send Verification OTP & Continue'}
                </span>
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
