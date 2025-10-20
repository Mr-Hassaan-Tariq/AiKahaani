'use client';

import React from 'react';

import PaginationClient from '../../../../components/common/PaginationClient';
import MyScriptsList from './MyScriptsList';
import MyScriptsTabWrapper from './MyScriptsTabWrapper';
import OutlinesPage from './OutlinesPage';
import ScriptsPage from './ScriptsPage';

type TabKey = 'all' | 'outlines' | 'scripts';

interface Props {
  activeTab: TabKey;
  setActiveTab: (t: TabKey) => void;

  searchValue: string;
  setSearchValue: (v: string) => void;

  ordering?: 'created' | 'modified' | undefined;
  setOrdering?: (v: 'created' | 'modified' | undefined) => void;

  wordCountMin?: number | undefined;
  setWordCountMin?: (v?: number) => void;
  wordCountMax?: number | undefined;
  setWordCountMax?: (v?: number) => void;

  durationMin?: number | undefined;
  setDurationMin?: (v?: number) => void;
  durationMax?: number | undefined;
  setDurationMax?: (v?: number) => void;

  currentPage: number;
  setCurrentPage: (p: number) => void;
  pageSize: number;
  setPageSize: (s: number) => void;

  scripts?: any[] | undefined;
  totalCount: number;
  loading: boolean;
  error: any;

  onApplyFilters: (filters: {
    ordering?: 'created' | 'modified' | undefined;
    wordCountMin?: number | undefined;
    wordCountMax?: number | undefined;
    durationMin?: number | undefined;
    durationMax?: number | undefined;
  }) => void;

  onClearFilters: () => void;
}

export default function MyScriptsContent(props: Props) {
  const {
    activeTab,
    setActiveTab,
    searchValue,
    setSearchValue,
    scripts,
    totalCount,
    error,
    currentPage,
    setCurrentPage,
    pageSize,
    setPageSize,
    onApplyFilters,
    onClearFilters,
  } = props;

  const renderBody = () => {
    if (activeTab === 'outlines') {
      return <OutlinesPage initialScripts={scripts} />;
    }

    if (activeTab === 'scripts') {
      return <ScriptsPage initialScripts={scripts} />;
    }

    // default 'all'
    return (
      <MyScriptsList
        initialScripts={scripts}
        error={error}
        isError={!!error}
        searchQuery={searchValue}
      />
    );
  };

  return (
    <div className="flex flex-col">
      <MyScriptsTabWrapper
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        searchValue={searchValue}
        setSearchValue={setSearchValue}
        onApplyFilters={onApplyFilters}
        onClearFilters={onClearFilters}
      >
        {renderBody()}
      </MyScriptsTabWrapper>

      <div className="mt-4">
        <PaginationClient
          currentPage={currentPage}
          totalCount={totalCount}
          pageSize={pageSize}
          onPageChange={(p: number) => setCurrentPage(p)}
          onPageSizeChange={(s: number) => setPageSize(s)}
        />
      </div>
    </div>
  );
}
