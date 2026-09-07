import { apiFetch } from './client';
import { HistoryRecord, CropProgressResponse } from '../types';

const LOCAL_HISTORY_KEY = 'aerocrop_history';

export async function fetchFarmerHistory(cropType?: string): Promise<{ count: number; records: HistoryRecord[] }> {
  const url = cropType
    ? `/api/farmer/history?crop_type=${encodeURIComponent(cropType)}`
    : '/api/farmer/history';
  return apiFetch<{ count: number; records: HistoryRecord[] }>(url);
}

export async function fetchCropProgress(): Promise<CropProgressResponse> {
  return apiFetch<CropProgressResponse>('/api/farmer/crop-progress');
}

export function getLocalHistory(): HistoryRecord[] {
  try {
    return JSON.parse(localStorage.getItem(LOCAL_HISTORY_KEY) || '[]');
  } catch {
    return [];
  }
}

export function saveToLocalHistory(entry: HistoryRecord): void {
  const history = getLocalHistory();
  history.unshift(entry);
  if (history.length > 20) history.pop();
  localStorage.setItem(LOCAL_HISTORY_KEY, JSON.stringify(history));
}

export function clearLocalHistory(): void {
  localStorage.removeItem(LOCAL_HISTORY_KEY);
}
