import React, { useState, useEffect, useMemo } from 'react';
import { useI18n } from '../../context/I18nContext';

interface AnalyzingOverlayProps {
  isOpen: boolean;
  selectedFile: File | null;
  crop: string;
  district: string;
}

interface TelemetryStep {
  agency: 'ISRO' | 'NASA' | 'AEROCROP' | 'ICAR' | 'OPEN-METEO';
  icon: string;
  title: string;
  detail: string;
  color: string;
}

export const AnalyzingOverlay: React.FC<AnalyzingOverlayProps> = ({
  isOpen,
  selectedFile,
  crop,
  district,
}) => {
  const { language } = useI18n();

  const [currentStepIdx, setCurrentStepIdx] = useState(0);
  const [progress, setProgress] = useState(12);
  const [terminalLogs, setTerminalLogs] = useState<string[]>([]);

  // Create object URL for uploaded preview
  const imagePreview = useMemo(() => {
    if (!selectedFile) return null;
    return URL.createObjectURL(selectedFile);
  }, [selectedFile]);

  // Clean up object URL on unmount or file change
  useEffect(() => {
    return () => {
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);

  // Telemetry stages that simulate real NASA, ISRO, and Deep Learning inference
  const steps: TelemetryStep[] = useMemo(() => {
    const cropLabel = crop === 'auto' ? 'Cultivated Crop' : crop.toUpperCase();
    const districtLabel = district ? district.toUpperCase() : 'MAHARASHTRA';

    return [
      {
        agency: 'ISRO',
        icon: '🛰️',
        title: `ISRO Bhuvan Multi-Spectral Satellite Telemetry`,
        detail: `Locking INSAT-3DR geo-orbital sensor coordinates over ${districtLabel} (${cropLabel} agrarian grid)...`,
        color: '#38bdf8',
      },
      {
        agency: 'NASA',
        icon: '🛰️',
        title: `NASA POWER Agro-Climatology Satellite Grid`,
        detail: `Acquiring surface solar insolation & thermal radiant flux telemetry from NASA Langley Research Center...`,
        color: '#60a5fa',
      },
      {
        agency: 'OPEN-METEO',
        icon: '📡',
        title: `Meteorological Telemetry Ingestion`,
        detail: `Calibrating ambient temperature, relative humidity, and precipitation vectors for ${districtLabel}...`,
        color: '#34d399',
      },
      {
        agency: 'AEROCROP',
        icon: '🔬',
        title: `ResNet-18 Deep Foliar Pathology Scan`,
        detail: `Extracting 512-dimensional cellular texture embeddings from leaf specimen via convolutional layers...`,
        color: '#4ade80',
      },
      {
        agency: 'ICAR',
        icon: '🧪',
        title: `ICAR & MPKV Rahuri Soil N-P-K Matrix`,
        detail: `Evaluating soil macronutrient reserves vs. standard PoP crop demand baselines...`,
        color: '#fbbf24',
      },
      {
        agency: 'AEROCROP',
        icon: '🧬',
        title: `Pathogen Genome Biomarker Matching`,
        detail: `Cross-referencing 38 phytopathological classes across fungal, bacterial, and viral taxonomy databases...`,
        color: '#f472b6',
      },
      {
        agency: 'AEROCROP',
        icon: '🌾',
        title: `Multi-Modal Tensor Fusion & Yield Trajectory`,
        detail: `Fusing 576-dim visual-tabular latent vector through dense neural layers for yield forecasting (t/ha)...`,
        color: '#a78bfa',
      },
      {
        agency: 'ICAR',
        icon: '⚡',
        title: `Precision Agronomic Prescription Synthesis`,
        detail: `Computing Urea, DAP, and MOP deficit dosages and generating PMFBY insurance crop advisory...`,
        color: '#10b981',
      },
    ];
  }, [crop, district]);

  // Step cycling timer
  useEffect(() => {
    if (!isOpen) {
      setCurrentStepIdx(0);
      setProgress(10);
      setTerminalLogs([]);
      return;
    }

    // Step progression timer
    const stepInterval = setInterval(() => {
      setCurrentStepIdx((prev) => {
        const next = prev + 1;
        if (next < steps.length) {
          return next;
        }
        return prev;
      });
    }, 750);

    // Progress bar smooth advance
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 94) return 94;
        const jump = Math.floor(Math.random() * 8) + 4;
        return Math.min(94, prev + jump);
      });
    }, 400);

    // Terminal log stream generator
    const logInterval = setInterval(() => {
      const now = new Date().toISOString().split('T')[1].slice(0, 8);
      const randomLogs = [
        `[${now}] [ISRO-BHUVAN] LISS-IV band 3 & 4 reflectance calibrated: NDVI = 0.742`,
        `[${now}] [NASA-POWER] PAR insolation: 5.38 kWh/m²/day | Direct normal irradiance verified`,
        `[${now}] [CUDA-TORCH] Input tensor normalized: shape [1, 3, 224, 224] across RGB channels`,
        `[${now}] [OPEN-METEO] Telemetry synoptic station latency: 28ms`,
        `[${now}] [RESNET-18] Layer4 bottleneck forward pass completed in 14.2ms`,
        `[${now}] [TABULAR-MLP] Ingested 6-dim agro-climate feature vector`,
        `[${now}] [FUSION-CORE] Concatenated visual (512-D) + tabular (64-D) -> 128-D latent state`,
        `[${now}] [ICAR-MPKV] Calculated nutrient balance deficit for targeted physiological stage`,
      ];

      setTerminalLogs((prev) => {
        const nextLog = randomLogs[Math.floor(Math.random() * randomLogs.length)];
        const updated = [...prev, nextLog];
        return updated.slice(-4); // keep last 4 lines
      });
    }, 600);

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
      clearInterval(logInterval);
    };
  }, [isOpen, steps.length]);

  if (!isOpen) return null;

  const currentStep = steps[currentStepIdx] || steps[0];

  return (
    <div
      className="modal-overlay analyzing-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Analyzing crop specimen"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(10, 20, 16, 0.82)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        padding: '16px',
        animation: 'fadeIn 0.25s ease-out',
      }}
    >
      <div
        className="glass"
        style={{
          maxWidth: '680px',
          width: '100%',
          maxHeight: '92vh',
          overflowY: 'auto',
          borderRadius: '24px',
          padding: '28px 24px',
          background: 'rgba(255, 255, 255, 0.96)',
          border: '1px solid rgba(16, 185, 129, 0.45)',
          boxShadow: '0 25px 50px -12px rgba(16, 185, 129, 0.25), 0 0 40px rgba(16, 185, 129, 0.15)',
          color: 'var(--text-primary)',
        }}
      >
        {/* Top High-Tech Satellite Badges */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '8px',
            marginBottom: '16px',
            borderBottom: '1px solid rgba(140, 195, 165, 0.25)',
            paddingBottom: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                fontSize: '0.72rem',
                fontWeight: 700,
                letterSpacing: '0.5px',
                padding: '4px 10px',
                borderRadius: '20px',
                background: 'rgba(14, 165, 233, 0.12)',
                color: '#0284c7',
                border: '1px solid rgba(14, 165, 233, 0.3)',
              }}
            >
              <span className="pulse-dot" style={{ background: '#0284c7' }} />
              🛰️ ISRO BHUVAN SAT-LINK
            </span>

            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                fontSize: '0.72rem',
                fontWeight: 700,
                letterSpacing: '0.5px',
                padding: '4px 10px',
                borderRadius: '20px',
                background: 'rgba(59, 130, 246, 0.12)',
                color: '#2563eb',
                border: '1px solid rgba(59, 130, 246, 0.3)',
              }}
            >
              <span className="pulse-dot" style={{ background: '#2563eb' }} />
              🛰️ NASA POWER TELEMETRY
            </span>
          </div>

          <span
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              padding: '4px 10px',
              borderRadius: '20px',
              background: 'rgba(16, 185, 129, 0.12)',
              color: '#059669',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <span className="pulse-dot" style={{ background: '#059669' }} />
            ⚡ AI INFERENCE ENGINE
          </span>
        </div>

        {/* Center Scanner Viewport: Holographic Scan of Leaf Photo */}
        <div style={{ display: 'grid', gridTemplateColumns: imagePreview ? '190px 1fr' : '1fr', gap: '20px', alignItems: 'center', marginBottom: '20px' }}>
          {imagePreview ? (
            <div
              style={{
                position: 'relative',
                width: '190px',
                height: '190px',
                borderRadius: '16px',
                overflow: 'hidden',
                border: '2px solid rgba(16, 185, 129, 0.6)',
                boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)',
                background: '#0f172a',
                margin: '0 auto',
              }}
            >
              <img
                src={imagePreview}
                alt="Leaf scan target"
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  filter: 'contrast(1.1) brightness(0.95)',
                }}
              />

              {/* Holographic HUD Grid Overlay */}
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  backgroundImage: 'linear-gradient(rgba(16, 185, 129, 0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(16, 185, 129, 0.15) 1px, transparent 1px)',
                  backgroundSize: '16px 16px',
                  pointerEvents: 'none',
                }}
              />

              {/* Animated Laser Scanning Line */}
              <div
                style={{
                  position: 'absolute',
                  left: 0,
                  right: 0,
                  height: '3px',
                  background: 'linear-gradient(90deg, transparent, #34d399, #10b981, #34d399, transparent)',
                  boxShadow: '0 0 12px #10b981, 0 0 20px #34d399',
                  animation: 'laser-scan 1.6s ease-in-out infinite alternate',
                  zIndex: 2,
                }}
              />

              {/* HUD Target Corners */}
              <div style={{ position: 'absolute', top: '8px', left: '8px', width: '12px', height: '12px', borderTop: '2px solid #34d399', borderLeft: '2px solid #34d399', zIndex: 3 }} />
              <div style={{ position: 'absolute', top: '8px', right: '8px', width: '12px', height: '12px', borderTop: '2px solid #34d399', borderRight: '2px solid #34d399', zIndex: 3 }} />
              <div style={{ position: 'absolute', bottom: '8px', left: '8px', width: '12px', height: '12px', borderBottom: '2px solid #34d399', borderLeft: '2px solid #34d399', zIndex: 3 }} />
              <div style={{ position: 'absolute', bottom: '8px', right: '8px', width: '12px', height: '12px', borderBottom: '2px solid #34d399', borderRight: '2px solid #34d399', zIndex: 3 }} />

              <div
                style={{
                  position: 'absolute',
                  bottom: '6px',
                  left: 0,
                  right: 0,
                  textAlign: 'center',
                  fontSize: '0.62rem',
                  fontWeight: 700,
                  letterSpacing: '1px',
                  color: '#34d399',
                  background: 'rgba(15, 23, 42, 0.75)',
                  padding: '2px 0',
                  zIndex: 3,
                }}
              >
                CELLULAR OPTICAL SCAN
              </div>
            </div>
          ) : (
            <div
              style={{
                textAlign: 'center',
                padding: '16px',
                background: 'rgba(16, 185, 129, 0.05)',
                borderRadius: '16px',
                border: '1px dashed rgba(16, 185, 129, 0.3)',
              }}
            >
              <div style={{ fontSize: '2.5rem', animation: 'pulse 1.5s infinite' }}>🛰️</div>
              <p style={{ margin: '4px 0 0', fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-green)' }}>
                Multi-Modal Diagnostic Pipeline Engaged
              </p>
            </div>
          )}

          {/* Current Active Telemetry Stage Description */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{ fontSize: '1.5rem' }}>{currentStep.icon}</span>
              <div>
                <span
                  style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    letterSpacing: '0.5px',
                    color: currentStep.color,
                    textTransform: 'uppercase',
                  }}
                >
                  Stage {currentStepIdx + 1} of {steps.length} • {currentStep.agency}
                </span>
                <h3 style={{ margin: 0, fontSize: '1.05rem', color: 'var(--text-primary)', fontWeight: 700 }}>
                  {currentStep.title}
                </h3>
              </div>
            </div>

            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {currentStep.detail}
            </p>

            {/* Target crop & district tags */}
            <div style={{ display: 'flex', gap: '8px', marginTop: '10px', flexWrap: 'wrap' }}>
              <span className="plot-stat-chip" style={{ fontSize: '0.74rem', padding: '2px 8px' }}>
                📍 {district.toUpperCase()}
              </span>
              <span className="plot-stat-chip" style={{ fontSize: '0.74rem', padding: '2px 8px' }}>
                🌱 {crop.toUpperCase()}
              </span>
              <span className="plot-stat-chip" style={{ fontSize: '0.74rem', padding: '2px 8px', color: '#0284c7', borderColor: '#38bdf8' }}>
                🛰️ INSAT-3DR / NASA POWER
              </span>
            </div>
          </div>
        </div>

        {/* Dynamic Progress Bar */}
        <div style={{ marginBottom: '18px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px', fontSize: '0.8rem', fontWeight: 600 }}>
            <span style={{ color: 'var(--text-secondary)' }}>
              {language === 'mr' ? 'उपग्रह डेटा व मॉडेल इन्फरन्स सुरू आहे...' : language === 'hi' ? 'उपग्रह डेटा एवं AI मॉडल प्रोसेसिंग जारी...' : 'Satellite Telemetry & AI Inference in Progress...'}
            </span>
            <span style={{ color: 'var(--accent-green)', fontWeight: 700 }}>{progress}%</span>
          </div>
          <div
            style={{
              width: '100%',
              height: '8px',
              borderRadius: '999px',
              background: 'rgba(140, 195, 165, 0.25)',
              overflow: 'hidden',
              position: 'relative',
            }}
          >
            <div
              style={{
                width: `${progress}%`,
                height: '100%',
                borderRadius: '999px',
                background: 'linear-gradient(90deg, #38bdf8, #10b981, #059669)',
                boxShadow: '0 0 10px rgba(16, 185, 129, 0.6)',
                transition: 'width 0.35s ease',
              }}
            />
          </div>
        </div>

        {/* Live Sci-Fi Console Terminal Stream */}
        <div
          style={{
            background: '#09130e',
            borderRadius: '12px',
            padding: '12px 16px',
            fontFamily: 'Consolas, Monaco, "Courier New", monospace',
            fontSize: '0.74rem',
            color: '#4ade80',
            border: '1px solid rgba(74, 222, 128, 0.25)',
            boxShadow: 'inset 0 2px 8px rgba(0, 0, 0, 0.6)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(74, 222, 128, 0.2)', paddingBottom: '6px', marginBottom: '8px' }}>
            <span style={{ color: '#86efac', fontWeight: 700, letterSpacing: '0.5px' }}>
              ● LIVE SATELLITE &amp; NEURAL TELEMETRY STREAM
            </span>
            <span style={{ color: '#64748b', fontSize: '0.68rem' }}>PORT 8000 // 256-BIT SECURE</span>
          </div>

          <div style={{ minHeight: '64px', display: 'flex', flexDirection: 'column', gap: '3px' }}>
            {terminalLogs.length === 0 ? (
              <span style={{ color: '#64748b' }}>Establishing link to ISRO Bhuvan &amp; NASA EarthData...</span>
            ) : (
              terminalLogs.map((log, i) => (
                <div key={i} style={{ opacity: 0.6 + i * 0.13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {log}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes laser-scan {
          0% { top: 0%; opacity: 0.8; }
          50% { top: 96%; opacity: 1; }
          100% { top: 0%; opacity: 0.8; }
        }
        .pulse-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          display: inline-block;
          animation: pulse-dot-anim 1.2s infinite ease-in-out;
        }
        @keyframes pulse-dot-anim {
          0% { transform: scale(0.9); opacity: 0.7; }
          50% { transform: scale(1.4); opacity: 1; }
          100% { transform: scale(0.9); opacity: 0.7; }
        }
      `}</style>
    </div>
  );
};
