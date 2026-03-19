'server-only';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

import { baseUrl } from 'lib/api/index';

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
  try {
    if (process.env.NEXT_PUBLIC_BYPASS_AUTH === 'true') {
      const { getMockDataForEndpoint } = await import('lib/mockData');
      return { isError: false, error: undefined, data: getMockDataForEndpoint(endpoint) as T };
    }

    const cookieStore = await cookies();
    const userCookie = cookieStore.get('access_token');
    if (!userCookie?.value) {
      return redirect('/signup');
    }

    const base = baseUrl.replace(/\/$/, '');
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const res = await fetch(`${base}${path}`, {
      method: 'GET',
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${userCookie.value}`,
      },
    });
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
    const res = await fetch(`${base}${path}`, fetchOptions);
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
