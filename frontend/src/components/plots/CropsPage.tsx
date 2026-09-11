import React, { useState } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { PlotCard } from './PlotCard';
import { AddPlotModal } from './AddPlotModal';
import { EditPlotModal } from './EditPlotModal';
import { deleteFarmerPlot } from '../../api/plots';
import { FarmPlot } from '../../types';

interface CropsPageProps {
  onQuickDiagnose: (plot: FarmPlot) => void;
}

export const CropsPage: React.FC<CropsPageProps> = ({ onQuickDiagnose }) => {
  const { t } = useI18n();
  const { userPlots, isAuthenticated, openAuthModal, refreshPlots } = useAuth();
  const { showToast } = useToast();
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingPlot, setEditingPlot] = useState<FarmPlot | null>(null);

  const handleAddPlotClick = () => {
    if (!isAuthenticated) {
      showToast('Please sign in to register and manage your farm plots.', 'info');
      openAuthModal('login');
      return;
    }
    setIsAddModalOpen(true);
  };

  const handleDeletePlot = async (plotId: number) => {
    if (!window.confirm('Are you sure you want to delete this farm plot?')) {
      return;
    }
    try {
      await deleteFarmerPlot(plotId);
      showToast('Farm plot deleted successfully.', 'info');
      await refreshPlots();
    } catch (err: any) {
      showToast(`Failed to delete plot: ${err.message}`, 'error');
    }
  };

  return (
    <section className="page-container" aria-labelledby="heading-crops">
      <header className="page-header">
        <div>
          <h1 id="heading-crops">{t('my_crops_title')}</h1>
          <p className="page-subtitle">{t('my_crops_subtitle')}</p>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleAddPlotClick}
        >
          <span aria-hidden="true">➕</span>
          <span>{t('add_plot_btn')}</span>
        </button>
      </header>

      {/* Plots Grid */}
      <div className="plots-grid">
        {!isAuthenticated ? (
          <div
            className="card glass"
            style={{ gridColumn: '1/-1', textAlign: 'center', padding: '48px 24px' }}
          >
            <p style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🌾</p>
            <h3>{t('signin_manage_plots')}</h3>
            <p style={{ color: 'var(--text-secondary)', margin: '8px 0 24px' }}>
              {t('signin_plots_desc')}
            </p>
            <button
              type="button"
              className="btn btn-primary"
              style={{ maxWidth: '240px', margin: '0 auto' }}
              onClick={() => openAuthModal('login')}
            >
              {t('signin_register_btn')}
            </button>
          </div>
        ) : userPlots.length === 0 ? (
          <div
            className="card glass"
            style={{ gridColumn: '1/-1', textAlign: 'center', padding: '48px 24px' }}
          >
            <p style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🌾</p>
            <h3>{t('no_plots_yet')}</h3>
            <p style={{ color: 'var(--text-secondary)', margin: '8px 0 24px' }}>
              {t('no_plots_desc')}
            </p>
            <button
              type="button"
              className="btn btn-primary"
              style={{ maxWidth: '240px', margin: '0 auto' }}
              onClick={() => setIsAddModalOpen(true)}
            >
              {t('add_first_plot')}
            </button>
          </div>
        ) : (
          userPlots.map((plot) => (
            <PlotCard
              key={plot.id}
              plot={plot}
              onQuickDiagnose={onQuickDiagnose}
              onEdit={(p) => setEditingPlot(p)}
              onDelete={handleDeletePlot}
            />
          ))
        )}
      </div>

      <AddPlotModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSuccess={() => {}}
      />

      <EditPlotModal
        isOpen={!!editingPlot}
        plot={editingPlot}
        onClose={() => setEditingPlot(null)}
        onSuccess={() => {}}
      />
    </section>
  );
};
