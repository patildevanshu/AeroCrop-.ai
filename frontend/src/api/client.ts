/**
 * AeroCrop.ai — API Client Layer
 */

const AUTH_TOKEN_KEY = 'aerocrop_jwt_token';

// If VITE_API_URL is configured (e.g. https://api.yourdomain.com), prefix endpoints.
const API_BASE_URL = String((import.meta as any).env?.VITE_API_URL || '').replace(/\/$/, '');

export function resolveAssetUrl(url?: string | null): string {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url;
  }
  const clean = url.startsWith('/') ? url : `/${url}`;
  return `${API_BASE_URL}${clean}`;
}

export function getApiUrl(endpoint: string): string {
  return resolveAssetUrl(endpoint);
}

export function getAuthToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearAuthToken(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export async function apiFetch<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    ...(options.headers || {}),
  };

  if (token && !('Authorization' in headers)) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  // If body is not FormData and Content-Type is not set, default to JSON
  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !('Content-Type' in headers)
  ) {
    (headers as Record<string, string>)['Content-Type'] = 'application/json';
  }

  const targetUrl = resolveAssetUrl(endpoint);
  const response = await fetch(targetUrl, {
    ...options,
    headers,
  });

  let data: any;
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    if (response.status === 401) {
      clearAuthToken();
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('aerocrop:unauthorized'));
      }
    }

    const errorDetail =
      (data && typeof data === 'object' && data.detail) ||
      (typeof data === 'string' && data) ||
      response.statusText ||
      'Request failed';
    throw new Error(errorDetail);
  }

  return data as T;
}
