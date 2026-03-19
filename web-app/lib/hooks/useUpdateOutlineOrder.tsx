'use client';

import { useMutation } from '@tanstack/react-query';

import { patchClientDataAction } from 'lib/utils/clientDataActions';

interface UpdateOutlineOrderParams {
  uuid: string;
  sectionOrder: number[];
  outlineData: { sections: any[] };
}

async function updateOutlineOrder(params: UpdateOutlineOrderParams) {
  return await patchClientDataAction<UpdateOutlineOrderParams, any>(
    `/v1/scripts/outlines/${params.uuid}`,
    {
      section_order: params.sectionOrder,
      outline_data: params.outlineData,
    },
  );
}

export default function useUpdateOutlineOrder() {
  return useMutation({ mutationFn: updateOutlineOrder });
}
