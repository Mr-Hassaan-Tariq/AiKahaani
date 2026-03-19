'use client';

import { OutlineType } from '@/(dashboard)/new-script/types';
import { useMutation } from '@tanstack/react-query';

import { patchClientDataAction } from 'lib/utils/clientDataActions';

async function updateOutline(params: Partial<OutlineType>) {
  return await patchClientDataAction<Partial<OutlineType>, Partial<OutlineType>>(
    `/v1/scripts/outlines/${params?.id}`,
    params,
  );
}

export default function useUpdateOutline() {
  return useMutation({ mutationFn: updateOutline });
}
