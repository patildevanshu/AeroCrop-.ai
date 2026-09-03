import { apiFetch } from './client';
import { FarmPlot } from '../types';

export interface CreatePlotPayload {
  plot_name: string;
  crop_type: string;
  area_acres: number;
  sowing_date?: string | null;
  soil_type: string;
  baseline_N?: number | null;
  baseline_P?: number | null;
  baseline_K?: number | null;
  notes?: string | null;
}

export async function fetchFarmerPlots(): Promise<{ count: number; plots: FarmPlot[] }> {
  return apiFetch<{ count: number; plots: FarmPlot[] }>('/api/farmer/plots');
}

export async function createFarmerPlot(payload: CreatePlotPayload): Promise<FarmPlot> {
  return apiFetch<FarmPlot>('/api/farmer/plots', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateFarmerPlot(plotId: number, payload: Partial<CreatePlotPayload>): Promise<FarmPlot> {
  return apiFetch<FarmPlot>(`/api/farmer/plots/${plotId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export async function deleteFarmerPlot(plotId: number): Promise<{ message: string }> {
  return apiFetch<{ message: string }>(`/api/farmer/plots/${plotId}`, {
    method: 'DELETE',
  });
}
