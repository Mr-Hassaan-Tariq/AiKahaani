'use client';

import React, { useCallback, useRef } from 'react';

import { convertFiltersToAPI, FiltersState } from '../_utils/filterUtils';
import ScriptsTab from './ScriptsTab';

type TabKey = 'all' | 'outlines' | 'scripts';

interface Props {
  children: React.ReactNode;
  activeTab: TabKey;
  setActiveTab: (t: TabKey) => void;

  searchValue: string;
  setSearchValue: (v: string) => void;

  onApplyFilters?: (filters: {
    ordering?: 'created' | 'modified' | undefined;
    wordCountMin?: number | undefined;
    wordCountMax?: number | undefined;
    durationMin?: number | undefined;
    durationMax?: number | undefined;
  }) => void;

  onClearFilters?: () => void;
}

export default function MyScriptsTabWrapper({
  children,
  activeTab,
  setActiveTab,
  searchValue,
  setSearchValue,
  onApplyFilters,
  onClearFilters,
}: Props) {
  const searchTimeoutRef = useRef<number | undefined>(undefined);

  // Debounced search: we still debounce inside the wrapper so parent state isn't spammed
  const handleSearch = useCallback(
    (value: string) => {
      if (searchTimeoutRef.current) {
        window.clearTimeout(searchTimeoutRef.current);
      }

      // using window.setTimeout so the returned id is number in browsers
      searchTimeoutRef.current = window.setTimeout(() => {
        setSearchValue(value);
      }, 300);
    },
    [setSearchValue],
  );

  const handleApplyFilters = useCallback(
    (filters: FiltersState) => {
      // Convert UI filters to simple object and bubble up
      const apiFilters = convertFiltersToAPI(filters);

      onApplyFilters?.({
        ordering: apiFilters.ordering,
        wordCountMin: apiFilters.word_count_min,
        wordCountMax: apiFilters.word_count_max,
        durationMin: apiFilters.duration_min,
        durationMax: apiFilters.duration_max,
      });
    },
    [onApplyFilters],
  );

  return (
    <ScriptsTab
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      onSearch={handleSearch}
      onApplyFilters={handleApplyFilters}
      onClearFilters={onClearFilters}
      searchValue={searchValue}
    >
      {children}
    </ScriptsTab>
  );
}
