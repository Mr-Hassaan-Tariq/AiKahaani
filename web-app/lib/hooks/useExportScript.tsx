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

async function exportScript({
  uuid,
  format,
}: ExportScriptPayload): Promise<{ file_url: string; format: string }> {
  // Bypass mode: generate a local blob download from mock content
  if (process.env.NEXT_PUBLIC_BYPASS_AUTH === 'true') {
    const { mockScript } = await import('lib/mockData');
    const text = [
      mockScript.title,
      '',
      ...mockScript.sections.map((s) => `## ${s.title}\n${s.content}`),
    ].join('\n\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const file_url = URL.createObjectURL(blob);
    return { file_url, format };
  }

  const token = Cookies.get('access_token');

  if (!token) {
    throw new Error('Authentication token not found');
  }

  const res = await fetch(`${baseUrl}v1/scripts/${uuid}/export/`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ format }),
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

  const file = await res.json();

  return { format: format, ...file };
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
