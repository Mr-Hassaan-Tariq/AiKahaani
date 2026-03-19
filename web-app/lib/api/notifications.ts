import { ApiClient } from './client';
import { ApiError, NotificationSettings } from './types';

export interface NotificationSettingsResponse {
  message: string;
  settings: NotificationSettings;
}

function getCookie(name: string): string | null {
  if (typeof window === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

export class NotificationService {
  private apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Get current user's notification settings — GET /api/v1/users/me/settings/notification
   */
  async getNotificationSettings(): Promise<NotificationSettings> {
    const token = getCookie('access_token');
    try {
      const response = await this.apiClient.get<{
        success: boolean;
        data: NotificationSettings;
      }>('/v1/users/me/settings/notification', {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
      });
      if (!response.data) {
        throw new Error('No notification settings received');
      }
      return response.data?.data ?? (response.data as unknown as NotificationSettings);
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to get notification settings',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Update user's notification settings — PATCH /api/v1/users/me/settings/notification
   */
  async updateNotificationSettings(
    settings: NotificationSettings,
  ): Promise<NotificationSettingsResponse> {
    const token = getCookie('access_token');
    try {
      const response = await this.apiClient.patch<{
        success: boolean;
        data: NotificationSettings;
      }>('/v1/users/me/settings/notification', settings, {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
      });
      if (!response.data) {
        throw new Error('No response received from notification settings update');
      }
      const settingsData =
        response.data?.data ?? (response.data as unknown as NotificationSettings);
      return { message: 'Notification settings updated', settings: settingsData };
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to update notification settings',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }
}
