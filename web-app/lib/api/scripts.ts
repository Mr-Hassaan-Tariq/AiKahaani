import { ApiClient } from './client';
import { ApiError, ScriptGeneration } from './types';

export class ScriptsService {
  private apiClient: ApiClient;

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient;
  }

  /**
   * Get all script generations
   * @param search - Optional search query parameter
   * @param type - Optional type filter ('script' | 'outline')
   * @returns Promise with script generations data
   */
  async getScriptGenerations(
    search?: string,
    type?: 'script' | 'outline',
  ): Promise<ScriptGeneration[]> {
    if (process.env.NEXT_PUBLIC_BYPASS_AUTH === 'true') {
      const { mockScriptGenerations } = await import('lib/mockData');
      let results = mockScriptGenerations;
      if (search) results = results.filter((s) => s.title.toLowerCase().includes(search.toLowerCase()));
      if (type) results = results.filter((s) => s.type === type);
      return results;
    }
    try {
      const token = this.getCookie('access_token');

      const params: string[] = [];
      if (search && search.trim()) {
        params.push(`search=${encodeURIComponent(search.trim())}`);
      }
      if (type) {
        params.push(`type=${encodeURIComponent(type)}`);
      }

      let url = '/v1/scripts/generations/';
      if (params.length > 0) {
        url += `?${params.join('&')}`;
      }

      const response = await this.apiClient.get<ScriptGeneration[]>(url, {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
        },
      });

      if (!response.data) {
        throw new Error('No script generations data received');
      }

      return response.data;
    } catch (error) {
      console.error('ScriptsService: API error:', error);
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to get script generations',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  // Helper function to get cookie value (same as user service)
  private getCookie(name: string): string | null {
    if (typeof window === 'undefined') {
      return null;
    }
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  /**
   * Get a specific script generation by UUID
   * @param uuid - The UUID of the script generation
   * @returns Promise with script generation data
   */
  async getScriptGeneration(uuid: string): Promise<ScriptGeneration> {
    try {
      const token = this.getCookie('access_token');
      const response = await this.apiClient.get<ScriptGeneration>(
        `/v1/scripts/generations/${uuid}/`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : '',
          },
        },
      );
      if (!response.data) {
        throw new Error('No script generation data received');
      }
      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to get script generation',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Delete a script generation
   * @param uuid - The UUID of the script generation to delete
   * @returns Promise indicating success
   */
  async deleteScriptGeneration(uuid: string): Promise<{ status: number }> {
    try {
      const token = this.getCookie('access_token');
      const response = await this.apiClient.delete<{ status: number }>(
        `v1/scripts/outlines/${uuid}/`,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : '',
          },
        },
      );
      if (!response.data) {
        throw new Error('No response received from delete request');
      }
      return response;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to delete script generation',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Update a script generation
   * @param uuid - The UUID of the script generation to update
   * @param updates - The updates to apply
   * @returns Promise with updated script generation data
   */
  async updateScriptGeneration(
    uuid: string,
    updates: Partial<ScriptGeneration>,
  ): Promise<ScriptGeneration> {
    try {
      const token = this.getCookie('access_token');
      const response = await this.apiClient.patch<ScriptGeneration>(
        `/v1/scripts/generations/${uuid}/`,
        updates,
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : '',
          },
        },
      );
      if (!response.data) {
        throw new Error('No response received from update request');
      }
      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to update script generation',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }

  /**
   * Update outline section order and data
   * @param uuid - The UUID of the outline to update
   * @param sectionOrder - Array of section indices in new order
   * @param outlineData - Updated outline data with reordered sections
   * @returns Promise with updated outline data
   */
  async updateOutlineOrder(
    uuid: string,
    sectionOrder: number[],
    outlineData: { sections: any[] },
  ): Promise<any> {
    try {
      const token = this.getCookie('access_token');
      const response = await this.apiClient.patch<any>(
        `v1/scripts/outlines/${uuid}/`,
        {
          section_order: sectionOrder,
          outline_data: outlineData,
        },
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : '',
          },
        },
      );
      if (!response.data) {
        throw new Error('No response received from update request');
      }
      return response.data;
    } catch (error) {
      const apiError = error as { data: ApiError; status: number };
      throw {
        message: apiError.data?.detail || 'Failed to update outline order',
        errors: apiError.data?.errors,
        status: apiError.status,
      };
    }
  }
}
