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

export async function updateProfile(payload: Partial<User>): Promise<User> {
  return apiFetch<User>('/api/auth/profile', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}
