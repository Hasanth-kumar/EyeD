const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClientError extends Error {
  code: string;
  details?: unknown;

  constructor(message: string, code = 'API_ERROR', details?: unknown) {
    super(message);
    this.name = 'ApiClientError';
    this.code = code;
    this.details = details;
  }

  getUserMessage(): string {
    return this.message;
  }
}

async function parseError(response: Response): Promise<ApiClientError> {
  try {
    const body = await response.json();
    const message = body.detail || body.message || body.error || response.statusText;
    return new ApiClientError(
      typeof message === 'string' ? message : JSON.stringify(message),
      body.code || 'API_ERROR',
      body
    );
  } catch {
    return new ApiClientError(response.statusText || 'Request failed', 'API_ERROR');
  }
}

export async function apiGet<T>(path: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) url.searchParams.set(key, String(value));
    });
  }

  const response = await fetch(url.toString());
  if (!response.ok) throw await parseError(response);
  return response.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) throw await parseError(response);
  return response.json() as Promise<T>;
}

export async function apiPostBlob(path: string, body: unknown): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) throw await parseError(response);
  return response.blob();
}
