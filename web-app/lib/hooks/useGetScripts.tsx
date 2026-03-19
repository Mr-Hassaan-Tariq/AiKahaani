'use client';

import { useQuery } from '@tanstack/react-query';

import { getClientDataAction } from 'lib/utils/clientDataActions';

export interface Script {
  uuid: string;
  title: string;
  outline_title?: string;
  word_count?: number;
  status?: string;
}

export interface ScriptsResponse {
  data: Script[];
  meta: { total: number };
}

async function getScripts(): Promise<ScriptsResponse> {
  // Backend returns { scripts: FullScriptOut[], total: N } after envelope unwrap
  const raw = await getClientDataAction<{ scripts: any[]; total: number }>('/v1/scripts/scripts');
  const items: Script[] = (raw?.scripts ?? []).map((s: any) => ({
    uuid: s.id ?? s.uuid,
    title: s.title ?? 'Untitled',
    word_count: s.word_count,
    status: s.status,
  }));
  return { data: items, meta: { total: raw?.total ?? items.length } };
}

export default function useGetScripts() {
  return useQuery({
    queryKey: ['get-scripts'],
    queryFn: getScripts,
    retry: false,
    refetchOnWindowFocus: false,
    staleTime: 1000 * 60 * 5,
  });
}
