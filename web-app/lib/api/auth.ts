import { ApiError } from 'next/dist/server/api-utils';

import { ApiClient } from './client';
import {
  GoogleAuthRequest,
  GoogleAuthResponse,
  SignupRequest,
  SignupResponse,
  User,
  VerifiedUser,
} from './types';

export class AuthService {
  private apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Register a new user
   * @param userData - User registration data
   * @returns Promise with signup response
   */
  async signup(userData: SignupRequest): Promise<SignupResponse> {
    try {
      const response = await this.apiClient.post<SignupResponse>('/api/auth/signup/', userData);
      if (!response.data) {
        throw new Error('No data received from signup request');
      }
      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        status: apiError.status,
      };
    }
  }

  /**
   * Send a magic link to the provided email
   * @param email - User email
   * @returns Promise with API response
   */
  async sendMagicLink(email: string): Promise<{ message: string }> {
    try {
      const response = await this.apiClient.post<{ message: string }>('/auth/magic-link/', {
        email,
      });

      if (!response.data) {
        throw new Error('No data received from magic link request');
      }

      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        status: apiError.status,
      };
    }
  }

  /**
   * Verify magic link token
   * @param token - Magic link token
   */
  async verifyMagicLink(
    token: string,
  ): Promise<{ success: boolean; message?: string; user: VerifiedUser | null; access?: string }> {
    try {
      const response = await this.apiClient.post<{
        success: boolean;
        message?: string;
        user: VerifiedUser | null;
      }>('/auth/magic-link/verify/', { token });

      // Ensure we always return user
      return (
        response.data ?? {
          success: false,
          message: 'Verification failed',
          user: null,
        }
      );
    } catch {
      return { success: false, message: 'Verification failed', user: null };
    }
  }

  /**
   * Authenticate user with Google
   * @param idToken - Google ID token or authorization code
   * @returns Promise with authentication response including tokens and user data
   */
  async googleAuth(idToken: string): Promise<GoogleAuthResponse> {
    try {
      const requestData: GoogleAuthRequest = { id_token: idToken };
      const response = await this.apiClient.post<GoogleAuthResponse>(
        '/api/auth/google/',
        requestData,
      );

      if (!response.data) {
        throw new Error('No data received from Google authentication request');
      }

      // Store tokens in localStorage
      this.apiClient.setTokens(response.data.access, response.data.refresh);

      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        status: apiError.status,
      };
    }
  }

  /**
   * Logout user by clearing tokens
   */
  logout(): void {
    this.apiClient.clearTokens();
  }

  /**
   * Check if user is authenticated
   * @returns boolean indicating authentication status
   */
  isAuthenticated(): boolean {
    return this.apiClient.isAuthenticated();
  }

  /**
   * Get current user data from localStorage (if available)
   * @returns User data or null if not available
   */
  getCurrentUser(): User | null {
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user_data');
      if (userData) {
        try {
          return JSON.parse(userData);
        } catch {
          return null;
        }
      }
    }
    return null;
  }

  /**
   * Store user data in localStorage
   * @param user - User data to store
   */
  setCurrentUser(user: User): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user_data', JSON.stringify(user));
    }
  }

  /**
   * Clear user data from localStorage
   */
  clearCurrentUser(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user_data');
    }
  }
}
