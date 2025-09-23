'use server';

import { ScriptGeneration } from 'lib/api/types';
import { getServerDataAction, updateServerDataAction } from 'lib/utils/getServerDataAction';

export interface ScriptFilters {
  search?: string;
  type?: 'script' | 'outline';
  ordering?: 'created' | 'modified';
  word_count_min?: number;
  word_count_max?: number;
  duration_min?: number;
  duration_max?: number;
  limit?: number;
  offset?: number;
}

export async function getScriptGenerations(filters: ScriptFilters = {}) {
  // Build query parameters
  const params = new URLSearchParams();

  if (filters.search) params.append('search', filters.search);
  if (filters.type) params.append('type', filters.type);
  if (filters.ordering) params.append('ordering', filters.ordering);
  if (filters.word_count_min !== undefined)
    params.append('word_count_min', filters.word_count_min.toString());
  if (filters.word_count_max !== undefined)
    params.append('word_count_max', filters.word_count_max.toString());
  if (filters.duration_min !== undefined)
    params.append('duration_min', filters.duration_min.toString());
  if (filters.duration_max !== undefined)
    params.append('duration_max', filters.duration_max.toString());
  if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
  if (filters.offset !== undefined) params.append('offset', filters.offset.toString());

  const queryString = params.toString();
  const endpoint = `v1/scripts/generations/${queryString ? `?${queryString}` : ''}`;

  return await getServerDataAction<{ count: number; results: ScriptGeneration[] }>(endpoint);
}

export async function deleteScriptGeneration(uuid: string) {
  return await updateServerDataAction<{ message: string }>(
    `v1/scripts/outlines/${uuid}/`,
    null,
    'DELETE',
  );
}

export async function updateScriptGeneration(uuid: string, updates: Partial<ScriptGeneration>) {
  return await updateServerDataAction<ScriptGeneration>(`v1/scripts/generations/${uuid}/`, updates);
}

export async function handleDeleteScript(uuid: string) {
  try {
    const response = await deleteScriptGeneration(uuid);

    if (response && 'message' in response) {
      // Handle success, e.g., show a toast notification
      // Example: toast.success('Script deleted successfully');
    } else {
      throw new Error('Unexpected response format');
    }
  } catch {
    // Handle error, e.g., show an error notification
    // Example: toast.error('Failed to delete script');
    // Log the error or integrate with an error tracking system
  }
}
