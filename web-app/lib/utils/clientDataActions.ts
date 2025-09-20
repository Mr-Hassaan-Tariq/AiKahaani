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

export async function getClientDataAction<T>(endpoint: string, schema?: z.ZodSchema<T>) {
  const token = getAuthToken();
  const res = await fetch(`${baseUrl}${endpoint}`, {
    method: 'GET',
    cache: 'no-store',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    // if (res.status === 401 && typeof window !== 'undefined') window.location.href = '/signout';
    const error = await processError(res);
    logger.error(error);
    throw error;
  }
  const data = await res.json();

  if (schema) {
    const parsedData = schema.safeParse(data);
    if (parsedData.success) {
      return parsedData.data;
    }

    logger.error(parsedData.error);
    throw new Error('Sorry, we were unable to process your request. Please try again later.');
  }

  return data as T;
}

export async function postClientDataAction<T, P>(endpoint: string, body?: P, customUrl?: string) {
  const token = getAuthToken();

  // headers
  const headers = new Headers();
  if (!(body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  headers.set('Authorization', `Bearer ${token}`);

  const res = await fetch(customUrl ?? `${baseUrl}${endpoint}`, {
    method: 'POST',
    headers: headers,
    body: body instanceof FormData ? body : JSON.stringify(body),
  });

  if (!res.ok) {
    const error = await processError(res);
    logger.error(error);
    throw error;
  }

  return res.json() as T;
}

export async function patchClientDataAction<T, P>(endpoint: string, body?: P) {
  const token = getAuthToken();
  const res = await fetch(`${baseUrl}/${endpoint}`, {
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
  return res.json() as T;
}

export async function deleteClientDataAction<T>(endpoint: string) {
  const token = getAuthToken();
  const res = await fetch(`${baseUrl}${endpoint}`, {
    method: method.delete,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });
  if (!res.ok) {
    // if (res.status === 401 && typeof window !== 'undefined') window.location.href = '/signout';
    const error = await processError(res);
    logger.error(error);
    throw error;
  }
  return res.json() as T;
}

export async function putClientDataAction<T, P>(endpoint: string, body?: P) {
  const token = getAuthToken();
  const res = await fetch(`${baseUrl}${endpoint}`, {
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
  return res.json() as T;
}
