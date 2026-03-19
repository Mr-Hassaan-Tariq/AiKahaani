'use server';

import { ScriptGeneration } from 'lib/api/types';
import { getServerDataAction, updateServerDataAction } from 'lib/utils/getServerDataAction';

type BackendOutline = {
  id: string;
  title: string;
  status: string;
  tokens_used: number;
  generation_time: number;
  outline_data: Record<string, any>;
  section_order: number[];
  created_at: string;
  updated_at: string;
  [key: string]: any;
};

function normalizeItem(item: BackendOutline, type: 'outline' | 'script'): ScriptGeneration {
  return {
    uuid: item.id,
    title: item.title,
    type,
    status: item.status as ScriptGeneration['status'],
    status_display: item.status,
    word_count: item.word_count ?? null,
    estimated_duration: item.estimated_duration ?? null,
    section_count: Array.isArray(item.section_order) ? item.section_order.length : null,
    created: item.created_at,
    modified: item.updated_at,
    is_published: item.is_published ?? null,
    version: item.version ?? 1,
  };
}

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
  const params = new URLSearchParams();

  if (filters.search) params.append('search', filters.search);
  if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
  if (filters.offset !== undefined) params.append('skip', filters.offset.toString());

  const queryString = params.toString();
  const qs = queryString ? `?${queryString}` : '';

  type RawOutlines = { outlines: BackendOutline[]; total: number };
  type RawScripts = { scripts: BackendOutline[]; total: number };

  if (filters.type === 'script') {
    const result = await getServerDataAction<RawScripts>(`/v1/scripts/scripts${qs}`);
    if (result.isError || !result.data) return result as any;
    const raw = result.data as any;
    const items = (raw.scripts ?? []).map((i: BackendOutline) => normalizeItem(i, 'script'));
    return { ...result, data: { data: items, meta: { total: raw.total ?? 0 } } };
  }

  if (filters.type === 'outline') {
    const result = await getServerDataAction<RawOutlines>(`/v1/scripts/outlines${qs}`);
    if (result.isError || !result.data) return result as any;
    const raw = result.data as any;
    const items = (raw.outlines ?? []).map((i: BackendOutline) => normalizeItem(i, 'outline'));
    return { ...result, data: { data: items, meta: { total: raw.total ?? 0 } } };
  }

  // 'all' tab: fetch both in parallel and merge, sorted by created_at desc
  const [outlinesResult, scriptsResult] = await Promise.all([
    getServerDataAction<RawOutlines>(`/v1/scripts/outlines${qs}`),
    getServerDataAction<RawScripts>(`/v1/scripts/scripts${qs}`),
  ]);

  const outlineItems = !outlinesResult.isError
    ? ((outlinesResult.data as any)?.outlines ?? []).map((i: BackendOutline) =>
        normalizeItem(i, 'outline'),
      )
    : [];
  const scriptItems = !scriptsResult.isError
    ? ((scriptsResult.data as any)?.scripts ?? []).map((i: BackendOutline) =>
        normalizeItem(i, 'script'),
      )
    : [];

  const allItems: ScriptGeneration[] = [...outlineItems, ...scriptItems].sort(
    (a, b) => new Date(b.created).getTime() - new Date(a.created).getTime(),
  );
  const total =
    ((outlinesResult.data as any)?.total ?? 0) + ((scriptsResult.data as any)?.total ?? 0);

  return {
    isError: false,
    error: undefined,
    data: { data: allItems, meta: { total } },
  };
}

export async function deleteScriptGeneration(uuid: string) {
  return await updateServerDataAction<{ message: string }>(
    `/v1/scripts/outlines/${uuid}`,
    null,
    'DELETE',
  );
}

export async function deleteScript(uuid: string) {
  return await updateServerDataAction<{ message: string }>(
    `/v1/scripts/scripts/${uuid}`,
    null,
    'DELETE',
  );
}

export async function updateScriptGeneration(uuid: string, updates: Partial<ScriptGeneration>) {
  return await updateServerDataAction<ScriptGeneration>(`/v1/scripts/outlines/${uuid}`, updates);
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
