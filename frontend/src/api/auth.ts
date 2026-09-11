import { apiFetch } from './client';
import { User } from '../types';

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterPayload {
  full_name: string;
  phone_number?: string | null;
  email?: string | null;
  password: string;
  district: string;
  taluka_village?: string | null;
  preferred_language?: string;
}

export interface LoginPayload {
  identifier: string;
  password: string;
}

export async function loginFarmer(payload: LoginPayload): Promise<AuthResponse> {
  return apiFetch<AuthResponse>('/api/auth/login', {
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
