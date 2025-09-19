'use server';

import { GenerationPromptType } from './types';
import { getServerDataAction } from 'lib/utils/getServerDataAction';

export async function getConfig() {
  return await getServerDataAction<GenerationPromptType>('v1/scripts/config/');
}
