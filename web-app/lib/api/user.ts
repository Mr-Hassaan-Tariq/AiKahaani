/* eslint-disable @typescript-eslint/no-explicit-any */

import { ApiClient } from './client';
import { ApiError, User } from './types';

export interface UpdateUserRequest {
  fullname?: string;
  username?: string;
  email?: string;
}

export interface UpdateUserResponse {
  user: User;
  message: string;
}

export interface UserDetailsResponse extends User {
  message?: string;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

export class UserService {
  private apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Get current user profile
   * @returns Promise with user data
   */
  async getProfile(): Promise<User> {
    try {
      const response = await this.apiClient.get<User>('/api/users/profile/');
      if (!response.data) {
        throw new Error('No user data received');
      }
      return response.data;
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
   * Get user details
   * @returns Promise with user details
   */
  async getUserDetails(): Promise<User> {
    const token = getCookie('access_token'); // get token from cookies

    const response = await this.apiClient.get<UserDetailsResponse>('/v1/users/details/', {
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
      },
    });

    if (response.status !== 200) {
      throw new Error('No user details received from API');
    }

    return response.data as User;
  }

  /**
   * Update user profile
   * @param userData - User data to update
   * @returns Promise with updated user data
   */
  async updateUserDetails(data: {
    fullname?: string;
    username?: string;
    email?: string;
    preferred_language?: string;
  }): Promise<any> {
    const token = getCookie('access_token'); // get token from cookies

    const response = await this.apiClient.put('/v1/users/details/', data, {
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
      },
    });

    if (response.status !== 200) {
      throw new Error('Failed to update user details');
    }

    return response.data;
  }

  /**
   * Update user profile
   * @param userData - User data to update
   * @returns Promise with updated user data
   */
  async updateProfile(userData: UpdateUserRequest): Promise<UpdateUserResponse> {
    try {
      const response = await this.apiClient.patch<UpdateUserResponse>(
        '/api/users/profile/',
        userData,
      );
      if (!response.data) {
        throw new Error('No data received from update request');
      }
      return response.data;
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
   * Delete user account
   * @returns Promise indicating success
   */
  async deleteAccount(): Promise<{ message: string }> {
    try {
      const response = await this.apiClient.delete<{ message: string }>('/api/users/profile/');
      if (!response.data) {
        throw new Error('No data received from delete request');
      }
      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to delete user account',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Change user password
   * @param currentPassword - Current password
   * @param newPassword - New password
   * @param confirmPassword - Password confirmation
   * @returns Promise indicating success
   */
  async changePassword(
    currentPassword: string,
    newPassword: string,
    confirmPassword: string,
  ): Promise<{ message: string }> {
    try {
      const passwordData = {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      };

      const response = await this.apiClient.post<{ message: string }>(
        '/api/users/change-password/',
        passwordData,
      );
      if (!response.data) {
        throw new Error('No data received from password change request');
      }
      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to change password',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }
}
