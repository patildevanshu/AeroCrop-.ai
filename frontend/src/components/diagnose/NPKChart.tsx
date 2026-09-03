import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { FertilizerAdvice } from '../../types';
import { useI18n } from '../../context/I18nContext';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface NPKChartProps {
  fertilizer: FertilizerAdvice;
}

export const NPKChart: React.FC<NPKChartProps> = ({ fertilizer }) => {
  const { t } = useI18n();
  const { soil, target, deficit } = fertilizer;

  const data = {
    labels: [t('nitrogen'), t('phosphorus'), t('potassium')],
    datasets: [
      {
        label: 'Current Soil Level',
        data: [soil.N, soil.P, soil.K],
        backgroundColor: 'rgba(6, 182, 212, 0.6)',
        borderColor: 'rgba(6, 182, 212, 1)',
        borderWidth: 1,
        borderRadius: 6,
      },
      {
        label: 'Target Level (ICAR)',
        data: [target.N, target.P, target.K],
        backgroundColor: 'rgba(34, 197, 94, 0.4)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 1,
        borderRadius: 6,
      },
      {
        label: 'Deficit',
        data: [deficit.N, deficit.P, deficit.K],
        backgroundColor: 'rgba(239, 68, 68, 0.45)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 1,
        borderRadius: 6,
      },
    ],
  };

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 800,
      easing: 'easeInOutQuart',
    },
    plugins: {
      legend: {
        labels: {
          color: '#94a3b8',
          font: { family: 'Inter', size: 12 },
        },
      },
      tooltip: {
        callbacks: {
          label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw} kg/ha`,
        },
        backgroundColor: 'rgba(13,26,32,0.92)',
        titleColor: '#e8f4f8',
        bodyColor: '#94a3b8',
        borderColor: 'rgba(6,182,212,0.3)',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: { color: '#94a3b8', font: { family: 'Inter' } },
        grid: { color: 'rgba(255,255,255,0.04)' },
      },
      y: {
        ticks: {
          color: '#94a3b8',
          font: { family: 'Inter' },
          callback: (v) => `${v} kg/ha`,
        },
        grid: { color: 'rgba(255,255,255,0.04)' },
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="card glass chart-card">
      <h2 className="card-title">
        <span aria-hidden="true">📈</span>
        <span>{t('npk_chart_title')}</span>
      </h2>
      <div className="chart-wrapper" role="img" aria-label="NPK comparison chart">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};
