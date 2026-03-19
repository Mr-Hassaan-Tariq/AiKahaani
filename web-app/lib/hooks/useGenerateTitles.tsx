'use client';

import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';

interface GenerateTitlesPayload {
  prompt: string;
  tones: string[];
}

async function generateTitles(payload: GenerateTitlesPayload) {
  const response = await postClientDataAction<any, GenerateTitlesPayload>(
    '/v1/scripts/titles/generate',
    payload,
  );

  return response;
}

export default function useGenerateTitles() {
  return useMutation({ mutationFn: generateTitles });
}
