'use client';

import { useCallback, useEffect } from 'react';
import Cookies from 'js-cookie';

import { baseUrl } from '../api';
import { SetAuthTokens } from 'app/(auth)/signup/actions';

function isTokenExpiredOrMissing(): boolean {
  const token = Cookies.get('access_token');
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    // Refresh if token expires within 60 seconds
    return payload.exp * 1000 < Date.now() + 60_000;
  } catch {
    return true;
  }
}

/**
 * Hook that automatically refreshes the access token when it is expired or close to expiry.
 */
export const useAutoRefresh = () => {
  const refreshToken = useCallback(async () => {
    if (typeof window === 'undefined') return;

    // Only refresh if the current token is expired / about to expire
    if (!isTokenExpiredOrMissing()) return;

    const storedRefresh = Cookies.get('refresh_token') ?? localStorage.getItem('refresh_token');
    if (!storedRefresh) return;

    try {
      const base = baseUrl.replace(/\/$/, '');
      const res = await fetch(`${base}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: storedRefresh }),
      });

      if (!res.ok) {
        // Refresh token is invalid — clear everything and send to login
        Cookies.remove('access_token');
        Cookies.remove('refresh_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/signup';
        return;
      }

      const json = await res.json();
      const data = json.data ?? json;
      const newAccess: string = data.access_token ?? data.access;
      const newRefresh: string = data.refresh_token ?? data.refresh ?? storedRefresh;

      if (!newAccess) return;

      // Persist in both js-cookie and server-accessible cookies via server action
      Cookies.set('access_token', newAccess, { expires: 1, path: '/', sameSite: 'lax' });
      Cookies.set('refresh_token', newRefresh, { expires: 30, path: '/', sameSite: 'lax' });
      localStorage.setItem('refresh_token', newRefresh);
      await SetAuthTokens(newAccess, newRefresh);
    } catch {
      // Network error — don't log out, just skip
    }
  }, []);

  useEffect(() => {
    refreshToken();
  }, [refreshToken]);

  return { refreshToken };
};

/**
 * Provider component that handles automatic token refresh on app initialization
 */
export const AutoRefreshProvider = ({ children }: { children: React.ReactNode }) => {
  useAutoRefresh();
  return children;
};
