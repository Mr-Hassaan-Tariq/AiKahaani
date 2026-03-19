'use client';

import { useMutation } from '@tanstack/react-query';

import { postClientDataAction } from 'lib/utils/clientDataActions';
import { GenerateScriptType } from 'app/(dashboard)/new-script/script/[scriptId]/types';

async function generateScript(outlineId: string) {
  if (!outlineId) throw new Error('outlineId not found');

  return await postClientDataAction<GenerateScriptType, unknown>(
    `/v1/scripts/outlines/${outlineId}/script`,
  );
}

export default function useGenerateScript() {
  return useMutation({ mutationFn: generateScript });
}
