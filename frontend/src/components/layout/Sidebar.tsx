import React, { useState } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { Language } from '../../types';
import { ProfileModal } from '../auth/ProfileModal';

export type PageTab = 'diagnose' | 'crops' | 'dashboard' | 'diseases' | 'about';

interface SidebarProps {
  activeTab: PageTab;
  onTabChange: (tab: PageTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const { language, setLanguage, t } = useI18n();
  const { currentUser, isAuthenticated, logout, openAuthModal } = useAuth();
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  const navItems: { id: PageTab; labelKey: string; icon: string }[] = [
    { id: 'diagnose', labelKey: 'nav_diagnose', icon: '🔬' },
    { id: 'crops', labelKey: 'nav_my_crops', icon: '🌱' },
    { id: 'dashboard', labelKey: 'nav_dashboard', icon: '📊' },
    { id: 'diseases', labelKey: 'nav_diseases', icon: '🦠' },
    { id: 'about', labelKey: 'nav_about', icon: 'ℹ️' },
  ];

  const handleLangChange = (lang: Language) => {
    setLanguage(lang);
  };

  return (
    <aside className="sidebar" role="navigation" aria-label="Main navigation">
      {/* Brand Logo */}
      <div className="sidebar-logo">
        <div className="logo-icon" aria-hidden="true">🌿</div>
        <div className="logo-text">
          <span className="logo-name">AeroCrop</span>
          <span className="logo-ai">.ai</span>
        </div>
      </div>

      {/* Language Switcher */}
      <div className="lang-toggle" role="group" aria-label="Language selection">
        <button
          className={`lang-btn ${language === 'en' ? 'active' : ''}`}
          onClick={() => handleLangChange('en')}
          aria-pressed={language === 'en'}
        >
          EN
        </button>
        <button
          className={`lang-btn ${language === 'mr' ? 'active' : ''}`}
          onClick={() => handleLangChange('mr')}
          aria-pressed={language === 'mr'}
        >
          मराठी
        </button>
        <button
          className={`lang-btn ${language === 'hi' ? 'active' : ''}`}
          onClick={() => handleLangChange('hi')}
          aria-pressed={language === 'hi'}
        >
          हिंदी
        </button>
      </div>

      {/* User Auth Section */}
      <div className="sidebar-auth">
        {!isAuthenticated ? (
          <div>
            <button
              className="btn btn-primary btn-sm btn-full"
              onClick={() => openAuthModal('login')}
            >
              <span>👤</span> <span>{t('btn_login_register')}</span>
            </button>
          </div>
        ) : (
          <div className="user-card glass">
            <div
              className="user-avatar"
              aria-hidden="true"
              style={{ cursor: 'pointer' }}
              onClick={() => setIsProfileModalOpen(true)}
              title="Click to view profile & settings"
            >
              🌾
            </div>
            <div
              className="user-info"
              style={{ cursor: 'pointer' }}
              onClick={() => setIsProfileModalOpen(true)}
              title="Click to edit profile & change password"
            >
              <p className="user-name" title={currentUser?.full_name}>
                {currentUser?.full_name}
              </p>
              <p className="user-location">
                📍 {currentUser?.district ? currentUser.district.charAt(0).toUpperCase() + currentUser.district.slice(1) : 'Maharashtra'}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '4px' }}>
              <button
                className="btn-icon-sm"
                onClick={() => setIsProfileModalOpen(true)}
                title="Profile & Settings"
                aria-label="Profile & Settings"
              >
                ⚙️
              </button>
              <button
                className="btn-icon-sm"
                onClick={logout}
                title="Log out"
                aria-label="Log out"
              >
                🚪
              </button>
            </div>
          </div>
        )}
      </div>

      <ProfileModal
        isOpen={isProfileModalOpen}
        onClose={() => setIsProfileModalOpen(false)}
      />

      {/* Navigation Links */}
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => onTabChange(item.id)}
            aria-current={activeTab === item.id ? 'page' : undefined}
          >
            <span className="nav-icon" aria-hidden="true">{item.icon}</span>
            <span className="nav-label">{t(item.labelKey)}</span>
          </button>
        ))}
      </nav>

      {/* Footer Badge */}
      <div className="sidebar-footer">
        <div className="model-badge">
          <span className="badge-dot" aria-hidden="true" />
          <span>ResNet-18 · Multi-Crop</span>
        </div>
        <p className="sidebar-ver">v2.0.0 — Maharashtra Multi-Tenant</p>
        <div style={{ marginTop: '8px', fontSize: '0.74rem' }}>
          <a
            href="mailto:support@devanshupatil.tech"
            style={{
              color: 'var(--text-secondary)',
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              transition: 'color 0.2s',
            }}
            title="Technical & Agronomy Support"
          >
            ✉️ support@devanshupatil.tech
          </a>
        </div>
      </div>
    </aside>
  );
};
