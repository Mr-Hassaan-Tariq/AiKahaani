'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import Cookies from 'js-cookie';

import { ApiError, baseUrl, method } from 'lib/api';
import { PrivacySettings, PrivacySettingsResponse } from 'lib/api/types';
import { processError } from 'lib/utils/clientDataActions';

async function updatePrivacySettings(settings: PrivacySettings): Promise<PrivacySettingsResponse> {
  const token = Cookies.get('access_token');
  try {
    const response = await fetch(`${baseUrl}v1/users/privacy`, {
      method: method.patch,
      headers: {
        'Content-Type': 'application/json',
        Authorization: token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify(settings),
    });
    if (!response.ok) throw await processError(response);
    return response.json();
  } catch (error) {
    const apiError = error as { data: ApiError; status: number };
    throw {
      message: apiError.data?.detail || 'Failed to update privacy settings',
      errors: apiError.data?.errors,
      status: apiError.status,
    };
  }
}

async function getPrivacySettings(): Promise<PrivacySettings> {
  const token = Cookies.get('access_token');
  try {
    const response = await fetch(`${baseUrl}v1/users/privacy`, {
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
      },
    });
    if (!response.ok) {
      throw new Error('No privacy settings received');
    }
    return response.json();
  } catch (error) {
    const apiError = error as { data: ApiError; status: number };
    throw {
      message: apiError.data?.detail || 'Failed to get privacy settings',
      errors: apiError.data?.errors,
      status: apiError.status,
    };
  }
}

export function useUpdatePrivacySettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: updatePrivacySettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['privacySettings'] });
    },
  });
}

export function useGetPrivacySettings() {
  return useQuery({ queryKey: ['privacySettings'], queryFn: getPrivacySettings });
}
