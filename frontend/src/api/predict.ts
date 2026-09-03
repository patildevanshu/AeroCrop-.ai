import { apiFetch } from './client';
import { DiseaseClassItem, PredictionResult } from '../types';

export interface PredictParams {
  image: File;
  crop: string;
  district: string;
  N: number;
  P: number;
  K: number;
  plot_id?: number | string | null;
}

export async function submitCropPrediction(params: PredictParams): Promise<PredictionResult> {
  const formData = new FormData();
  formData.append('image', params.image);
  formData.append('crop', params.crop);
  formData.append('district', params.district);
  formData.append('N', params.N.toString());
  formData.append('P', params.P.toString());
  formData.append('K', params.K.toString());
  if (params.plot_id) {
    formData.append('plot_id', params.plot_id.toString());
  }

  return apiFetch<PredictionResult>('/api/predict', {
    method: 'POST',
    body: formData,
  });
}

export async function fetchDiseaseClasses(): Promise<{ count: number; diseases: DiseaseClassItem[] }> {
  return apiFetch<{ count: number; diseases: DiseaseClassItem[] }>('/api/disease/classes');
}
