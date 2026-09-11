import React, { useState } from 'react';
import { ToastProvider } from './context/ToastContext';
import { I18nProvider } from './context/I18nContext';
import { AuthProvider } from './context/AuthContext';
import { AppShell } from './components/layout/AppShell';
import { PageTab } from './components/layout/Sidebar';
import { AuthModal } from './components/auth/AuthModal';

import { DiagnosePage } from './components/diagnose/DiagnosePage';
import { CropsPage } from './components/plots/CropsPage';
import { DashboardPage } from './components/dashboard/DashboardPage';
import { DiseaseDBPage } from './components/diseases/DiseaseDBPage';
import { AboutPage } from './components/about/AboutPage';
import { FarmPlot } from './types';

const MainApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<PageTab>('diagnose');
  const [activePlotId, setActivePlotId] = useState<string>('');
  const [activeCrop, setActiveCrop] = useState<string>('');

  const handleQuickDiagnose = (plot: FarmPlot) => {
    setActivePlotId(plot.id.toString());
    setActiveCrop(plot.crop_type);
    setActiveTab('diagnose');
  };

  const handleQuickDiagnoseFromId = (plotId?: number | null) => {
    setActivePlotId(plotId ? plotId.toString() : '');
    setActiveTab('diagnose');
  };

  const handleDiagnoseCrop = (cropName: string) => {
    setActiveCrop(cropName);
    setActivePlotId('');
    setActiveTab('diagnose');
  };

  return (
    <AppShell activeTab={activeTab} onTabChange={setActiveTab}>
      {activeTab === 'diagnose' && <DiagnosePage initialPlotId={activePlotId} initialCrop={activeCrop} />}
      {activeTab === 'crops' && <CropsPage onQuickDiagnose={handleQuickDiagnose} />}
      {activeTab === 'dashboard' && <DashboardPage onQuickDiagnose={handleQuickDiagnoseFromId} />}
      {activeTab === 'diseases' && <DiseaseDBPage onDiagnoseCrop={handleDiagnoseCrop} />}
      {activeTab === 'about' && <AboutPage />}

      <AuthModal />
    </AppShell>
  );
};

export const App: React.FC = () => {
  return (
    <ToastProvider>
      <I18nProvider>
        <AuthProvider>
          <MainApp />
        </AuthProvider>
      </I18nProvider>
    </ToastProvider>
  );
};

export default App;
