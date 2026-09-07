import React, { useState, useEffect, useCallback } from 'react';
import { useI18n } from '../../context/I18nContext';
import { useAuth } from '../../context/AuthContext';
import { fetchCropProgress } from '../../api/history';
import { CropProgressPlot, AnalysisProgressItem } from '../../types';

interface CropProgressCardProps {
  onQuickDiagnose?: (plotId?: number | null) => void;
}

const CROP_ICONS: Record<string, string> = {
  cotton: '🌱',
  sugarcane: '🎋',
  banana: '🍌',
  turmeric: '🌿',
  haldi: '🌿',
  onion: '🧅',
  wheat: '🌾',
  maize: '🌽',
  rice: '🍚',
  potato: '🥔',
  tomato: '🍅',
  pepper: '🌶️',
  apple: '🍎',
  grape: '🍇',
  orange: '🍊',
  peach: '🍑',
  strawberry: '🍓',
  soybean: '🫘',
  cherry: '🍒',
  blueberry: '🫐',
  squash: '🎃',
  raspberry: '🫐',
};

export const CropProgressCard: React.FC<CropProgressCardProps> = ({ onQuickDiagnose }) => {
  const { t } = useI18n();
  const { isAuthenticated, openAuthModal } = useAuth();

  const [crops, setCrops] = useState<CropProgressPlot[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedPlotId, setExpandedPlotId] = useState<number | string | null>(null);

  const loadProgress = useCallback(async () => {
    if (!isAuthenticated) {
      setCrops([]);
      return;
    }
    setIsLoading(true);
    try {
      const data = await fetchCropProgress();
      setCrops(data.crops || []);
      if (data.crops && data.crops.length > 0) {
        // Expand the first plot with analyses by default
        const firstWithAnalyses = data.crops.find((c) => c.total_analyses > 0);
        setExpandedPlotId(firstWithAnalyses ? (firstWithAnalyses.plot_id ?? firstWithAnalyses.crop_type) : (data.crops[0].plot_id ?? data.crops[0].crop_type));
      }
    } catch (err) {
      console.warn('Failed to load crop progress:', err);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    loadProgress();
  }, [loadProgress]);

  const getTrendBadge = (trend: string) => {
    switch (trend) {
      case 'recovered':
        return {
          icon: '✅',
          text: t('trend_recovered') || 'Fully Recovered',
          cls: 'trend-badge-recovered',
        };
      case 'improving':
        return {
          icon: '📈',
          text: t('trend_improving') || 'Health Improving',
          cls: 'trend-badge-improving',
        };
      case 'deteriorating':
        return {
          icon: '⚠️',
          text: t('trend_deteriorating') || 'Action Needed',
          cls: 'trend-badge-deteriorating',
        };
      case 'stable':
        return {
          icon: '🟡',
          text: t('trend_stable') || 'Stable',
          cls: 'trend-badge-stable',
        };
      case 'baseline':
        return {
          icon: '🔵',
          text: t('trend_baseline') || 'Baseline Recorded',
          cls: 'trend-badge-baseline',
        };
      default:
        return {
          icon: '⚪',
          text: t('trend_no_analyses') || 'Awaiting Analysis',
          cls: 'trend-badge-none',
        };
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'var(--accent-green)';
    if (score >= 50) return 'var(--accent-amber)';
    return 'var(--accent-red)';
  };

  const togglePlotExpand = (id: number | string) => {
    setExpandedPlotId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="card glass crop-progress-card">
      <div className="crop-progress-header">
        <div>
          <h2 className="card-title" style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span aria-hidden="true">🌱</span>
            <span>{t('crop_progress_title') || 'Crop Health Progress per Analysis'}</span>
          </h2>
          <p className="crop-progress-subtitle">
            {t('crop_progress_subtitle') || 'Longitudinal crop health, pathology evolution, and yield trajectory across consecutive field diagnoses.'}
          </p>
        </div>
        {isAuthenticated && (
          <button
            type="button"
            className="btn-clear"
            onClick={loadProgress}
            title="Refresh Progress"
          >
            🔄 Refresh
          </button>
        )}
      </div>

      {!isAuthenticated ? (
        <div className="crop-progress-empty">
          <p className="crop-empty-icon">🌾</p>
          <h3>Sign in to Track Crop Progress</h3>
          <p className="crop-empty-desc">
            Sign in to view longitudinal crop health trajectories, disease recovery tracking, and yield forecasts across your analyses.
          </p>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => openAuthModal('login')}
          >
            Farmer Sign In
          </button>
        </div>
      ) : isLoading ? (
        <div className="crop-progress-loading">
          <p>Analyzing crop health trajectories…</p>
        </div>
      ) : crops.length === 0 ? (
        <div className="crop-progress-empty">
          <p className="crop-empty-icon">🌱</p>
          <h3>No Crop Progress Records Yet</h3>
          <p className="crop-empty-desc">
            Register farm plots or run leaf diagnoses to start tracking health and yield progress over time.
          </p>
          {onQuickDiagnose && (
            <button
              type="button"
              className="btn btn-primary btn-sm"
              onClick={() => onQuickDiagnose(null)}
            >
              Analyze a Crop Now
            </button>
          )}
        </div>
      ) : (
        <div className="crop-progress-list">
          {crops.map((cropPlot) => {
            const plotKey = cropPlot.plot_id ?? cropPlot.crop_type;
            const isExpanded = expandedPlotId === plotKey;
            const icon = CROP_ICONS[cropPlot.crop_type.toLowerCase()] || '🌱';
            const trendInfo = getTrendBadge(cropPlot.trend);
            const healthColor = getHealthColor(cropPlot.health_score);

            return (
              <div key={plotKey} className="crop-plot-item glass">
                {/* Plot Summary Header */}
                <div
                  className="crop-plot-summary"
                  onClick={() => togglePlotExpand(plotKey)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      togglePlotExpand(plotKey);
                    }
                  }}
                  aria-expanded={isExpanded}
                >
                  <div className="crop-plot-info">
                    <span className="crop-plot-avatar" aria-hidden="true">
                      {icon}
                    </span>
                    <div>
                      <div className="crop-plot-title-row">
                        <h3 className="crop-plot-name">
                          {cropPlot.plot_name}
                        </h3>
                        <span className="crop-badge">
                          {cropPlot.crop_type.toUpperCase()}
                        </span>
                        <span className={`trend-badge ${trendInfo.cls}`}>
                          {trendInfo.icon} {trendInfo.text}
                        </span>
                      </div>
                      <p className="crop-plot-subinfo">
                        {cropPlot.area_acres} {t('unit_acre')} · {cropPlot.soil_type} ·{' '}
                        <strong>{cropPlot.total_analyses}</strong> {t('analyses_count')}
                      </p>
                    </div>
                  </div>

                  <div className="crop-plot-right">
                    {/* Health Score Meter */}
                    <div className="health-score-container">
                      <div className="health-score-dial">
                        <span className="health-score-num" style={{ color: healthColor }}>
                          {cropPlot.health_score}%
                        </span>
                        <span className="health-score-label">Health</span>
                      </div>
                      <div className="health-score-bar-bg">
                        <div
                          className="health-score-bar-fill"
                          style={{
                            width: `${cropPlot.health_score}%`,
                            backgroundColor: healthColor,
                          }}
                        />
                      </div>
                    </div>

                    <span className="crop-expand-toggle" aria-hidden="true">
                      {isExpanded ? '▲' : '▼'}
                    </span>
                  </div>
                </div>

                {/* Expanded Progression View */}
                {isExpanded && (
                  <div className="crop-progression-panel">
                    {cropPlot.analyses.length === 0 ? (
                      <div className="crop-no-analyses">
                        <p>{t('no_analyses_yet') || 'No diagnoses recorded yet for this crop. Run your first analysis to track progression.'}</p>
                        {onQuickDiagnose && (
                          <button
                            type="button"
                            className="btn btn-secondary btn-sm"
                            onClick={() => onQuickDiagnose(cropPlot.plot_id)}
                          >
                            Analyze Now
                          </button>
                        )}
                      </div>
                    ) : (
                      <>
                        <div className="analyses-timeline-header">
                          <h4>
                            Analysis Progression Timeline ({cropPlot.analyses.length} Recorded)
                          </h4>
                          {onQuickDiagnose && (
                            <button
                              type="button"
                              className="btn btn-primary btn-xs"
                              onClick={() => onQuickDiagnose(cropPlot.plot_id)}
                            >
                              + New Analysis
                            </button>
                          )}
                        </div>

                        {/* Timeline Steps */}
                        <div className="analyses-timeline">
                          {cropPlot.analyses.map((analysis: AnalysisProgressItem, index: number) => {
                            const prevAnalysis = index > 0 ? cropPlot.analyses[index - 1] : null;
                            const yieldDiff = prevAnalysis
                              ? +(analysis.predicted_yield_t_ha - prevAnalysis.predicted_yield_t_ha).toFixed(2)
                              : null;

                            return (
                              <div key={analysis.id} className="timeline-node glass">
                                <div className="timeline-step-badge">
                                  #{analysis.analysis_number}
                                </div>

                                <div className="timeline-content">
                                  <div className="timeline-top-row">
                                    <div className="timeline-diag-head">
                                      <span className="timeline-status-icon">
                                        {analysis.is_healthy ? '✅' : '🦠'}
                                      </span>
                                      <strong>{analysis.disease_name}</strong>
                                      <span className={`severity-badge severity-${analysis.severity.toLowerCase()}`}>
                                        {analysis.severity}
                                      </span>
                                    </div>
                                    <span className="timeline-date">{analysis.date_display}</span>
                                  </div>

                                  <div className="timeline-stats-row">
                                    <span className="timeline-chip">
                                      🎯 Confidence: <strong>{analysis.confidence}%</strong>
                                    </span>
                                    <span className="timeline-chip">
                                      🌾 Yield: <strong>{analysis.predicted_yield_t_ha} t/ha</strong>
                                      {yieldDiff !== null && (
                                        <span
                                          className={`yield-diff ${
                                            yieldDiff >= 0 ? 'yield-up' : 'yield-down'
                                          }`}
                                        >
                                          {yieldDiff >= 0 ? ` (+${yieldDiff})` : ` (${yieldDiff})`}
                                        </span>
                                      )}
                                    </span>
                                    {analysis.weather_temp !== null && analysis.weather_temp !== undefined && (
                                      <span className="timeline-chip">
                                        ⛅ {analysis.weather_temp}°C · {analysis.weather_hum}% Hum
                                      </span>
                                    )}
                                    {analysis.fertilizers?.urea_kg ? (
                                      <span className="timeline-chip">
                                        🧪 Urea: {analysis.fertilizers.urea_kg} kg
                                      </span>
                                    ) : null}
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
