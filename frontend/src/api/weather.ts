import { apiFetch } from './client';
import { WeatherData } from '../types';

export async function fetchDistricts(): Promise<{ count: number; districts: string[] }> {
  return apiFetch<{ count: number; districts: string[] }>('/api/weather/districts');
}

export async function fetchWeatherForDistrict(district: string): Promise<WeatherData> {
  return apiFetch<WeatherData>(`/api/weather/${encodeURIComponent(district)}`);
}
