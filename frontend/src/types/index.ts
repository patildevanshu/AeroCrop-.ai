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
  notes: string | null;
  created_at: string;
  total_diagnoses: number;
  health_score?: number;
  recent_analyses?: Array<{
    id: number;
    disease_name: string;
    is_healthy: boolean;
    severity: string;
    confidence: number;
    predicted_yield_t_ha: number;
    created_at: string | null;
  }>;
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
  chemical_cost?: string;
  organic_cost?: string;
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

export interface PredictionResult {
  crop: string;
  district: string;
  mock_mode: boolean;
  low_confidence: boolean;
  out_of_distribution?: boolean;
  ood_reason?: string;
  saved_record_id: number | null;
  image_url: string | null;
  disease: DiseaseInfo;
  yield_t_ha: number;
  yield_category?: string;
  yield_category_label?: string;
  yield_loss_pct?: number | null;
  baseline_yield_t_ha?: number | null;
  yield_reason?: string | null;
  weather: WeatherData;
  mandi?: MandiRateInfo;
  email_status?: 'queued' | 'sent' | null;
  email_recipient?: string | null;
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
  chemical_cost?: string;
  organic_cost?: string;
}

export interface AnalysisProgressItem {
  id: number;
  analysis_number: number;
  created_at: string | null;
  date_display: string;
  disease_name: string;
  severity: string;
  is_healthy: boolean;
  confidence: number;
  predicted_yield_t_ha: number;
  image_url: string | null;
  weather_temp?: number | null;
  weather_hum?: number | null;
  weather_rain?: number | null;
}

export interface CropProgressPlot {
  plot_id: number | null;
  plot_name: string;
  crop_type: string;
  area_acres: number;
  soil_type: string;
  sowing_date: string | null;
  total_analyses: number;
  health_score: number;
  trend: 'baseline' | 'improving' | 'recovered' | 'deteriorating' | 'stable' | 'no_analyses';
  status_text: string;
  latest_analysis: AnalysisProgressItem | null;
  analyses: AnalysisProgressItem[];
}

export interface CropProgressResponse {
  count: number;
  crops: CropProgressPlot[];
}

export interface FarmerAnalytics {
  total_plots: number;
  total_acres: number;
  total_diagnoses: number;
  health_rate_percent: number;
  avg_yield_t_ha: number;
  top_diseases: Array<{ name: string; count: number }>;
}

export interface DiagnosisDetail {
  id: number;
  plot_id: number | null;
  plot_name: string | null;
  crop: string;
  district: string;
  image_url: string | null;
  disease: DiseaseInfo;
  yield_t_ha: number;
  weather: WeatherData;
  low_confidence: boolean;
  mock_mode: boolean;
  created_at: string | null;
}

export interface ProfileUpdatePayload {
  full_name?: string;
  district?: string;
  taluka_village?: string;
  preferred_language?: Language;
}

export interface ChangePasswordPayload {
  current_password: string;
  new_password: string;
}

