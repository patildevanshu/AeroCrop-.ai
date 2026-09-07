import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { User, FarmPlot } from '../types';
import {
  getAuthToken,
  setAuthToken,
  clearAuthToken,
} from '../api/client';
import {
  loginFarmer,
  registerFarmer,
  getCurrentUser,
  LoginPayload,
  RegisterPayload,
} from '../api/auth';
import { fetchFarmerPlots } from '../api/plots';
import { useToast } from './ToastContext';
import { useI18n } from './I18nContext';

interface AuthContextType {
  currentUser: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  userPlots: FarmPlot[];
  refreshPlots: () => Promise<void>;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  isAuthModalOpen: boolean;
  authModalTab: 'login' | 'register';
  openAuthModal: (tab?: 'login' | 'register') => void;
  closeAuthModal: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userPlots, setUserPlots] = useState<FarmPlot[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState<boolean>(false);
  const [authModalTab, setAuthModalTab] = useState<'login' | 'register'>('login');

  const { showToast } = useToast();
  const { setLanguage } = useI18n();

  const refreshPlots = useCallback(async () => {
    if (!getAuthToken()) {
      setUserPlots([]);
      return;
    }
    try {
      const data = await fetchFarmerPlots();
      setUserPlots(data.plots || []);
    } catch (err) {
      console.warn('Failed to load farmer plots:', err);
    }
  }, []);

  const checkAuth = useCallback(async () => {
    const token = getAuthToken();
    if (!token) {
      setIsLoading(false);
      return;
    }
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
      const savedLang = localStorage.getItem('aerocrop_lang');
      if (!savedLang && user.preferred_language) {
        setLanguage(user.preferred_language);
      }
      await refreshPlots();
    } catch {
      clearAuthToken();
      setCurrentUser(null);
      setUserPlots([]);
    } finally {
      setIsLoading(false);
    }
  }, [refreshPlots, setLanguage]);

  useEffect(() => {
    checkAuth();

    const handleUnauthorized = () => {
      setCurrentUser(null);
      setUserPlots([]);
    };

    window.addEventListener('aerocrop:unauthorized', handleUnauthorized);
    return () => {
      window.removeEventListener('aerocrop:unauthorized', handleUnauthorized);
    };
  }, [checkAuth]);

  const login = async (payload: LoginPayload) => {
    const data = await loginFarmer(payload);
    setAuthToken(data.access_token);
    setCurrentUser(data.user);
    const savedLang = localStorage.getItem('aerocrop_lang');
    if (!savedLang && data.user.preferred_language) {
      setLanguage(data.user.preferred_language);
    }
    setIsAuthModalOpen(false);
    showToast(`Welcome back, ${data.user.full_name}!`, 'success');
    await refreshPlots();
  };

  const register = async (payload: RegisterPayload) => {
    const data = await registerFarmer(payload);
    setAuthToken(data.access_token);
    setCurrentUser(data.user);
    if (data.user.preferred_language) {
      setLanguage(data.user.preferred_language);
    }
    setIsAuthModalOpen(false);
    showToast(`Account created! Welcome, ${data.user.full_name}!`, 'success');
    await refreshPlots();
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: getAuthToken() ? { Authorization: `Bearer ${getAuthToken()}` } : {},
      });
    } catch {
      // Ignore network errors on logout
    }
    clearAuthToken();
    setCurrentUser(null);
    setUserPlots([]);
    showToast('Logged out successfully.', 'info');
  };

  const openAuthModal = (tab: 'login' | 'register' = 'login') => {
    setAuthModalTab(tab);
    setIsAuthModalOpen(true);
  };

  const closeAuthModal = () => {
    setIsAuthModalOpen(false);
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        isAuthenticated: !!currentUser,
        isLoading,
        userPlots,
        refreshPlots,
        login,
        register,
        logout,
        isAuthModalOpen,
        authModalTab,
        openAuthModal,
        closeAuthModal,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
