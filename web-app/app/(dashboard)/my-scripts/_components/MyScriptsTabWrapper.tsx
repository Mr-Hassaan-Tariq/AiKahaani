'use client';

import { useCallback, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

import { convertFiltersToAPI, FiltersState } from '../_utils/filterUtils';
import ScriptsTab from './ScriptsTab';

interface MyScriptsTabWrapperProps {
  children: React.ReactNode;
  searchValue?: string;
}

export default function MyScriptsTabWrapper({ children, searchValue }: MyScriptsTabWrapperProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleSearch = useCallback(
    (query: string) => {
      // Clear existing timeout
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }

      // Set new timeout for debounced search
      searchTimeoutRef.current = setTimeout(() => {
        const params = new URLSearchParams(searchParams.toString());

        if (query.trim()) {
          params.set('search', query.trim());
        } else {
          params.delete('search');
        }

        // Update URL with search parameter
        const newUrl = params.toString() ? `?${params.toString()}` : '';
        router.push(`/my-scripts${newUrl}`);
      }, 500);
    },
    [router, searchParams],
  );

  const handleApplyFilters = useCallback(
    (filters: FiltersState) => {
      const params = new URLSearchParams(searchParams.toString());

      // Convert filters to API parameters
      const apiFilters = convertFiltersToAPI(filters);

      // Clear existing filter parameters
      params.delete('ordering');
      params.delete('word_count_min');
      params.delete('word_count_max');
      params.delete('duration_min');
      params.delete('duration_max');

      // Add new filter parameters
      if (apiFilters.ordering) params.set('ordering', apiFilters.ordering);
      if (apiFilters.word_count_min !== undefined)
        params.set('word_count_min', apiFilters.word_count_min.toString());
      if (apiFilters.word_count_max !== undefined)
        params.set('word_count_max', apiFilters.word_count_max.toString());
      if (apiFilters.duration_min !== undefined)
        params.set('duration_min', apiFilters.duration_min.toString());
      if (apiFilters.duration_max !== undefined)
        params.set('duration_max', apiFilters.duration_max.toString());

      // Update URL with filter parameters
      const newUrl = params.toString() ? `?${params.toString()}` : '';
      router.push(`/my-scripts${newUrl}`);
    },
    [router, searchParams],
  );

  return (
    <ScriptsTab
      onSearch={handleSearch}
      onApplyFilters={handleApplyFilters}
      searchValue={searchValue}
    >
      {children}
    </ScriptsTab>
  );
}
