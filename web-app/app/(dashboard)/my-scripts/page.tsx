'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

import MyScriptsContent from './_components/MyScriptsContent';
import { getScriptGenerations, ScriptFilters } from './actions';

type TabKey = 'all' | 'outlines' | 'scripts';

export default function MyScriptsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('all');
  const [searchValue, setSearchValue] = useState<string>('');
  const [ordering, setOrdering] = useState<'created' | 'modified' | undefined>(undefined);
  const [wordCountMin, setWordCountMin] = useState<number | undefined>(undefined);
  const [wordCountMax, setWordCountMax] = useState<number | undefined>(undefined);
  const [durationMin, setDurationMin] = useState<number | undefined>(undefined);
  const [durationMax, setDurationMax] = useState<number | undefined>(undefined);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize] = useState<number>(12);
  const [scripts, setScripts] = useState<any[] | undefined>(undefined);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<any>(null);

  const apiFilters = useMemo<ScriptFilters>(
    () => ({
      search: searchValue || undefined,
      type: activeTab === 'outlines' ? 'outline' : activeTab === 'scripts' ? 'script' : undefined,
      ordering,
      word_count_min: wordCountMin,
      word_count_max: wordCountMax,
      duration_min: durationMin,
      duration_max: durationMax,
      limit: pageSize,
      offset: (currentPage - 1) * pageSize,
    }),
    [
      activeTab,
      searchValue,
      ordering,
      wordCountMin,
      wordCountMax,
      durationMin,
      durationMax,
      pageSize,
      currentPage,
    ],
  );

  const fetchScripts = useCallback(async (filters: ScriptFilters) => {
    setLoading(true);
    setError(null);
    try {
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

  useEffect(() => {
    fetchScripts(apiFilters);
  }, [apiFilters, fetchScripts]);

  const handleApplyFilters = useCallback(
    (filters: {
      ordering?: 'created' | 'modified';
      wordCountMin?: number;
      wordCountMax?: number;
      durationMin?: number;
      durationMax?: number;
    }) => {
      if (filters.ordering !== undefined) setOrdering(filters.ordering);
      if (filters.wordCountMin !== undefined) setWordCountMin(filters.wordCountMin);
      if (filters.wordCountMax !== undefined) setWordCountMax(filters.wordCountMax);
      if (filters.durationMin !== undefined) setDurationMin(filters.durationMin);
      if (filters.durationMax !== undefined) setDurationMax(filters.durationMax);
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
    <div className="flex flex-col">
      <div className="px-4 py-6 sm:px-7 sm:py-7">
        <MyScriptsContent
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
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          pageSize={pageSize}
          setPageSize={() => {}}
          scripts={scripts}
          totalCount={totalCount}
          loading={loading}
          error={error}
          onApplyFilters={handleApplyFilters}
          onClearFilters={handleClearFilters}
        />
      </div>
    </div>
  );
}
