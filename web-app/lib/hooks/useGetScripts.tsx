'use client';

import { useQuery } from '@tanstack/react-query';

import { getClientDataAction } from 'lib/utils/clientDataActions';

export interface Script {
  outline_title: any;
  uuid: number;
  title: string;
}

export interface ScriptsResponse {
  results: Script[];
  count: number;
  next: string;
  previous: string;
}

async function getScripts() {
  return await getClientDataAction<ScriptsResponse>('v1/scripts/');
}

export default function useGetScripts() {
  return useQuery({
    queryKey: ['get-scripts'],
    queryFn: () => getScripts(),
    retry: false,
    refetchOnWindowFocus: false,
    staleTime: 1000 * 60 * 60 * 1,
  });
}
