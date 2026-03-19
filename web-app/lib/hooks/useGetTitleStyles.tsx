'use client';

import { useQuery } from '@tanstack/react-query';

import { getClientDataAction } from 'lib/utils/clientDataActions';

export interface Tone {
  id: number;
  name: string;
}

export interface TemplateStyle {
  id: number;
  name: string;
  min_length: number;
  max_length: number;
  duration: number;
  description: string;
  word_range: string;
}

export interface LengthRange {
  min: number;
  max: number;
  default: number;
}

export interface TitleStylesResponse {
  /** Backend returns "tones" (not "results") */
  tones: Tone[];
  template_styles: TemplateStyle[];
  length_range: LengthRange;
}

async function getTitleStyles() {
  return await getClientDataAction<TitleStylesResponse>('/v1/scripts/config');
}

export default function useGetTitleStyles() {
  return useQuery({
    queryKey: ['get-title-styles'],
    queryFn: () => getTitleStyles(),
    retry: false,
    refetchOnWindowFocus: false,
    staleTime: 1000 * 60 * 60 * 1,
  });
}
