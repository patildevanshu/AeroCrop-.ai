/**
 * AeroCrop.ai — Mandi API Client
 */

import { apiFetch } from './client';
import { MandiRateInfo } from '../types';

export interface MandiOverviewResponse {
  district: string;
  count: number;
  market_rates: MandiRateInfo[];
}

export async function fetchMandiRate(
  district: string,
  crop: string,
  yield_t_ha?: number
): Promise<MandiRateInfo> {
  const params = new URLSearchParams();
  if (yield_t_ha !== undefined && yield_t_ha !== null) {
    params.append('yield_t_ha', yield_t_ha.toString());
  }
  const qs = params.toString() ? `?${params.toString()}` : '';
  return apiFetch<MandiRateInfo>(`/api/mandi/${encodeURIComponent(district)}/${encodeURIComponent(crop)}${qs}`);
}

export async function fetchDistrictMandiOverview(district: string): Promise<MandiOverviewResponse> {
  return apiFetch<MandiOverviewResponse>(`/api/mandi/overview/${encodeURIComponent(district)}`);
}

export async function fetchMandiCrops(): Promise<{ count: number; crops: string[] }> {
  return apiFetch<{ count: number; crops: string[] }>('/api/mandi/crops');
}
