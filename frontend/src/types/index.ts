/**
 * AeroCrop.ai — TypeScript Definitions
 */

export type Language = 'en' | 'mr' | 'hi';

export interface User {
  id: number;
  full_name: string;
  phone_number: string | null;
  email: string | null;
  district: string;
  taluka_village: string | null;
  preferred_language: Language;
  created_at: string;
}

export interface LatestPlotDiagnosis {
  disease_name: string;
  is_healthy: boolean;
  confidence: number;
  diagnosed_at: string;
  severity: string;
}

export interface FarmPlot {
  id: number;
  user_id: number;
  plot_name: string;
  crop_type: string;
  area_acres: number;
  sowing_date: string | null;
  soil_type: string;
  baseline_N: number;
  baseline_P: number;
  baseline_K: number;
  notes: string | null;
  created_at: string;
  total_diagnoses: number;
  latest_diagnosis: LatestPlotDiagnosis | null;
}

export interface DiseaseInfo {
  name: string;
  crop: string;
  confidence: number;
  severity: string;
  is_healthy: boolean;
  description: string;
  chemical_treatment: string[];
  organic_treatment: string[];
}

export interface NPKValues {
  N: number;
  P: number;
  K: number;
}

export interface FertilizerQuantities {
  Urea: number;
  DAP: number;
  MOP: number;
}

export interface SprayWindowInfo {
  safe: boolean;
  status: 'success' | 'warning' | 'danger';
  badge: string;
  reason: string;
  reason_mr: string;
  reason_hi: string;
}

export interface WeatherData {
  district: string;
  temperature: number;
  humidity: number;
  rainfall: number;
  wind_speed?: number;
  spray_window?: SprayWindowInfo;
  source: 'live' | 'cache' | 'mock' | 'api';
}

export interface CommercialBagItem {
  kg: number;
  bags_50kg: number;
  bag_price_inr: number;
  cost_inr: number;
}

export interface RevenueProjection {
  yield_t_ha: number;
  yield_quintals_per_ha: number;
  yield_quintals_per_acre: number;
  gross_revenue_ha_inr: number;
  gross_revenue_acre_inr: number;
}

export interface MandiRateInfo {
  crop: string;
  district: string;
  apmc_market: string;
  commodity_name: string;
  name_mr: string;
  name_hi: string;
  modal_price_inr: number;
  min_price_inr: number;
  max_price_inr: number;
  msp_inr: number;
  unit: string;
  arrivals_quintal: number;
  trend: 'bullish' | 'bearish' | 'steady';
  trend_change_pct: number;
  revenue_projection?: RevenueProjection | null;
}

export interface FertilizerAdvice {
  mode?: 'standard_pop' | 'soil_test';
  soil?: NPKValues | null;
  target: NPKValues;
  deficit: NPKValues;
  fertilizers: FertilizerQuantities;
  interpretation: string;
  surplus_n_warning: string | null;
  commercial_bags?: Record<string, CommercialBagItem>;
  total_cost_inr_ha?: number;
}

export interface PredictionResult {
  crop: string;
  district: string;
  mock_mode: boolean;
  low_confidence: boolean;
  saved_record_id: number | null;
  image_url: string | null;
  disease: DiseaseInfo;
  yield_t_ha: number;
  fertilizer: FertilizerAdvice;
  weather: WeatherData;
  mandi?: MandiRateInfo;
}

export interface HistoryRecord {
  id?: number;
  created_at: string;
  crop_type: string;
  district: string;
  plot_name?: string | null;
  disease_name: string;
  confidence: number;
  predicted_yield_t_ha: number;
  severity: string;
  is_healthy: boolean;
  image_url?: string | null;
}

export interface DiseaseClassItem {
  name: string;
  crop: string;
  severity: string;
  is_healthy: boolean;
  description: string;
  chemical_treatment: string[];
  organic_treatment: string[];
}
