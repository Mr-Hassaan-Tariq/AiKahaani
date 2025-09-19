'use client';

import { OutlineType } from '@/(dashboard)/new-script/types';
import { useMutation } from '@tanstack/react-query';

import { putClientDataAction } from 'lib/utils/clientDataActions';

async function updateOutline(params: Partial<OutlineType>) {
  return await putClientDataAction<Partial<OutlineType>, Partial<OutlineType>>(
    `v1/scripts/outlines/${params?.uuid}/`,
    params,
  );
}

export default function useUpdateOutline() {
  return useMutation({ mutationFn: updateOutline });
}
