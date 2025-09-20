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

export async function getServerDataAction<T>(
  endpoint: string,
): Promise<GetServerDataActionReturnType<T>> {
  try {
    const cookieStore = await cookies();
    const userCookie = cookieStore.get('access_token');
    if (!userCookie?.value) return redirect('/signup');

    const res = await fetch(`${baseUrl}${endpoint}`, {
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
    const data = (await res.json()) as T;
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

    // Only add body for non-DELETE requests
    if (method !== 'DELETE' && data !== null) {
      fetchOptions.body = JSON.stringify(data);
    }

    const res = await fetch(`${baseUrl}${endpoint}`, fetchOptions);
    if (!res.ok) {
      return { isError: true, error: await processError(res), data: undefined };
    }

    // Handle DELETE requests that might not return JSON
    if (method === 'DELETE' && res.status === 204) {
      return { isError: false, error: undefined, data: { message: 'Deleted successfully' } as T };
    }

    const responseData = (await res.json()) as T;
    return { isError: false, error: undefined, data: responseData };
  } catch (error) {
    return { isError: true, error: error as Error, data: undefined };
  }
}
