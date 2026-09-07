import React, { useState } from 'react';
import { useI18n } from '../../context/I18nContext';

interface KVKContact {
  district: string;
  name: string;
  phone: string;
  location: string;
}

const KVK_DIRECTORY: KVKContact[] = [
  { district: 'Pune', name: 'ICAR-KVK Baramati (ADT)', phone: '+91 2112 255227', location: 'Malegaon Khurd, Baramati' },
  { district: 'Nashik', name: 'ICAR-KVK YCMOU Nashik', phone: '+91 253 2231477', location: 'Gangapur Road, Nashik' },
  { district: 'Jalgaon', name: 'ICAR-KVK Pal (Satpuda)', phone: '+91 2588 251234', location: 'Pal, Raver, Jalgaon' },
  { district: 'Nagpur', name: 'ICAR-CICR KVK Nagpur', phone: '+91 7103 275536', location: 'Panjari Farm, Wardha Road' },
  { district: 'Ahmednagar', name: 'ICAR-KVK Babhaleshwar', phone: '+91 2422 252414', location: 'Rahata, Ahmednagar' },
  { district: 'Amravati', name: 'ICAR-KVK Durgapur (GVM)', phone: '+91 721 2552244', location: 'Badnera Road, Amravati' },
  { district: 'Kolhapur', name: 'ICAR-KVK Talsande (DYP)', phone: '+91 230 2479299', location: 'Hatkanangale, Kolhapur' },
  { district: 'Chhatrapati Sambhajinagar', name: 'ICAR-KVK VNMKV', phone: '+91 240 2376558', location: 'Paithan Road, Aurangabad' },
  { district: 'Solapur', name: 'ICAR-KVK Kavathe', phone: '+91 217 2373005', location: 'North Solapur' },
  { district: 'Latur', name: 'ICAR-KVK Manjara', phone: '+91 2382 245900', location: 'Vilaspur, Latur' },
];

export const KVKCard: React.FC = () => {
  const { t } = useI18n();
  const [searchTerm, setSearchTerm] = useState('');

  const filtered = KVK_DIRECTORY.filter(
    (k) =>
      k.district.toLowerCase().includes(searchTerm.toLowerCase()) ||
      k.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      k.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="card glass dash-card" style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
      <div className="dash-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <h2 className="card-title" style={{ margin: 0 }}>
          <span aria-hidden="true">👨‍🌾</span>
          <span>{t('kvk_help')}</span>
        </h2>
        <input
          type="search"
          placeholder={t('kvk_search_placeholder')}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            padding: '0.35rem 0.75rem',
            borderRadius: '6px',
            border: '1px solid rgba(255,255,255,0.2)',
            background: 'rgba(0,0,0,0.3)',
            color: '#fff',
            fontSize: '0.85rem',
            width: '220px',
          }}
        />
      </div>

      <p style={{ margin: '0.5rem 0 1rem 0', fontSize: '0.85rem', color: '#94a3b8' }}>
        {t('kvk_subtitle')}
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '0.75rem' }}>
        {filtered.map((kvk) => (
          <div
            key={kvk.name}
            className="metric-card glass"
            style={{ padding: '0.85rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                <span style={{ fontWeight: 700, color: '#38bdf8', fontSize: '0.92rem' }}>📍 {kvk.district}</span>
              </div>
              <p style={{ margin: '0.2rem 0', fontWeight: 600, fontSize: '0.88rem' }}>{kvk.name}</p>
              <p style={{ margin: '0.1rem 0 0.5rem 0', fontSize: '0.78rem', color: '#94a3b8' }}>{kvk.location}</p>
            </div>
            <a
              href={`tel:${kvk.phone.replace(/\s+/g, '')}`}
              className="btn btn-secondary btn-sm"
              style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem', textDecoration: 'none' }}
            >
              <span>📞</span>
              <span>{kvk.phone}</span>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
};
