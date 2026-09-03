import React, { useState, useEffect } from 'react';
import { useI18n } from '../../context/I18nContext';
import { fetchDiseaseClasses } from '../../api/predict';
import { DiseaseClassItem } from '../../types';

export const DiseaseDBPage: React.FC = () => {
  const { t } = useI18n();
  const [diseases, setDiseases] = useState<DiseaseClassItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDiseaseClasses()
      .then((data) => {
        setDiseases(data.diseases || []);
      })
      .catch((err) => {
        console.warn('Failed to load disease classes:', err);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const filteredDiseases = diseases.filter((d) => {
    const q = searchQuery.toLowerCase().trim();
    if (!q) return true;
    return (
      d.name.toLowerCase().includes(q) ||
      d.crop.toLowerCase().includes(q) ||
      (d.description && d.description.toLowerCase().includes(q))
    );
  });

  const getSeverityClass = (sev: string) => {
    return `severity-${(sev || 'none').toLowerCase()}`;
  };

  return (
    <section className="page-container" aria-labelledby="heading-diseases">
      <header className="page-header">
        <div>
          <h1 id="heading-diseases">{t('disease_db_title')}</h1>
          <p className="page-subtitle">{t('disease_db_subtitle')}</p>
        </div>
      </header>

      {/* Search Input */}
      <div className="search-row">
        <input
          type="search"
          placeholder="Search disease, crop, or symptoms…"
          aria-label="Search disease database"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {/* Disease Cards Grid */}
      {isLoading ? (
        <p className="loading-text" style={{ padding: '24px 0' }}>
          Loading disease knowledge database…
        </p>
      ) : (
        <div className="disease-db-grid" aria-label="Disease database cards">
          {filteredDiseases.map((d, idx) => {
            const treatments = [
              ...(d.chemical_treatment || []).slice(0, 2),
              ...(d.organic_treatment || []).slice(0, 1),
            ];

            return (
              <div key={idx} className="disease-db-card">
                <div className="db-card-header">
                  <div>
                    <p className="db-card-name">
                      {d.is_healthy ? '✅ ' : '🦠 '}
                      {d.name}
                    </p>
                    <p className="db-card-crop">🌱 {d.crop}</p>
                  </div>
                  <span className={`severity-badge ${getSeverityClass(d.severity)}`}>
                    {d.severity}
                  </span>
                </div>

                <p className="db-card-desc">{d.description}</p>

                <div className="db-card-tags">
                  {treatments.map((tr, tIdx) => (
                    <span key={tIdx} className="db-tag">
                      {tr.length > 32 ? tr.substring(0, 30) + '…' : tr}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
};
