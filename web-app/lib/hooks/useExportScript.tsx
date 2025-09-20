'use client';

import { useMutation } from '@tanstack/react-query';
import Cookies from 'js-cookie';

import { baseUrl } from 'lib/api';
import { logger } from 'lib/logger';
import useToast from 'lib/utils/useToast';

export interface ExportScriptPayload {
  uuid: string;
  format: 'docx' | 'pdf' | 'txt';
}

async function exportScript({ uuid, format }: ExportScriptPayload) {
  const token = Cookies.get('access_token');

  if (!token) {
    throw new Error('Authentication token not found');
  }

  const res = await fetch(`${baseUrl}file/${uuid}/export/?format=${format}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('Authentication failed. Please log in again.');
    }
    if (res.status === 404) {
      throw new Error('Script not found or no longer available.');
    }
    if (res.status === 500) {
      throw new Error('Server error. Please try again later.');
    }
    throw new Error(`Export failed with status: ${res.status}`);
  }

  const blob = await res.blob();
  return { blob, uuid, format };
}

export default function useExportScript() {
  const toast = useToast();

  return useMutation({
    mutationFn: exportScript,
    onSuccess: ({ format }) => {
      toast.success(
        'Export Successful',
        `Your script has been exported as ${format.toUpperCase()} format.`,
      );
    },
    onError: (error: Error) => {
      logger.error('Export failed:', error);
      toast.error('Export Failed', error.message || 'Failed to export script. Please try again.');
    },
  });
}
