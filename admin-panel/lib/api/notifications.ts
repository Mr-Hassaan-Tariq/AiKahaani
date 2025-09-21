import { ApiClient } from './client';
import { ApiError, NotificationSettings } from './types';

export interface NotificationSettingsResponse {
  message: string;
  settings: NotificationSettings;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

export class NotificationService {
  private apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Get current user's notification settings
   * @returns Promise with notification settings
   */
  async getNotificationSettings(): Promise<NotificationSettings> {
    const token = getCookie('access_token');
    try {
      const response = await this.apiClient.get<NotificationSettings>('/v1/users/notifications', {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
      });
      if (!response.data) {
        throw new Error('No notification settings received');
      }
      return response.data;
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
   * Update user's notification settings
   * @param settings - Notification settings to update
   * @returns Promise with updated settings
   */
  async updateNotificationSettings(
    settings: NotificationSettings,
  ): Promise<NotificationSettingsResponse> {
    const token = getCookie('access_token');
    try {
      const response = await this.apiClient.patch<NotificationSettingsResponse>(
        '/v1/users/notifications',
        settings,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : '',
          },
        },
      );
      if (!response.data) {
        throw new Error('No response received from notification settings update');
      }
      return response.data;
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
