/**
 * AeroCrop.ai — API Client Layer
 */

const AUTH_TOKEN_KEY = 'aerocrop_jwt_token';

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

  const response = await fetch(endpoint, {
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
