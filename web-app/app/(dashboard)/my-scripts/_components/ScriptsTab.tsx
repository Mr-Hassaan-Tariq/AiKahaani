'use client';

import React from 'react';
import { Filter, Search, X } from 'lucide-react';

import { SEARCH_PLACEHOLDER, TABS_CONFIG } from '../_constants';
import { FiltersState } from '../_utils/filterUtils';
import FilterScriptModal from './FilterScriptModal';
import { Button } from 'components/ui/Button';
import { cn } from 'lib/utils';

type TabKey = 'all' | 'outlines' | 'scripts';

interface Props {
  children: React.ReactNode;
  activeTab: TabKey;
  setActiveTab: (t: TabKey) => void;
  onSearch?: (q: string) => void;
  onApplyFilters?: (filters: FiltersState) => void;
  onClearFilters?: () => void;
  searchValue?: string;
}

const DEFAULT_FILTERS: FiltersState = {
  lastEdited: 'most_recent',
  wordCount: [1000, 2000],
  videoDuration: null,
};

export default function ScriptsTab({
  children,
  activeTab,
  setActiveTab,
  onSearch,
  onApplyFilters,
  onClearFilters,
  searchValue = '',
}: Props) {
  const [localInput, setLocalInput] = React.useState<string>(searchValue);
  const [filters, setFilters] = React.useState<FiltersState>({ ...DEFAULT_FILTERS });

  React.useEffect(() => { setLocalInput(searchValue); }, [searchValue]);
  React.useEffect(() => { onSearch?.(localInput); }, [localInput]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleApplyFiltersFromModal = (applied: FiltersState) => {
    setFilters(applied);
    onApplyFilters?.(applied);
  };

  const handleClearFiltersFromModal = () => {
    setFilters({ ...DEFAULT_FILTERS });
    onClearFilters?.();
  };

  const handleTabClick = (tabLabel: string) => {
    const found = TABS_CONFIG.find((t) => t.label === tabLabel);
    if (!found) return;
    if (found.query === 'outlines') setActiveTab('outlines');
    else if (found.query === 'scripts') setActiveTab('scripts');
    else setActiveTab('all');
  };

  const removeFilter = (key: keyof FiltersState) => {
    const next: FiltersState = { ...filters };
    if (key === 'wordCount') next.wordCount = DEFAULT_FILTERS.wordCount;
    else if (key === 'lastEdited') next.lastEdited = DEFAULT_FILTERS.lastEdited;
    else if (key === 'videoDuration') next.videoDuration = null;
    setFilters(next);
    onApplyFilters?.(next);
    const isDefault =
      next.lastEdited === DEFAULT_FILTERS.lastEdited &&
      next.wordCount[0] === DEFAULT_FILTERS.wordCount[0] &&
      next.wordCount[1] === DEFAULT_FILTERS.wordCount[1] &&
      next.videoDuration === DEFAULT_FILTERS.videoDuration;
    if (isDefault) onClearFilters?.();
  };

  const renderFilterLabel = (key: keyof FiltersState, value: any) => {
    if (key === 'lastEdited') return value === 'most_recent' ? 'Most recent' : 'Oldest';
    if (key === 'wordCount') return `${value[0].toLocaleString()}–${value[1].toLocaleString()} words`;
    if (key === 'videoDuration') return value ? (value === '<20' ? '< 20 min' : value === '>60' ? '> 60 min' : `${value} min`) : null;
    return String(value);
  };

  const isFilterActive = (key: keyof FiltersState) => {
    if (key === 'wordCount') return !(filters.wordCount[0] === DEFAULT_FILTERS.wordCount[0] && filters.wordCount[1] === DEFAULT_FILTERS.wordCount[1]);
    if (key === 'lastEdited') return filters.lastEdited !== DEFAULT_FILTERS.lastEdited;
    if (key === 'videoDuration') return filters.videoDuration !== null;
    return false;
  };

  const activeFilterKeys = (['lastEdited', 'wordCount', 'videoDuration'] as (keyof FiltersState)[]).filter(isFilterActive);

  return (
    <div className="flex flex-col gap-4">
      {/* Controls row */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        {/* Search */}
        <div className="relative w-full sm:w-64 lg:w-80">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            className="h-9 w-full rounded-lg border border-border bg-background pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder={SEARCH_PLACEHOLDER}
            value={localInput}
            onChange={(e) => setLocalInput(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-3">
          {/* Filter button */}
          <FilterScriptModal
            trigger={
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4" />
                Filters
                {activeFilterKeys.length > 0 && (
                  <span className="flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] text-primary-foreground">
                    {activeFilterKeys.length}
                  </span>
                )}
              </Button>
            }
            initialFilters={filters}
            onApplyFilters={handleApplyFiltersFromModal}
            onClearFilters={handleClearFiltersFromModal}
          />

          {/* Tabs */}
          <div className="flex items-center rounded-lg border border-border bg-muted p-0.5">
            {TABS_CONFIG.map((tab) => {
              const isActive =
                tab.query === 'outlines' ? activeTab === 'outlines'
                : tab.query === 'scripts' ? activeTab === 'scripts'
                : activeTab === 'all';
              return (
                <button
                  key={tab.label}
                  onClick={() => handleTabClick(tab.label)}
                  className={cn(
                    'rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
                    isActive
                      ? 'bg-background text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground',
                  )}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Active filter chips */}
      {activeFilterKeys.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {activeFilterKeys.map((k) => {
            const label = renderFilterLabel(k, (filters as any)[k]);
            if (!label) return null;
            return (
              <span
                key={k}
                className="flex items-center gap-1.5 rounded-full border border-border bg-accent px-2.5 py-1 text-xs text-foreground"
              >
                {label}
                <button
                  onClick={() => removeFilter(k)}
                  className="text-muted-foreground hover:text-foreground"
                  aria-label={`Remove ${k} filter`}
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            );
          })}
        </div>
      )}

      {children}
    </div>
  );
}
