// services/subscription.ts
import { ApiClient } from './client';
import { ApiError } from './types';

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

interface BillingPortalResponse {
  url: string;
}

export class SubscriptionService {
  private apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Create a billing portal session and return the redirect URL
   */
  async createBillingPortal(): Promise<string> {
    const token = getCookie('access_token');

    try {
      const response = await this.apiClient.post<BillingPortalResponse>(
        '/v1/payments/billing-portal/',
        {},
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : '',
          },
        },
      );

      if (!response.data?.url) {
        throw new Error('No billing portal URL received');
      }

      return response.data.url;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to create billing portal session',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }
}
