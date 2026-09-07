import React from 'react';
import { useI18n } from '../../context/I18nContext';

export const AboutPage: React.FC = () => {
  const { t } = useI18n();

  const crops = [
    '🌱 Cotton (कापूस)',
    '🎋 Sugarcane (ऊस)',
    '🍌 Banana (केळी)',
    '🌿 Turmeric (हळद)',
    '🌽 Maize / Corn (मका)',
    '🍚 Rice / Paddy (भात)',
    '🫘 Soybean (सोयाबीन)',
    '🥔 Potato (बटाटा)',
    '🌾 Wheat (गहू)',
    '🧅 Onion (कांदा)',
  ];

  return (
    <section className="page-container" aria-labelledby="heading-about">
      <header className="page-header">
        <div>
          <h1 id="heading-about">{t('about_title')}</h1>
          <p className="page-subtitle">{t('about_subtitle')}</p>
        </div>
      </header>

      <div className="about-grid">
        {/* Architecture Card */}
        <div className="card glass about-card">
          <h2>{t('arch_title')}</h2>
          <div className="arch-diagram" aria-label="Model architecture diagram">
            <div className="arch-block visual">
              📷 RGB Leaf Image<br />
              <small>3 × 224 × 224</small>
            </div>
            <div className="arch-arrow">▼</div>
            <div className="arch-block encoder">
              ResNet-18 Visual Encoder<br />
              <small>512-dim visual representation</small>
            </div>
            <div className="arch-line" />
            <div className="arch-fusion">
              <div className="arch-block tabular">
                🧪 Soil + Weather MLP<br />
                <small>6-dim tabular → 64-dim vector</small>
              </div>
              <div className="arch-concat">
                ⊕ Concat → 576-dim<br />
                → Linear → BatchNorm → ReLU → <strong>128-dim Embedding</strong>
              </div>
            </div>
            <div className="arch-arrow">▼</div>
            <div className="arch-heads">
              <div className="arch-block head-a">
                🦠 Disease Head<br />
                <small>38 classes (CrossEntropy)</small>
              </div>
              <div className="arch-block head-b">
                🌾 Yield Head<br />
                <small>t/ha regression (MSE)</small>
              </div>
            </div>
          </div>
        </div>

        {/* References Card */}
        <div className="card glass about-card">
          <h2>{t('dataset_tech_title')}</h2>
          <ul className="about-list">
            <li>
              <strong>Dataset:</strong> PlantVillage &amp; New Plant Diseases Dataset — 87,900 images across 38 classes (Kaggle).
            </li>
            <li>
              <strong>Disease Model:</strong> Custom Multi-Modal Dual-Head Deep CNN (ResNet-18 + Tabular MLP Fusion).
            </li>
            <li>
              <strong>Yield Forecasting:</strong> Microclimate-conditioned regression network trained on soil NPK and meteorological telemetry.
            </li>
            <li>
              <strong>Live Telemetry:</strong> Open-Meteo REST API (real-time meteorological telemetry for 36 districts).
            </li>
            <li>
              <strong>Core Technologies:</strong> PyTorch · FastAPI · React 18 · TypeScript · Vite · Chart.js · SQLAlchemy Async.
            </li>
          </ul>
        </div>

        {/* Supported Crops */}
        <div className="card glass about-card">
          <h2>{t('supported_crops_title')}</h2>
          <div className="crop-badges">
            {crops.map((c, idx) => (
              <span key={idx} className="crop-badge">
                {c}
              </span>
            ))}
          </div>
        </div>

        {/* Coverage Card */}
        <div className="card glass about-card">
          <h2>{t('mh_coverage_title')}</h2>
          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            {t('mh_coverage_desc')}
          </p>
          <p className="about-note">
            {t('mh_target_zones')}
          </p>
        </div>
      </div>
    </section>
  );
};
