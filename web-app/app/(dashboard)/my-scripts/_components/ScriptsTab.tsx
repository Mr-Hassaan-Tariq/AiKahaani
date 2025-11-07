'use client';

import React from 'react';
import Image from 'next/image';
import Filter from '@assets/svg/filters.svg';

import { SEARCH_PLACEHOLDER, TABS_CONFIG } from '../_constants';
import { FiltersState } from '../_utils/filterUtils';
import { SearchIcon } from './components';
import FilterScriptModal from './FilterScriptModal';
import Button from 'components/ui/Button';
import Row from 'components/ui/Row';
import { Tabs, TabsList, TabsTrigger } from 'components/shadcn_ui/tabs';

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

  // local filters state for showing chips
  const [filters, setFilters] = React.useState<FiltersState>({ ...DEFAULT_FILTERS });

  React.useEffect(() => {
    setLocalInput(searchValue);
  }, [searchValue]);

  React.useEffect(() => {
    onSearch?.(localInput);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [localInput]);

  // modal applied filters handler
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

    if (key === 'wordCount') {
      next.wordCount = DEFAULT_FILTERS.wordCount;
    } else if (key === 'lastEdited') {
      next.lastEdited = DEFAULT_FILTERS.lastEdited;
    } else if (key === 'videoDuration') {
      next.videoDuration = null;
    }

    setFilters(next);
    onApplyFilters?.(next);

    const isDefault =
      next.lastEdited === DEFAULT_FILTERS.lastEdited &&
      next.wordCount[0] === DEFAULT_FILTERS.wordCount[0] &&
      next.wordCount[1] === DEFAULT_FILTERS.wordCount[1] &&
      next.videoDuration === DEFAULT_FILTERS.videoDuration;

    if (isDefault) {
      onClearFilters?.();
    }
  };

  const renderFilterLabel = (key: keyof FiltersState, value: any) => {
    if (key === 'lastEdited') {
      return value === 'most_recent' ? 'Most recent' : 'Oldest';
    }
    if (key === 'wordCount') {
      return `${value[0].toLocaleString()} - ${value[1].toLocaleString()} words`;
    }
    if (key === 'videoDuration') {
      return value
        ? value === '<20'
          ? '< 20 min'
          : value === '>60'
            ? '> 60 min'
            : `${value} min`
        : null;
    }
    return String(value);
  };

  const isFilterActive = (key: keyof FiltersState) => {
    if (key === 'wordCount') {
      return !(
        filters.wordCount[0] === DEFAULT_FILTERS.wordCount[0] &&
        filters.wordCount[1] === DEFAULT_FILTERS.wordCount[1]
      );
    }
    if (key === 'lastEdited') {
      return filters.lastEdited !== DEFAULT_FILTERS.lastEdited;
    }
    if (key === 'videoDuration') {
      return filters.videoDuration !== null;
    }
    return false;
  };

  return (
    <div className="my-5 flex flex-col">
      <Row className="flex-col items-start justify-normal gap-6 lg:flex-row lg:items-center lg:justify-between">
        <Row className="justify-start">
          <div className="relative w-[280px] lg:w-[350px]">
            {SearchIcon}
            <input
              className="h-full w-full rounded-2xl border-none bg-[#262724] p-4 pl-10 text-base leading-6 tracking-[-0.2px] text-white outline-0 placeholder:text-[#737373]"
              placeholder={SEARCH_PLACEHOLDER}
              value={localInput}
              onChange={(e) => setLocalInput(e.target.value)}
            />
          </div>

          <FilterScriptModal
            trigger={
              <Button
                variant="gray"
                className="hover:bg-bg-white/10 w-[50px] p-3 hover:text-white lg:w-[140px]"
                onClick={() => {}}
              >
                <Image src={Filter} alt="Filter" />
                <span className="hidden lg:block">Filters</span>
              </Button>
            }
            initialFilters={filters}
            onApplyFilters={handleApplyFiltersFromModal}
            onClearFilters={handleClearFiltersFromModal}
          />
        </Row>

        <div className="w-full overflow-x-auto overflow-y-visible lg:w-fit">
          <Tabs
            defaultValue={TABS_CONFIG[0].label}
            value={
              TABS_CONFIG.find((t) => t.query === activeTab || (!t.query && activeTab === 'all'))
                ?.label
            }
            className=""
          >
            <TabsList className="flex h-[52px] w-full items-center justify-normal gap-1.5 bg-transparent md:justify-normal md:gap-4 lg:h-fit">
              {TABS_CONFIG.map((tab) => (
                <button key={tab.label} onClick={() => handleTabClick(tab.label)}>
                  <TabsTrigger
                    value={tab.label}
                    className="whitespace-nowrap rounded-full border-gray-100 bg-[#FFFFFF1A] px-3 py-3 text-base font-bold text-white data-[state=active]:bg-white data-[state=active]:text-black lg:px-6 lg:py-[18px]"
                  >
                    {tab.label}
                  </TabsTrigger>
                </button>
              ))}
            </TabsList>
          </Tabs>
        </div>
      </Row>

      {/* Active filter chips */}
      <div className="mt-3 flex w-full flex-wrap gap-2">
        {(['lastEdited', 'wordCount', 'videoDuration'] as (keyof FiltersState)[]).map((k) => {
          if (!isFilterActive(k)) return null;
          const label = renderFilterLabel(k, (filters as any)[k]);
          if (!label) return null;
          return (
            <div
              key={k}
              className="flex items-center gap-2 rounded-full bg-transparent px-3 py-1 text-sm text-white"
            >
              <span>{label}</span>
              <button
                onClick={() => removeFilter(k)}
                aria-label={`Remove ${k} filter`}
                className="flex h-5 w-5 items-center justify-center rounded-full hover:bg-white/20"
              >
                {/* simple close icon */}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  width="12"
                  height="12"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 6l12 12M6 18L18 6" />
                </svg>
              </button>
            </div>
          );
        })}
      </div>

      <div className="scrollbar pb-3">{children}</div>
    </div>
  );
}
