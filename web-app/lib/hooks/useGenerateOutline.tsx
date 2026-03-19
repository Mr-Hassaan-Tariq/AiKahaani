'use client';

import { FormType, OutlineResponseType } from '@/(dashboard)/new-script/types';
import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';

async function generateOutline(params: Partial<FormType> | FormData) {
  return await postClientDataAction<OutlineResponseType, unknown>(
    '/v1/scripts/outlines/generate',
    params,
  );
}

export default function useGenerateOutline() {
  return useMutation({ mutationFn: generateOutline });
}
