import React, { ReactNode } from 'react';
import { Sidebar, PageTab } from './Sidebar';
import { BackgroundOrbs } from './BackgroundOrbs';

interface AppShellProps {
  activeTab: PageTab;
  onTabChange: (tab: PageTab) => void;
  children: ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ activeTab, onTabChange, children }) => {
  return (
    <>
      <BackgroundOrbs />
      <div className="app-shell">
        <Sidebar activeTab={activeTab} onTabChange={onTabChange} />
        <main className="main-content" role="main">
          {children}
        </main>
      </div>
    </>
  );
};
