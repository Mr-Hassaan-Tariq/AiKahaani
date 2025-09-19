'use client';

import { useMutation } from '@tanstack/react-query';

import { baseUrl } from 'lib/api';

export interface ExportScriptPayload {
  script: string | number;
  format: string;
}

async function exportScript({ script, format }: ExportScriptPayload) {
  const res = await fetch(`${baseUrl}v1/scripts/${script}/export?format=${format}`, {
    method: 'GET',
  });

  if (!res.ok) {
    throw new Error('Failed to export script');
  }

  const blob = await res.blob();
  return { blob, script, format };
}

export default function useExportScript() {
  return useMutation({
    mutationFn: exportScript,
  });
}
