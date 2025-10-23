'use client';

import React from 'react';
import Image from 'next/image';
import Filter from '@assets/svg/filters.svg';

import { SEARCH_PLACEHOLDER, TABS_CONFIG } from '../_constants';
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
  onApplyFilters?: (filters: any) => void;
  onClearFilters?: () => void;
  searchValue?: string;
}

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

  React.useEffect(() => {
    setLocalInput(searchValue);
  }, [searchValue]);

  React.useEffect(() => {
    onSearch?.(localInput);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [localInput]);

  const handleTabClick = (tabLabel: string) => {
    const found = TABS_CONFIG.find((t) => t.label === tabLabel);
    if (!found) return;

    if (found.query === 'outlines') setActiveTab('outlines');
    else if (found.query === 'scripts') setActiveTab('scripts');
    else setActiveTab('all');
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
            onApplyFilters={onApplyFilters}
            onClearFilters={onClearFilters}
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

      <div className="scrollbar pb-3">{children}</div>
    </div>
  );
}
