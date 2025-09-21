'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import Cookies from 'js-cookie';

import { ApiError, baseUrl, method, NotificationSettings } from 'lib/api';
import { NotificationSettingsResponse } from 'lib/api/notifications';
import { processError } from 'lib/utils/clientDataActions';

async function updateProfileImage(formData: FormData) {
  const token = Cookies.get('access_token');

  if (!token) return (window.location.href = '/signup');

  const res = await fetch(`${baseUrl}v1/users/profile-picture`, {
    method: method.patch,
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });
  if (!res.ok) throw await processError(res);
  return res.json();
}

async function getNotificationSettings(): Promise<NotificationSettings> {
  const token = Cookies.get('access_token');
  try {
    const response = await fetch(`${baseUrl}v1/users/notifications`, {
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
      },
    });
    if (!response.ok) {
      throw new Error('No notification settings received');
    }
    return response.json();
  } catch (error) {
    const apiError = error as { data: ApiError; status: number };
    throw {
      message: apiError.data?.detail || 'Failed to get notification settings',
      errors: apiError.data?.errors,
      status: apiError.status,
    };
  }
}

async function updateNotificationSettings(
  settings: NotificationSettings,
): Promise<NotificationSettingsResponse> {
  const token = Cookies.get('access_token');
  try {
    const response = await fetch(`${baseUrl}v1/users/notifications`, {
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
      message: apiError.data?.detail || 'Failed to update notification settings',
      errors: apiError.data?.errors,
      status: apiError.status,
    };
  }
}

export function useUpdateNotificationSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateNotificationSettings,
    onSuccess: () => {
      // Invalidate and refetch notification settings after successful update
      queryClient.invalidateQueries({ queryKey: ['notificationSettings'] });
    },
  });
}

export function useGetNotificationSettings() {
  return useQuery({ queryKey: ['notificationSettings'], queryFn: getNotificationSettings });
}

export default function useUpdateProfileImage() {
  return useMutation({ mutationFn: updateProfileImage });
}
