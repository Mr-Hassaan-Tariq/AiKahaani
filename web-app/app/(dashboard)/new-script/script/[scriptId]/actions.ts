'use server';

import { ScriptType } from './types';
import { getServerDataAction } from 'lib/utils/getServerDataAction';

export async function getScript(scriptId: string) {
  return await getServerDataAction<ScriptType>(`/v1/scripts/scripts/${scriptId}`);
}
