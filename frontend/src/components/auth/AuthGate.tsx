import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useI18n } from '../../context/I18nContext';
import { useToast } from '../../context/ToastContext';
import { sendEmailOtp } from '../../api/auth';
import { fetchDistricts } from '../../api/weather';
import { ShieldCheck, Mail, Lock, User as UserIcon, MapPin, Sparkles, CheckCircle2, ArrowRight, RefreshCw, Smartphone } from 'lucide-react';

export const AuthGate: React.FC = () => {
  const { login, loginWithOtp, registerWithOtp } = useAuth();
  const { language, setLanguage, t } = useI18n();
  const { showToast } = useToast();

  const [activeTab, setActiveTab] = useState<'signin' | 'signup'>('signin');
  const [signInMode, setSignInMode] = useState<'password' | 'otp'>('password');
  const [districts, setDistricts] = useState<string[]>([]);

  // Sign In Form States
  const [loginIdentifier, setLoginIdentifier] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginOtp, setLoginOtp] = useState('');
  const [isSubmittingLogin, setIsSubmittingLogin] = useState(false);

  // Sign Up Form States
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regOtp, setRegOtp] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regPhone, setRegPhone] = useState('');
  const [regDistrict, setRegDistrict] = useState('');
  const [regVillage, setRegVillage] = useState('');
  const [isSubmittingRegister, setIsSubmittingRegister] = useState(false);

  // OTP Management States
  const [otpSentForRegister, setOtpSentForRegister] = useState(false);
  const [otpSentForLogin, setOtpSentForLogin] = useState(false);
  const [isSendingOtp, setIsSendingOtp] = useState(false);
  const [regCooldown, setRegCooldown] = useState(0);
  const [loginCooldown, setLoginCooldown] = useState(0);

  // Fetch districts on mount
  useEffect(() => {
    fetchDistricts()
      .then((res) => setDistricts(res.districts))
      .catch(() => setDistricts(['pune', 'nagpur', 'nashik', 'amravati', 'kolhapur', 'aurangabad', 'solapur']));
  }, []);

  // Cooldown countdown timers
  useEffect(() => {
    if (regCooldown <= 0) return;
    const interval = setInterval(() => setRegCooldown((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(interval);
  }, [regCooldown]);

  useEffect(() => {
    if (loginCooldown <= 0) return;
    const interval = setInterval(() => setLoginCooldown((c) => Math.max(0, c - 1)), 1000);
    return () => clearInterval(interval);
  }, [loginCooldown]);

  // Request OTP for Sign Up
  const handleSendRegisterOtp = async () => {
    const cleanEmail = regEmail.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      showToast('Please enter a valid email address first.', 'warning');
      return;
    }
    if (regCooldown > 0) return;

    setIsSendingOtp(true);
    try {
      const res = await sendEmailOtp({ email: cleanEmail, purpose: 'register' });
      setOtpSentForRegister(true);
      setRegCooldown(res.cooldown_seconds || 60);
      showToast(`Verification code sent to ${cleanEmail}! Please check your Inbox and Spam/Junk folder.`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to send verification code.', 'error');
    } finally {
      setIsSendingOtp(false);
    }
  };

  // Request OTP for Sign In
  const handleSendLoginOtp = async () => {
    const cleanEmail = loginIdentifier.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      showToast('Please enter your registered email address.', 'warning');
      return;
    }
    if (loginCooldown > 0) return;

    setIsSendingOtp(true);
    try {
      const res = await sendEmailOtp({ email: cleanEmail, purpose: 'login' });
      setOtpSentForLogin(true);
      setLoginCooldown(res.cooldown_seconds || 60);
      showToast(`Login OTP sent to ${cleanEmail}! Please check your Inbox and Spam/Junk folder.`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to send login code.', 'error');
    } finally {
      setIsSendingOtp(false);
    }
  };

  // Submit Sign In
  const handleSignInSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (signInMode === 'password') {
      if (!loginIdentifier.trim() || !loginPassword) {
        showToast('Please enter both identifier and password.', 'warning');
        return;
      }
      setIsSubmittingLogin(true);
      try {
        await login({ identifier: loginIdentifier.trim(), password: loginPassword });
      } catch (err: any) {
        showToast(err.message || 'Login failed. Please verify credentials.', 'error');
      } finally {
        setIsSubmittingLogin(false);
      }
    } else {
      if (!loginIdentifier.trim() || !loginOtp.trim()) {
        showToast('Please enter your email and the 6-digit verification code.', 'warning');
        return;
      }
      if (loginOtp.trim().length !== 6) {
        showToast('Please enter a 6-digit numeric OTP code.', 'warning');
        return;
      }
      setIsSubmittingLogin(true);
      try {
        await loginWithOtp({ email: loginIdentifier.trim(), otp: loginOtp.trim() });
      } catch (err: any) {
        showToast(err.message || 'OTP verification failed.', 'error');
      } finally {
        setIsSubmittingLogin(false);
      }
    }
  };

  // Submit Sign Up with OTP
  const handleSignUpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanEmail = regEmail.trim().toLowerCase();
    if (!cleanEmail || !cleanEmail.includes('@') || !cleanEmail.includes('.')) {
      showToast('A valid email address is compulsory.', 'warning');
      return;
    }
    if (!otpSentForRegister && (!regOtp.trim() || regOtp.trim().length !== 6)) {
      showToast(`Sending 6-digit verification code to ${cleanEmail}...`, 'info');
      await handleSendRegisterOtp();
      return;
    }
    if (!regOtp.trim() || regOtp.trim().length !== 6) {
      showToast('Please enter the 6-digit verification code sent to your email.', 'warning');
      return;
    }
    if (regPassword.length < 6) {
      showToast('Password must be at least 6 characters.', 'warning');
      return;
    }
    if (!regDistrict.trim()) {
      showToast('Please select your district from the dropdown.', 'warning');
      return;
    }

    setIsSubmittingRegister(true);
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
    } catch (err: any) {
      showToast(err.message || 'Registration failed. Please check your verification code.', 'error');
    } finally {
      setIsSubmittingRegister(false);
    }
  };

  return (
    <div className="auth-gate-root" style={{
      minHeight: '100vh',
      width: '100%',
      maxWidth: '100%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(ellipse at 50% 10%, #153828 0%, #0a1712 55%, #050d0a 100%)',
      padding: '24px 16px',
      boxSizing: 'border-box',
      overflowX: 'hidden',
    }}>
      <div style={{
        width: '100%',
        maxWidth: '520px',
        background: 'rgba(19, 34, 28, 0.88)',
        backdropFilter: 'blur(16px)',
        border: '1px solid rgba(56, 161, 105, 0.35)',
        borderRadius: '20px',
        boxShadow: '0 20px 50px rgba(0, 0, 0, 0.65)',
        padding: '32px 28px',
        boxSizing: 'border-box',
      }}>
        {/* Top Header & Language Picker */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '1.75rem' }}>🌱</span>
            <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.5px' }}>
              AeroCrop<span style={{ color: '#38a169' }}>.ai</span>
            </span>
          </div>

          <div style={{ display: 'flex', gap: '4px' }}>
            {(['en', 'mr', 'hi'] as const).map((lang) => (
              <button
                key={lang}
                type="button"
                onClick={() => setLanguage(lang)}
                style={{
                  background: language === lang ? '#38a169' : 'rgba(255, 255, 255, 0.08)',
                  color: language === lang ? '#ffffff' : '#94a3b8',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {lang === 'en' ? 'EN' : lang === 'mr' ? 'मरा' : 'हिंदी'}
              </button>
            ))}
          </div>
        </div>

        {/* Tagline & Subheading */}
        <div style={{ marginBottom: '24px' }}>
          <h2 style={{ margin: '0 0 6px 0', fontSize: '1.35rem', fontWeight: 700, color: '#f1f5f9' }}>
            {activeTab === 'signin' ? 'Sign in to your farm portal' : 'Create your farmer account'}
          </h2>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>
            Access multimodal disease diagnostics, yield forecasts, and precision agricultural insights.
          </p>
        </div>

        {/* Feature Highlights Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '22px' }}>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.74rem', background: 'rgba(56, 161, 105, 0.15)', color: '#68d391', padding: '4px 8px', borderRadius: '12px', border: '1px solid rgba(56, 161, 105, 0.25)' }}>
            <Sparkles size={12} /> 134 Crop Diseases
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.74rem', background: 'rgba(56, 161, 105, 0.15)', color: '#68d391', padding: '4px 8px', borderRadius: '12px', border: '1px solid rgba(56, 161, 105, 0.25)' }}>
            <ShieldCheck size={12} /> Email OTP Protected
          </span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.74rem', background: 'rgba(56, 161, 105, 0.15)', color: '#68d391', padding: '4px 8px', borderRadius: '12px', border: '1px solid rgba(56, 161, 105, 0.25)' }}>
            <CheckCircle2 size={12} /> Mandi Market Rates
          </span>
        </div>

        {/* Main Tab Switcher */}
        <div className="auth-tabs" style={{ marginBottom: '20px' }}>
          <button
            type="button"
            className={`auth-tab ${activeTab === 'signin' ? 'active' : ''}`}
            onClick={() => setActiveTab('signin')}
            style={{ padding: '10px 16px', fontSize: '0.92rem' }}
          >
            {t('sign_in_btn')}
          </button>
          <button
            type="button"
            className={`auth-tab ${activeTab === 'signup' ? 'active' : ''}`}
            onClick={() => setActiveTab('signup')}
            style={{ padding: '10px 16px', fontSize: '0.92rem' }}
          >
            {t('create_account_btn')}
          </button>
        </div>

        {/* SIGN IN VIEW */}
        {activeTab === 'signin' && (
          <form onSubmit={handleSignInSubmit}>
            {/* Sign in mode selector */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
              <button
                type="button"
                onClick={() => setSignInMode('password')}
                style={{
                  flex: 1,
                  padding: '7px 10px',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  background: signInMode === 'password' ? 'rgba(56, 161, 105, 0.2)' : 'transparent',
                  color: signInMode === 'password' ? '#68d391' : '#94a3b8',
                  border: signInMode === 'password' ? '1px solid #38a169' : '1px solid rgba(255, 255, 255, 0.1)',
                }}
              >
                Password Login
              </button>
              <button
                type="button"
                onClick={() => setSignInMode('otp')}
                style={{
                  flex: 1,
                  padding: '7px 10px',
                  borderRadius: '8px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  background: signInMode === 'otp' ? 'rgba(56, 161, 105, 0.2)' : 'transparent',
                  color: signInMode === 'otp' ? '#68d391' : '#94a3b8',
                  border: signInMode === 'otp' ? '1px solid #38a169' : '1px solid rgba(255, 255, 255, 0.1)',
                }}
              >
                Email OTP Login
              </button>
            </div>

            <div className="form-group" style={{ marginBottom: '16px' }}>
              <label htmlFor="gate-login-id" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '6px' }}>
                <Mail size={14} color="#38a169" />
                {signInMode === 'password' ? 'Email or Mobile Number' : 'Registered Email Address'}
              </label>
              <input
                id="gate-login-id"
                type={signInMode === 'password' ? 'text' : 'email'}
                required
                placeholder={signInMode === 'password' ? 'farmer@example.com or 9876543210' : 'farmer@example.com'}
                value={loginIdentifier}
                onChange={(e) => setLoginIdentifier(e.target.value)}
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  background: 'rgba(10, 25, 18, 0.7)',
                  border: '1px solid rgba(56, 161, 105, 0.3)',
                  color: '#f8fafc',
                  padding: '11px 14px',
                  borderRadius: '10px',
                  fontSize: '0.92rem',
                }}
              />
            </div>

            {signInMode === 'password' ? (
              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label htmlFor="gate-login-pw" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '6px' }}>
                  <Lock size={14} color="#38a169" />
                  {t('password')}
                </label>
                <input
                  id="gate-login-pw"
                  type="password"
                  required
                  placeholder="••••••••"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  style={{
                    width: '100%',
                    boxSizing: 'border-box',
                    background: 'rgba(10, 25, 18, 0.7)',
                    border: '1px solid rgba(56, 161, 105, 0.3)',
                    color: '#f8fafc',
                    padding: '11px 14px',
                    borderRadius: '10px',
                    fontSize: '0.92rem',
                  }}
                />
              </div>
            ) : (
              <div className="form-group" style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <label htmlFor="gate-login-otp" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#cbd5e1', margin: 0 }}>
                    <ShieldCheck size={14} color="#38a169" />
                    6-Digit Verification Code
                  </label>
                  <button
                    type="button"
                    onClick={handleSendLoginOtp}
                    disabled={isSendingOtp || loginCooldown > 0}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: loginCooldown > 0 ? '#94a3b8' : '#38a169',
                      fontSize: '0.78rem',
                      fontWeight: 600,
                      cursor: loginCooldown > 0 ? 'default' : 'pointer',
                      textDecoration: 'underline',
                      padding: 0,
                    }}
                  >
                    {isSendingOtp ? 'Sending...' : loginCooldown > 0 ? `Resend in ${loginCooldown}s` : otpSentForLogin ? 'Resend Code' : 'Send Code to Email'}
                  </button>
                </div>
                <input
                  id="gate-login-otp"
                  type="text"
                  required
                  maxLength={6}
                  placeholder="e.g. 123456"
                  value={loginOtp}
                  onChange={(e) => setLoginOtp(e.target.value.replace(/\D/g, ''))}
                  style={{
                    width: '100%',
                    boxSizing: 'border-box',
                    background: 'rgba(10, 25, 18, 0.7)',
                    border: '1px solid rgba(56, 161, 105, 0.3)',
                    color: '#34d399',
                    fontFamily: 'monospace',
                    fontSize: '1.25rem',
                    letterSpacing: '4px',
                    textAlign: 'center',
                    padding: '11px 14px',
                    borderRadius: '10px',
                  }}
                />
              </div>
            )}

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={isSubmittingLogin}
              style={{
                width: '100%',
                padding: '13px',
                borderRadius: '10px',
                fontWeight: 700,
                fontSize: '0.96rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                background: '#38a169',
                color: '#ffffff',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              {isSubmittingLogin ? (
                <RefreshCw size={18} className="animate-spin" />
              ) : (
                <>
                  <span>{signInMode === 'password' ? t('sign_in_btn') : 'Verify Code & Sign In'}</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>
        )}

        {/* SIGN UP VIEW (OTP VERIFIED) */}
        {activeTab === 'signup' && (
          <form onSubmit={handleSignUpSubmit}>
            <div className="form-group" style={{ marginBottom: '14px' }}>
              <label htmlFor="gate-reg-name" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '6px' }}>
                <UserIcon size={14} color="#38a169" />
                {t('full_name')} *
              </label>
              <input
                id="gate-reg-name"
                type="text"
                required
                placeholder="e.g. Ramesh Patil"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  background: 'rgba(10, 25, 18, 0.7)',
                  border: '1px solid rgba(56, 161, 105, 0.3)',
                  color: '#f8fafc',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  fontSize: '0.9rem',
                }}
              />
            </div>

            {/* Compulsory Email with OTP Trigger */}
            <div className="form-group" style={{ marginBottom: '14px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <label htmlFor="gate-reg-email" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#cbd5e1', margin: 0 }}>
                  <Mail size={14} color="#38a169" />
                  Compulsory Email Address *
                </label>
                <button
                  type="button"
                  onClick={handleSendRegisterOtp}
                  disabled={isSendingOtp || regCooldown > 0 || !regEmail.includes('@')}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: regCooldown > 0 || !regEmail.includes('@') ? '#64748b' : '#38a169',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: regCooldown > 0 || !regEmail.includes('@') ? 'default' : 'pointer',
                    textDecoration: 'underline',
                    padding: 0,
                  }}
                >
                  {isSendingOtp ? 'Sending...' : regCooldown > 0 ? `Resend in ${regCooldown}s` : otpSentForRegister ? 'Resend Code' : 'Send Verification Code'}
                </button>
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  id="gate-reg-email"
                  type="email"
                  required
                  placeholder="farmer@example.com"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  style={{
                    flex: 1,
                    boxSizing: 'border-box',
                    background: 'rgba(10, 25, 18, 0.7)',
                    border: '1px solid rgba(56, 161, 105, 0.3)',
                    color: '#f8fafc',
                    padding: '10px 14px',
                    borderRadius: '10px',
                    fontSize: '0.9rem',
                  }}
                />
                {!otpSentForRegister && (
                  <button
                    type="button"
                    onClick={handleSendRegisterOtp}
                    disabled={isSendingOtp || !regEmail.includes('@')}
                    style={{
                      background: '#234e38',
                      color: '#68d391',
                      border: '1px solid #38a169',
                      borderRadius: '10px',
                      padding: '0 14px',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {isSendingOtp ? 'Sending...' : 'Get OTP'}
                  </button>
                )}
              </div>
            </div>

            {/* OTP Verification Code Input */}
            <div className="form-group" style={{ marginBottom: '14px' }}>
              <label htmlFor="gate-reg-otp" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '6px' }}>
                <ShieldCheck size={14} color="#38a169" />
                6-Digit Email Verification Code *
              </label>
              <input
                id="gate-reg-otp"
                type="text"
                required={otpSentForRegister}
                maxLength={6}
                placeholder={otpSentForRegister ? "Enter 6-digit code" : "Click Get OTP or Register to receive code"}
                value={regOtp}
                onChange={(e) => setRegOtp(e.target.value.replace(/\D/g, ''))}
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  background: 'rgba(10, 25, 18, 0.7)',
                  border: '1px solid rgba(56, 161, 105, 0.3)',
                  color: '#34d399',
                  fontFamily: 'monospace',
                  fontSize: '1.2rem',
                  letterSpacing: '4px',
                  textAlign: 'center',
                  padding: '10px 14px',
                  borderRadius: '10px',
                }}
              />
              <span style={{ display: 'block', marginTop: '4px', fontSize: '0.74rem', color: '#94a3b8' }}>
                {language === 'mr'
                  ? 'कोड थेट ईमेल इनबॉक्समध्ये पाठवला आहे. (काही सेकंदात न दिसल्यास स्पॅम/जंक फोल्डरही तपासा)'
                  : language === 'hi'
                  ? 'कोड सीधे ईमेल इनबॉक्स में भेजा गया है। (कुछ सेकंड में न दिखने पर स्पैम/जंक फ़ोल्डर भी जांचें)'
                  : 'Code sent directly to your inbox. (If delayed, also check Spam/Junk folder)'}
              </span>
            </div>

            {/* Password */}
            <div className="form-group" style={{ marginBottom: '14px' }}>
              <label htmlFor="gate-reg-pw" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '6px' }}>
                <Lock size={14} color="#38a169" />
                {t('password_min6')} *
              </label>
              <input
                id="gate-reg-pw"
                type="password"
                required
                minLength={6}
                placeholder="••••••••"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  background: 'rgba(10, 25, 18, 0.7)',
                  border: '1px solid rgba(56, 161, 105, 0.3)',
                  color: '#f8fafc',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  fontSize: '0.9rem',
                }}
              />
            </div>

            {/* District & Village */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '14px' }}>
              <div className="form-group">
                <label htmlFor="gate-reg-district" style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.82rem', color: '#cbd5e1', marginBottom: '4px' }}>
                  <MapPin size={12} color="#38a169" />
                  {t('district_label')} *
                </label>
                <select
                  id="gate-reg-district"
                  required
                  value={regDistrict}
                  onChange={(e) => setRegDistrict(e.target.value)}
                  style={{
                    width: '100%',
                    boxSizing: 'border-box',
                    background: '#0d2017',
                    border: !regDistrict ? '1px solid rgba(234, 179, 8, 0.6)' : '1px solid rgba(56, 161, 105, 0.3)',
                    color: !regDistrict ? '#94a3b8' : '#f8fafc',
                    padding: '9px 10px',
                    borderRadius: '8px',
                    fontSize: '0.86rem',
                  }}
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
                <label htmlFor="gate-reg-village" style={{ fontSize: '0.82rem', color: '#cbd5e1', marginBottom: '4px', display: 'block' }}>
                  {t('village_label')}
                </label>
                <input
                  id="gate-reg-village"
                  type="text"
                  placeholder="e.g. Haveli"
                  value={regVillage}
                  onChange={(e) => setRegVillage(e.target.value)}
                  style={{
                    width: '100%',
                    boxSizing: 'border-box',
                    background: 'rgba(10, 25, 18, 0.7)',
                    border: '1px solid rgba(56, 161, 105, 0.3)',
                    color: '#f8fafc',
                    padding: '9px 10px',
                    borderRadius: '8px',
                    fontSize: '0.86rem',
                  }}
                />
              </div>
            </div>

            {/* Mobile Phone (Optional) */}
            <div className="form-group" style={{ marginBottom: '20px' }}>
              <label htmlFor="gate-reg-phone" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: '#cbd5e1', marginBottom: '4px' }}>
                <Smartphone size={13} color="#38a169" />
                {t('phone_number')} (Optional)
              </label>
              <input
                id="gate-reg-phone"
                type="tel"
                placeholder="10-digit mobile number"
                value={regPhone}
                onChange={(e) => setRegPhone(e.target.value)}
                style={{
                  width: '100%',
                  boxSizing: 'border-box',
                  background: 'rgba(10, 25, 18, 0.7)',
                  border: '1px solid rgba(56, 161, 105, 0.3)',
                  color: '#f8fafc',
                  padding: '9px 12px',
                  borderRadius: '8px',
                  fontSize: '0.86rem',
                }}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={isSubmittingRegister}
              style={{
                width: '100%',
                padding: '13px',
                borderRadius: '10px',
                fontWeight: 700,
                fontSize: '0.96rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                background: '#38a169',
                color: '#ffffff',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              {isSubmittingRegister ? (
                <RefreshCw size={18} className="animate-spin" />
              ) : (
                <>
                  <span>{otpSentForRegister ? 'Verify OTP & Create Account' : 'Send Verification OTP & Continue'}</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
