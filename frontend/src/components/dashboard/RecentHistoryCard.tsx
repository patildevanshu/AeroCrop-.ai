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
            <option value="">All Crops</option>
            <option value="cotton">Cotton</option>
            <option value="wheat">Wheat</option>
            <option value="maize">Maize</option>
            <option value="rice">Rice</option>
            <option value="potato">Potato</option>
            <option value="tomato">Tomato</option>
            <option value="soybean">Soybean</option>
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
          <p className="loading-text">Loading diagnostics…</p>
        ) : records.length === 0 ? (
          <p className="no-history">{t('no_history')}</p>
        ) : (
          records.map((r, idx) => {
            const dateStr = new Date(r.created_at).toLocaleDateString('en-IN', {
              day: '2-digit',
              month: 'short',
              year: 'numeric',
            });
            const timeStr = new Date(r.created_at).toLocaleTimeString('en-IN', {
              hour: '2-digit',
              minute: '2-digit',
            });

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
                  <p className="history-disease">{r.disease_name}</p>
                  <p className="history-meta">
                    {r.crop_type.toUpperCase()} · {r.district.toUpperCase()}
                    {r.plot_name ? ` · Plot: ${r.plot_name}` : ''} · {dateStr} {timeStr}
                  </p>
                  <p className="history-meta">
                    Yield: {r.predicted_yield_t_ha} t/ha · Confidence: {r.confidence.toFixed(1)}%
                  </p>
                </div>
                <span className={`severity-badge ${getSeverityClass(r.severity)}`}>
                  {r.severity}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
