'use client';

import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';

interface OptimizePayload {
  prompt: string;
  tones: string[];
  script?: string;
  user_title?: string;
}

async function optimizeTitles(payload: OptimizePayload) {
  const response = await postClientDataAction<any, OptimizePayload>(
    '/v1/scripts/titles/optimize',
    payload,
  );

  return response;
}

export default function useOptimizeTitles() {
  return useMutation({ mutationFn: optimizeTitles });
}
