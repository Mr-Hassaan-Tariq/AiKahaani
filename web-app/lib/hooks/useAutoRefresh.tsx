'use client';

import { useCallback, useEffect } from 'react';

import { api, authService } from '../api';

/**
 * Hook that automatically refreshes the access token when the browser loads
 * if a refresh token is available in localStorage
 */
export const useAutoRefresh = () => {
  const refreshToken = useCallback(async () => {
    try {
      // Check if we have a refresh token
      const refreshTokenValue = api.getClient().getRefreshToken();
      if (!refreshTokenValue) {
        return; // No refresh token available, skip refresh
      }

      // Check if we already have a valid access token
      const isAuthenticated = authService.isAuthenticated();
      if (isAuthenticated) {
        return; // Already authenticated, skip refresh
      }

      // Attempt to refresh the token
      const result = await authService.refreshToken();

      // Update the access token cookie for server-side requests
      if (typeof window !== 'undefined') {
        const expires = new Date();
        expires.setDate(expires.getDate() + 7); // 7 days expiry
        document.cookie = `access_token=${result.access}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
      }

      console.log('Token refreshed successfully:', result.message);
    } catch (error) {
      console.warn('Failed to refresh token:', error);
      // Clear tokens if refresh fails
      authService.logout();
    }
  }, []);

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') {
      return;
    }

    // Run refresh on component mount (browser load)
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
