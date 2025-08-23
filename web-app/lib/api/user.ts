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
