import { apiFetch } from './client';
import { DiseaseClassItem, PredictionResult } from '../types';

export interface PredictParams {
  image: File;
  crop: string;
  district: string;
  N?: number | null;
  P?: number | null;
  K?: number | null;
  plot_id?: number | string | null;
  email?: string | null;
}

export async function submitCropPrediction(params: PredictParams): Promise<PredictionResult> {
  const formData = new FormData();
  formData.append('image', params.image);
  formData.append('crop', params.crop);
  formData.append('district', params.district);
  if (params.N !== undefined && params.N !== null) {
    formData.append('N', params.N.toString());
  }
  if (params.P !== undefined && params.P !== null) {
    formData.append('P', params.P.toString());
  }
  if (params.K !== undefined && params.K !== null) {
    formData.append('K', params.K.toString());
  }
  if (params.plot_id) {
    formData.append('plot_id', params.plot_id.toString());
  }
  if (params.email && params.email.trim()) {
    formData.append('email', params.email.trim());
  }

  return apiFetch<PredictionResult>('/api/predict', {
    method: 'POST',
    body: formData,
  });
}

export async function fetchDiseaseClasses(): Promise<{ count: number; diseases: DiseaseClassItem[] }> {
  return apiFetch<{ count: number; diseases: DiseaseClassItem[] }>('/api/disease/classes');
}

export interface EmailReportPayload {
  email: string;
  name?: string;
  crop: string;
  district: string;
  disease: any;
  fertilizer: any;
  yield_t_ha?: number | null;
  weather?: any;
}

export async function sendEmailReport(payload: EmailReportPayload): Promise<{ status: string; message: string }> {
  return apiFetch<{ status: string; message: string }>('/api/predict/email-report', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
