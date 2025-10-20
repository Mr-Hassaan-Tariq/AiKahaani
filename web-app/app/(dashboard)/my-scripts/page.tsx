'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import ComponentNav from '@/(dashboard)/_components/ComponentNav';

import { Magicpan } from './_components/components';
import MyScriptsContent from './_components/MyScriptsContent';
import { getScriptGenerations, ScriptFilters } from './actions';

type TabKey = 'all' | 'outlines' | 'scripts';

export default function MyScriptsPage() {
  // UI state
  const [activeTab, setActiveTab] = useState<TabKey>('all');
  const [searchValue, setSearchValue] = useState<string>('');
  const [ordering, setOrdering] = useState<'created' | 'modified' | undefined>(undefined);
  const [wordCountMin, setWordCountMin] = useState<number | undefined>(undefined);
  const [wordCountMax, setWordCountMax] = useState<number | undefined>(undefined);
  const [durationMin, setDurationMin] = useState<number | undefined>(undefined);
  const [durationMax, setDurationMax] = useState<number | undefined>(undefined);

  // Pagination state
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(12);

  // Data state
  const [scripts, setScripts] = useState<any[] | undefined>(undefined);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<any>(null);

  // Build filters for API call
  const apiFilters = useMemo<ScriptFilters>(() => {
    const type =
      activeTab === 'outlines' ? 'outline' : activeTab === 'scripts' ? 'script' : undefined;

    return {
      search: searchValue || undefined,
      type,
      ordering: ordering,
      word_count_min: wordCountMin,
      word_count_max: wordCountMax,
      duration_min: durationMin,
      duration_max: durationMax,
      limit: pageSize,
      offset: (currentPage - 1) * pageSize,
    };
  }, [
    activeTab,
    searchValue,
    ordering,
    wordCountMin,
    wordCountMax,
    durationMin,
    durationMax,
    pageSize,
    currentPage,
  ]);

  const fetchScripts = useCallback(async (filters: ScriptFilters) => {
    setLoading(true);
    setError(null);
    try {
      // If getScriptGenerations is server-only, replace this with a client fetch to your API
      // e.g. const res = await fetch('/api/scripts', { method: 'POST', body: JSON.stringify(filters) })
      const { data, error: apiError, isError } = await getScriptGenerations(filters);

      if (isError || apiError) {
        setError(apiError || true);
        setScripts([]);
        setTotalCount(0);
      } else {
        setScripts(data?.results ?? []);
        setTotalCount(data?.count ?? 0);
      }
    } catch (err) {
      setError(err);
      setScripts([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch on initial mount and whenever apiFilters changes
  useEffect(() => {
    fetchScripts(apiFilters);
  }, [apiFilters, fetchScripts]);

  // Handlers passed down
  const handleApplyFilters = useCallback(
    (filters: {
      ordering?: 'created' | 'modified' | undefined;
      wordCountMin?: number | undefined;
      wordCountMax?: number | undefined;
      durationMin?: number | undefined;
      durationMax?: number | undefined;
    }) => {
      if (filters.ordering !== undefined) setOrdering(filters.ordering);
      if (filters.wordCountMin !== undefined) setWordCountMin(filters.wordCountMin);
      if (filters.wordCountMax !== undefined) setWordCountMax(filters.wordCountMax);
      if (filters.durationMin !== undefined) setDurationMin(filters.durationMin);
      if (filters.durationMax !== undefined) setDurationMax(filters.durationMax);

      // NOTE: per your request, we DO NOT reset currentPage here.
    },
    [],
  );

  const handleClearFilters = useCallback(() => {
    setOrdering(undefined);
    setWordCountMin(undefined);
    setWordCountMax(undefined);
    setDurationMin(undefined);
    setDurationMax(undefined);
  }, []);

  return (
    <div className="flex min-h-screen flex-col space-y-6">
      <ComponentNav
        title="My Scripts"
        buttonText="Generate New Script"
        buttonIcon={Magicpan}
        buttonClassName="lg:max-w-[240px]"
        _onButtonClick="/new-script"
      />

      <MyScriptsContent
        // state
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        searchValue={searchValue}
        setSearchValue={setSearchValue}
        ordering={ordering}
        setOrdering={setOrdering}
        wordCountMin={wordCountMin}
        setWordCountMin={setWordCountMin}
        wordCountMax={wordCountMax}
        setWordCountMax={setWordCountMax}
        durationMin={durationMin}
        setDurationMin={setDurationMin}
        durationMax={durationMax}
        setDurationMax={setDurationMax}
        // pagination
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        pageSize={pageSize}
        setPageSize={setPageSize}
        // data
        scripts={scripts}
        totalCount={totalCount}
        loading={loading}
        error={error}
        // handlers
        onApplyFilters={handleApplyFilters}
        onClearFilters={handleClearFilters}
      />
    </div>
  );
}
