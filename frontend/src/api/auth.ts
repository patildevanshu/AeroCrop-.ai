import { apiFetch } from './client';
import { User } from '../types';

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterPayload {
  full_name: string;
  email: string;
  phone_number?: string | null;
  password: string;
  district: string;
  taluka_village?: string | null;
  preferred_language?: string;
}

export interface RegisterWithOtpPayload {
  full_name: string;
  email: string;
  otp: string;
  password: string;
  district: string;
  phone_number?: string | null;
  taluka_village?: string | null;
  preferred_language?: string;
}

export interface LoginPayload {
  identifier: string;
  password: string;
}

export interface LoginWithOtpPayload {
  email: string;
  otp: string;
}

export interface SendOtpPayload {
  email: string;
  purpose?: 'register' | 'login' | 'reset_password';
}

export interface SendOtpResponse {
  status: string;
  message: string;
  cooldown_seconds: number;
}

export interface VerifyOtpPayload {
  email: string;
  otp: string;
  purpose?: 'register' | 'login' | 'reset_password';
}

export async function loginFarmer(payload: LoginPayload): Promise<AuthResponse> {
  return apiFetch<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function loginFarmerWithOtp(payload: LoginWithOtpPayload): Promise<AuthResponse> {
  return apiFetch<AuthResponse>('/api/auth/login-with-otp', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function registerFarmer(payload: RegisterPayload): Promise<AuthResponse> {
  return apiFetch<AuthResponse>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function registerFarmerWithOtp(payload: RegisterWithOtpPayload): Promise<AuthResponse> {
  return apiFetch<AuthResponse>('/api/auth/register-with-otp', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function sendEmailOtp(payload: SendOtpPayload): Promise<SendOtpResponse> {
  return apiFetch<SendOtpResponse>('/api/auth/send-otp', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function verifyEmailOtp(payload: VerifyOtpPayload): Promise<{ status: string; message: string; verified: boolean }> {
  return apiFetch<{ status: string; message: string; verified: boolean }>('/api/auth/verify-otp', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getCurrentUser(): Promise<User> {
  return apiFetch<User>('/api/auth/me');
}

export async function updateProfile(payload: Partial<User>): Promise<{ status: string; message: string; user: User }> {
  return apiFetch<{ status: string; message: string; user: User }>('/api/auth/profile', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export interface ChangePasswordResponse {
  status: string;
  message: string;
  access_token: string;
  token_type: string;
}

export async function changeFarmerPassword(payload: { current_password: string; new_password: string }): Promise<ChangePasswordResponse> {
  return apiFetch<ChangePasswordResponse>('/api/auth/change-password', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}
