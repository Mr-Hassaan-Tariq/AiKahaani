'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { PrivacySettings, PrivacySettingsResponse } from 'lib/api/types';
import { getClientDataAction, patchClientDataAction } from 'lib/utils/clientDataActions';

async function getPrivacySettings(): Promise<PrivacySettings> {
  return getClientDataAction<PrivacySettings>('v1/users/privacy');
}

async function updatePrivacySettings(settings: PrivacySettings): Promise<PrivacySettingsResponse> {
  return patchClientDataAction<PrivacySettingsResponse, PrivacySettings>('v1/users/privacy', settings);
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
