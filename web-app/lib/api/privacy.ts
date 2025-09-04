import { ApiClient } from './client';
import { ApiError, PrivacySettings } from './types';

export interface PrivacySettingsResponse {
  message: string;
  settings: PrivacySettings;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

export class PrivacyService {
  private apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Get current user's privacy settings
   * @returns Promise with privacy settings
   */
  async getPrivacySettings(): Promise<PrivacySettings> {
    const token = getCookie('access_token');
    try {
      const response = await this.apiClient.get<PrivacySettings>('/v1/users/privacy', {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
      });
      if (!response.data) {
        throw new Error('No privacy settings received');
      }
      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to get privacy settings',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Update user's privacy settings
   * @param settings - Privacy settings to update
   * @returns Promise with updated settings
   */
  async updatePrivacySettings(settings: PrivacySettings): Promise<PrivacySettingsResponse> {
    const token = getCookie('access_token');
    try {
      const response = await this.apiClient.patch<PrivacySettingsResponse>(
        '/v1/users/privacy',
        settings,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : '',
          },
        },
      );
      if (!response.data) {
        throw new Error('No response received from privacy settings update');
      }
      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to update privacy settings',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }
}
