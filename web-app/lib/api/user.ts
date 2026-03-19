/* eslint-disable @typescript-eslint/no-explicit-any */

import { ApiClient } from './client';
import { ApiError, User } from './types';

export interface UpdateUserRequest {
  fullname?: string;
  username?: string;
  preferred_language?: string;
  profile_picture_url?: string | null;
}

export interface UpdateUserResponse {
  user: User;
  message: string;
}

export interface UserDetailsResponse extends User {
  message?: string;
}

function getCookie(name: string): string | null {
  if (typeof window === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

export class UserService {
  private apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Get current user profile — GET /api/v1/users/me
   */
  async getProfile(): Promise<User> {
    try {
      const response = await this.apiClient.get<{ success: boolean; data: User }>('/v1/users/me');
      if (!response.data) {
        throw new Error('No user data received');
      }
      return response.data?.data ?? (response.data as unknown as User);
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to get user profile',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Get user details — alias for getProfile
   */
  async getUserDetails(): Promise<User> {
    return this.getProfile();
  }

  /**
   * Update user profile — PATCH /api/v1/users/me
   */
  async updateUserDetails(data: UpdateUserRequest): Promise<any> {
    const token = getCookie('access_token');

    const response = await this.apiClient.patch<{ success: boolean; data: User }>(
      '/v1/users/me',
      data,
      {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
      },
    );

    if (response.status !== 200) {
      throw new Error('Failed to update user details');
    }

    return response.data?.data ?? response.data;
  }

  /**
   * Update user profile — same as updateUserDetails
   */
  async updateProfile(userData: UpdateUserRequest): Promise<UpdateUserResponse> {
    try {
      const response = await this.apiClient.patch<{ success: boolean; data: User }>(
        '/v1/users/me',
        userData,
      );
      if (!response.data) {
        throw new Error('No data received from update request');
      }
      const user = response.data?.data ?? (response.data as unknown as User);
      return { user, message: 'Profile updated' };
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to update user profile',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Update profile picture URL — PATCH /api/v1/users/me with profile_picture_url
   * Note: Backend does not support file upload; pass a URL string directly.
   */
  async updateProfilePicture(
    profilePictureUrl: string,
  ): Promise<{ message: string; profile_picture_url: string }> {
    const token = getCookie('access_token');

    const response = await this.apiClient.patch<{ success: boolean; data: User }>(
      '/v1/users/me',
      { profile_picture_url: profilePictureUrl },
      {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
      },
    );

    if (!response || !response.data) {
      throw new Error('No response received from API');
    }

    const user = response.data?.data ?? (response.data as unknown as User);
    return {
      message: 'Profile picture updated',
      profile_picture_url: (user as any).profile_picture_url ?? profilePictureUrl,
    };
  }

  /**
   * Delete user account — not supported by current backend.
   */
  async deleteAccount(): Promise<{ message: string }> {
    throw new Error('Delete account is not supported by the current backend.');
  }

  /**
   * Change user password — not supported by current backend.
   */
  async changePassword(
    _currentPassword: string,
    _newPassword: string,
    _confirmPassword: string,
  ): Promise<{ message: string }> {
    throw new Error('Change password is not supported by the current backend.');
  }
}
