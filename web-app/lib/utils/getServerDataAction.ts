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
