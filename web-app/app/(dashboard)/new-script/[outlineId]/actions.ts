'use server';

import { OutlineType } from '@/(dashboard)/new-script/types';

import { getServerDataAction } from 'lib/utils/getServerDataAction';

export async function getOutline(outlineId: string) {
  return await getServerDataAction<OutlineType>(`v1/scripts/outlines/${outlineId}/`);
}
