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

// Admin User Management Types
export interface AdminUser extends User {
  is_active: boolean;
  date_joined: string;
  roles_display: string[];
  is_admin: boolean;
  is_email_verified: boolean;
}

export interface AdminUsersResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: AdminUser[];
}

export interface UpdateUserStatusRequest {
  is_active?: boolean;
  is_admin?: boolean;
}

export interface UpdateUserStatusResponse {
  user: AdminUser;
  message: string;
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
    const token = getCookie('access_token');

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

  async updateProfilePicture(file: File): Promise<{ message: string; profile_picture: string }> {
    const token = getCookie('access_token');

    const formData = new FormData();
    formData.append('profile_picture', file);

    const response = await this.apiClient.patch<{ message: string; profile_picture: string }>(
      '/v1/users/profile-picture/',
      formData,
      {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
          'Content-Type': 'multipart/form-data',
        },
      },
    );

    if (!response || !response.data) {
      throw new Error('No response received from API');
    }

    return response.data;
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

  // Admin User Management Methods

  /**
   * Get all users for admin management
   * @param page - Page number for pagination
   * @param limit - Number of users per page
   * @param search - Optional search term
   * @returns Promise with paginated users data
   */
  async getAdminUsers(
    page: number = 1,
    limit: number = 20,
    search?: string,
  ): Promise<AdminUsersResponse> {
    try {
      const offset = (page - 1) * limit;
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      });

      if (search) {
        params.append('search', search);
      }

      const response = await this.apiClient.get<AdminUsersResponse>(
        `/v1/admin/users/?${params.toString()}`,
      );

      if (!response.data) {
        throw new Error('No users data received');
      }

      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to get users',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Get a specific user by ID for admin management
   * @param userId - User ID
   * @returns Promise with user data
   */
  async getAdminUser(userId: string): Promise<AdminUser> {
    try {
      const response = await this.apiClient.get<AdminUser>(`/v1/admin/users/${userId}/`);

      if (!response.data) {
        throw new Error('No user data received');
      }

      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to get user',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Update user status (active, staff, superuser)
   * @param userId - User ID
   * @param statusData - Status data to update
   * @returns Promise with updated user data
   */
  async updateUserStatus(
    userId: string,
    statusData: UpdateUserStatusRequest,
  ): Promise<UpdateUserStatusResponse> {
    try {
      const response = await this.apiClient.patch<UpdateUserStatusResponse>(
        `/v1/admin/users/${userId}/`,
        statusData,
      );

      if (!response.data) {
        throw new Error('No data received from update request');
      }

      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to update user status',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Delete a user (admin only)
   * @param userId - User ID
   * @returns Promise indicating success
   */
  async deleteUser(userId: string): Promise<{ message: string }> {
    try {
      const response = await this.apiClient.delete<{ message: string }>(
        `/v1/admin/users/${userId}/`,
      );

      if (!response.data) {
        throw new Error('No data received from delete request');
      }

      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to delete user',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Activate a user
   * @param userId - User ID
   * @returns Promise with updated user data
   */
  async activateUser(userId: string): Promise<UpdateUserStatusResponse> {
    return this.updateUserStatus(userId, { is_active: true });
  }

  /**
   * Deactivate a user
   * @param userId - User ID
   * @returns Promise with updated user data
   */
  async deactivateUser(userId: string): Promise<UpdateUserStatusResponse> {
    return this.updateUserStatus(userId, { is_active: false });
  }

  /**
   * Grant admin privileges to a user
   * @param userId - User ID
   * @returns Promise with updated user data
   */
  async grantAdminPrivileges(userId: string): Promise<UpdateUserStatusResponse> {
    return this.updateUserStatus(userId, { is_admin: true });
  }

  /**
   * Revoke admin privileges from a user
   * @param userId - User ID
   * @returns Promise with updated user data
   */
  async revokeAdminPrivileges(userId: string): Promise<UpdateUserStatusResponse> {
    return this.updateUserStatus(userId, { is_admin: false });
  }
}
