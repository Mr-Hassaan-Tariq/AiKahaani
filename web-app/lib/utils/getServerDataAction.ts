'server-only';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { baseUrl as publicBaseUrl } from 'lib/api/index';

// Inside Docker, server actions must use the internal service name instead of localhost
const baseUrl = process.env.INTERNAL_API_URL ?? publicBaseUrl;

/**
 * Try to refresh the access token using the refresh_token cookie.
 * Updates the access_token cookie on success.
 * Returns the new access token string, or null on failure.
 */
async function tryRefreshToken(): Promise<string | null> {
  try {
    const cookieStore = await cookies();
    const refreshToken = cookieStore.get('refresh_token')?.value;
    if (!refreshToken) return null;

    const base = baseUrl.replace(/\/$/, '');
    const res = await fetch(`${base}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: 'no-store',
    });

    if (!res.ok) return null;

    const json = await res.json();
    const data = json.data ?? json;
    const newAccess: string = data.access_token ?? data.access;
    const newRefresh: string = data.refresh_token ?? data.refresh ?? refreshToken;

    if (!newAccess) return null;

    const DAY = 60 * 60 * 24;
    cookieStore.set('access_token', newAccess, { path: '/', maxAge: DAY, sameSite: 'lax' });
    cookieStore.set('refresh_token', newRefresh, { path: '/', maxAge: DAY * 30, sameSite: 'lax' });

    return newAccess;
  } catch {
    return null;
  }
}

async function processError(resp: Response) {
  const contentType = resp.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return resp.json() as ErrorResponse;
  }
  return new Error('Failed to fetch data');
}

/**
 * Standard paginated response envelope from the backend.
 * Use this as the generic type T when calling a paginated endpoint.
 */
export interface PaginatedApiResponse<T> {
  success: boolean;
  message: string;
  data: T[];
  meta: {
    total: number;
    limit: number;
    offset: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

/**
 * Auto-unwrap the standard { success, message, data } envelope.
 * Paginated responses (has "meta" key) are returned as-is so callers
 * can access both .data[] and .meta.total.
 * Raw endpoints (no "success" key, e.g. /scripts/config) are also returned as-is.
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

export async function getServerDataAction<T>(
  endpoint: string,
): Promise<GetServerDataActionReturnType<T>> {
  if (process.env.NEXT_PUBLIC_BYPASS_AUTH === 'true') {
    const { getMockDataForEndpoint } = await import('lib/mockData');
    return { isError: false, error: undefined, data: getMockDataForEndpoint(endpoint) as T };
  }

  const cookieStore = await cookies();
  const userCookie = cookieStore.get('access_token');

  // No cookie at all → redirect immediately (outside try/catch so it propagates)
  if (!userCookie?.value) {
    return redirect('/signup');
  }

  try {
    const base = baseUrl.replace(/\/$/, '');
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${base}${path}`;

    let token = userCookie.value;
    let res = await fetch(url, {
      method: 'GET',
      cache: 'no-store',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    });

    // Auto-refresh on 401 (expired access token)
    if (res.status === 401) {
      const newToken = await tryRefreshToken();
      if (!newToken) {
        // Refresh failed — redirect outside the catch so it isn't swallowed
        return { isError: true, error: new Error('Session expired'), data: undefined };
      }
      token = newToken;
      res = await fetch(url, {
        method: 'GET',
        cache: 'no-store',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      });
    }

    if (!res.ok) {
      return { isError: true, error: await processError(res), data: undefined };
    }
    const json = await res.json();
    const data = unwrapApiEnvelope<T>(json);
    return { isError: false, error: undefined, data };
  } catch (error) {
    return { isError: true, error: error as Error, data: undefined };
  }
}

export type GetServerDataActionReturnType<T> =
  | {
      isError: true;
      error: ErrorResponse | Error;
      data: undefined;
    }
  | {
      isError: false;
      error: undefined;
      data: T;
    };

export type ErrorResponse = {
  message?: string[];
  error?: string;
  statusCode?: number;
  digest?: string;
};

export async function updateServerDataAction<T>(
  endpoint: string,
  data: unknown,
  method: 'PATCH' | 'PUT' | 'DELETE' = 'PATCH',
): Promise<GetServerDataActionReturnType<T>> {
  try {
    const cookieStore = await cookies();
    const userCookie = cookieStore.get('access_token');

    const fetchOptions: RequestInit = {
      method,
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${userCookie?.value}`,
      },
    };

    if (method !== 'DELETE' && data !== null) {
      fetchOptions.body = JSON.stringify(data);
    }

    const base = baseUrl.replace(/\/$/, '');
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${base}${path}`;
    let res = await fetch(url, fetchOptions);

    // Auto-refresh on 401
    if (res.status === 401) {
      const newToken = await tryRefreshToken();
      if (newToken) {
        fetchOptions.headers = {
          ...(fetchOptions.headers as Record<string, string>),
          Authorization: `Bearer ${newToken}`,
        };
        res = await fetch(url, fetchOptions);
      }
    }

    if (!res.ok) {
      return { isError: true, error: await processError(res), data: undefined };
    }

    if (method === 'DELETE' && res.status === 204) {
      return { isError: false, error: undefined, data: { message: 'Deleted successfully' } as T };
    }

    const json = await res.json();
    const responseData = unwrapApiEnvelope<T>(json);
    return { isError: false, error: undefined, data: responseData };
  } catch (error) {
    return { isError: true, error: error as Error, data: undefined };
  }
}
