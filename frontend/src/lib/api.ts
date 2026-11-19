import type { TokenResponse } from '../types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
const TOKEN_KEY = 'finpilot_access_token';
const USER_KEY = 'finpilot_user_email';

let accessToken: string | null = localStorage.getItem(TOKEN_KEY);
let refreshing: Promise<boolean> | null = null;

export function getAccessToken() {
  return accessToken;
}

export function getSavedEmail() {
  return localStorage.getItem(USER_KEY) || '';
}

export function saveSession(token: string, email: string) {
  accessToken = token;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, email);
}

export function clearSession() {
  accessToken = null;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

async function refreshAccessToken(): Promise<boolean> {
  if (refreshing) return refreshing;
  refreshing = (async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });
      if (!response.ok) return false;
      const data = (await response.json()) as TokenResponse;
      if (!data.access_token) return false;
      accessToken = data.access_token;
      localStorage.setItem(TOKEN_KEY, data.access_token);
      return true;
    } catch {
      return false;
    } finally {
      refreshing = null;
    }
  })();
  return refreshing;
}

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

function makeHeaders(body: RequestInit['body'], extra?: HeadersInit) {
  const headers = new Headers(extra);
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`);
  if (body && !(body instanceof FormData) && !(body instanceof URLSearchParams)) {
    headers.set('Content-Type', 'application/json');
  }
  return headers;
}

async function parseResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json().catch(() => null)
    : await response.text().catch(() => '');

  if (!response.ok) {
    const detail = typeof data === 'object' && data !== null && 'detail' in data
      ? (data as { detail: unknown }).detail
      : data;
    const message = typeof detail === 'string'
      ? detail
      : detail
        ? JSON.stringify(detail)
        : `Request failed (${response.status})`;
    throw new ApiError(message, response.status, data);
  }
  return data as T;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  retryOnUnauthorized = true,
): Promise<T> {
  const body = options.body;
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: makeHeaders(body, options.headers),
    credentials: 'include',
  });

  if (response.status === 401 && retryOnUnauthorized && !path.startsWith('/auth/')) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return apiRequest<T>(path, options, false);
  }
  return parseResponse<T>(response);
}

export async function loginRequest(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ email, password });
  const response = await fetch(`${API_BASE}/auth/token`, {
    method: 'POST',
    body,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    credentials: 'include',
  });
  return parseResponse<TokenResponse>(response);
}

export async function registerRequest(username: string, email: string, password: string) {
  return apiRequest<{ message?: string; email?: string }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  }, false);
}

export function apiBaseUrl() {
  return API_BASE;
}
