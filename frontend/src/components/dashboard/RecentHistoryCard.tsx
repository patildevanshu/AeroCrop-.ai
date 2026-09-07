import React, { useState, useEffect, useCallback } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { fetchFarmerHistory, getLocalHistory, clearLocalHistory } from '../../api/history';
import { HistoryRecord } from '../../types';

export const RecentHistoryCard: React.FC = () => {
  const { t } = useI18n();
  const { isAuthenticated } = useAuth();
  const { showToast } = useToast();

  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [filterCrop, setFilterCrop] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const loadHistory = useCallback(async () => {
    setIsLoading(true);
    if (isAuthenticated) {
      try {
        const data = await fetchFarmerHistory(filterCrop || undefined);
        setRecords(data.records || []);
      } catch (err) {
        console.warn('Failed to load server history:', err);
      } finally {
        setIsLoading(false);
      }
    } else {
      let local = getLocalHistory();
      if (filterCrop) {
        local = local.filter((r) => r.crop_type.toLowerCase() === filterCrop.toLowerCase());
      }
      setRecords(local);
      setIsLoading(false);
    }
  }, [isAuthenticated, filterCrop]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleClear = () => {
    clearLocalHistory();
    if (!isAuthenticated) {
      setRecords([]);
    } else {
      loadHistory();
    }
    showToast('Diagnostic history cleared.', 'info');
  };

  const getSeverityClass = (sev: string) => {
    return `severity-${(sev || 'none').toLowerCase()}`;
  };

  return (
    <div className="card glass dash-card">
      <div className="dash-card-header">
        <h2 className="card-title" style={{ margin: 0 }}>
          <span aria-hidden="true">📋</span>
          <span>{t('recent_diagnostics')}</span>
        </h2>
        <div className="dash-history-actions">
          <select
            className="filter-select-sm"
            value={filterCrop}
            onChange={(e) => setFilterCrop(e.target.value)}
          >
            <option value="">{t('all_crops')}</option>
            <option value="cotton">Cotton (कापूस)</option>
            <option value="sugarcane">Sugarcane (ऊस)</option>
            <option value="banana">Banana (केळी)</option>
            <option value="turmeric">Turmeric (हळद)</option>
            <option value="soybean">Soybean (सोयाबीन)</option>
            <option value="maize">Corn / Maize (मका)</option>
            <option value="rice">Rice (भात)</option>
            <option value="potato">Potato (बटाटा)</option>
            <option value="wheat">Wheat (गहू)</option>
            <option value="onion">Onion (कांदा)</option>
          </select>
          <button
            type="button"
            className="btn-clear"
            onClick={handleClear}
            aria-label="Clear history"
          >
            {t('clear_history')}
          </button>
        </div>
      </div>

      <div className="history-list">
        {isLoading ? (
          <p className="loading-text">{t('loading_diagnostics')}</p>
        ) : (Array.isArray(records) ? records : []).length === 0 ? (
          <p className="no-history">{t('no_history')}</p>
        ) : (
          (Array.isArray(records) ? records : []).map((r, idx) => {
            let dateStr = '--';
            let timeStr = '';
            try {
              if (r.created_at) {
                const d = new Date(r.created_at);
                if (!isNaN(d.getTime())) {
                  dateStr = d.toLocaleDateString('en-IN', {
                    day: '2-digit',
                    month: 'short',
                    year: 'numeric',
                  });
                  timeStr = d.toLocaleTimeString('en-IN', {
                    hour: '2-digit',
                    minute: '2-digit',
                  });
                }
              }
            } catch {
              dateStr = '--';
            }

            const cropName = (r.crop_type || 'Crop').toUpperCase();
            const districtName = (r.district || 'Maharashtra').toUpperCase();
            const confVal = r.confidence != null ? Number(r.confidence).toFixed(1) : '--';
            const yieldVal = r.predicted_yield_t_ha != null ? r.predicted_yield_t_ha : '--';

            return (
              <div key={r.id || idx} className="history-item glass">
                {r.image_url ? (
                  <img
                    src={r.image_url}
                    className="history-thumb"
                    alt="Diagnosed leaf"
                  />
                ) : (
                  <div className="history-icon">
                    {r.is_healthy ? '✅' : '🦠'}
                  </div>
                )}
                <div className="history-body">
                  <p className="history-disease">{r.disease_name || 'Specimen Diagnosis'}</p>
                  <p className="history-meta">
                    {cropName} · {districtName}
                    {r.plot_name ? ` · ${t('plot_label')} ${r.plot_name}` : ''} · {dateStr} {timeStr}
                  </p>
                  <p className="history-meta">
                    {t('yield_label')} {yieldVal} t/ha · {t('confidence_label')} {confVal}%
                  </p>
                </div>
                <span className={`severity-badge ${getSeverityClass(r.severity)}`}>
                  {r.severity || 'None'}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
