'use client';

import Cookies from 'js-cookie';
import { z } from 'zod';

import { baseUrl, method } from 'lib/api';
import { logger } from 'lib/logger';

export async function processError(resp: Response) {
  const contentType = resp.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return resp.json();
  }
  return new Error('Failed to fetch data');
}

function getAuthToken() {
  return Cookies.get('access_token');
}

function buildUrl(endpoint: string, customUrl?: string): string {
  if (customUrl) return customUrl;
  const base = baseUrl.replace(/\/$/, ''); // strip any trailing slash
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${base}${path}`;
}

/**
 * Auto-unwrap the standard { success, message, data } envelope.
 * Paginated responses (has "meta" key) and raw endpoints are returned as-is.
 */
function unwrapApiEnvelope<T>(json: unknown): T {
  if (
    json !== null &&
    typeof json === 'object' &&
    'success' in json &&
    (json as Record<string, unknown>).success === true &&
    'data' in json &&
    !('meta' in json)
  ) {
    return (json as Record<string, unknown>).data as T;
  }
  return json as T;
}

export async function getClientDataAction<T>(endpoint: string, schema?: z.ZodSchema<T>) {
  if (process.env.NEXT_PUBLIC_BYPASS_AUTH === 'true') {
    const { getMockDataForEndpoint } = await import('lib/mockData');
    return getMockDataForEndpoint(endpoint) as T;
  }
  const token = getAuthToken();
  const res = await fetch(buildUrl(endpoint), {
    method: 'GET',
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    const error = await processError(res);
    logger.error(error);
    throw error;
  }
  const json = await res.json();
  const data = unwrapApiEnvelope<T>(json);

  if (schema) {
    const parsedData = schema.safeParse(data);
    if (parsedData.success) {
      return parsedData.data;
    }
    logger.error(parsedData.error);
    throw new Error('Sorry, we were unable to process your request. Please try again later.');
  }

  return data;
}

export async function postClientDataAction<T, P>(endpoint: string, body?: P, customUrl?: string) {
  if (process.env.NEXT_PUBLIC_BYPASS_AUTH === 'true') {
    const { getMockPostDataForEndpoint } = await import('lib/mockData');
    return getMockPostDataForEndpoint(endpoint) as T;
  }
  const token = getAuthToken();

  const headers = new Headers();
  if (!(body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  headers.set('Authorization', `Bearer ${token}`);

  const res = await fetch(buildUrl(endpoint, customUrl), {
    method: 'POST',
    headers: headers,
    body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
  });

  if (!res.ok) {
    const error = await processError(res);
    logger.error(error);
    throw error;
  }

  const json = await res.json();
  return unwrapApiEnvelope<T>(json);
}

export async function patchClientDataAction<T, P>(endpoint: string, body?: P) {
  const token = getAuthToken();
  const res = await fetch(buildUrl(endpoint), {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    if (res.status === 401 && typeof window !== 'undefined') window.location.href = '/signout';
    const error = await processError(res);
    logger.error(error);
    throw error;
  }
  const json = await res.json();
  return unwrapApiEnvelope<T>(json);
}

export async function deleteClientDataAction<T>(endpoint: string) {
  const token = getAuthToken();
  const res = await fetch(buildUrl(endpoint), {
    method: method.delete,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const error = await processError(res);
    logger.error(error);
    throw error;
  }

  if (res.status === 204 || res.status === 200) {
    return { status: res.status } as T;
  }

  return res.json() as T;
}

export async function putClientDataAction<T, P>(endpoint: string, body?: P) {
  const token = getAuthToken();
  const res = await fetch(buildUrl(endpoint), {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    if (res.status === 401 && typeof window !== 'undefined') window.location.href = '/signout';
    const error = await processError(res);
    logger.error(error);
    throw error;
  }
  const json = await res.json();
  return unwrapApiEnvelope<T>(json);
}
