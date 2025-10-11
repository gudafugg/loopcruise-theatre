// src/api/http.ts

const BASE_URL = 'http://localhost:3000'; // 本地后端地址

export type HttpError = {
  status: number;
  message: string;
  body?: unknown;
};

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
};

async function request<T>(url: string, options: RequestOptions = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    method: options.method ?? 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
    signal: options.signal,
  });

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const err: HttpError = {
      status: res.status,
      message: (data && (data.message || data.error)) || res.statusText,
      body: data,
    };
    throw err;
  }
  return data as T;
}

export const http = {
  get: <T>(url: string, opts?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(url, { ...opts, method: 'GET' }),
  post: <T>(url: string, body?: unknown, opts?: Omit<RequestOptions, 'method'>) =>
    request<T>(url, { ...opts, method: 'POST', body }),
  put: <T>(url: string, body?: unknown, opts?: Omit<RequestOptions, 'method'>) =>
    request<T>(url, { ...opts, method: 'PUT', body }),
  del: <T>(url: string, opts?: Omit<RequestOptions, 'method' | 'body'>) =>
    request<T>(url, { ...opts, method: 'DELETE' }),
};