'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import Filter from '@assets/svg/filters.svg';

import { SEARCH_PLACEHOLDER, TABS_CONFIG } from '../_constants';
import { ScriptsTabProps } from '../_types';
import { SearchIcon } from './components';
import FilterScriptModal from './FilterScriptModal';
import Button from 'components/ui/Button';
import Row from 'components/ui/Row';
import { Tabs, TabsList, TabsTrigger } from 'components/shadcn_ui/tabs';

export default function ScriptsTab({
  children,
  onSearch,
  onFilter,
  onApplyFilters,
  searchValue = '',
  className = '',
}: ScriptsTabProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const query = searchParams.get('query');
  const [searchInput, setSearchInput] = useState(searchValue);

  const activeTab =
    TABS_CONFIG.find((tab) => tab.path === pathname + (query ? `?query=${query}` : '')) ??
    TABS_CONFIG[0];

  // Handle search input changes
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onSearch?.(searchInput);
    }, 300); // Debounce search

    return () => clearTimeout(timeoutId);
  }, [searchInput, onSearch]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
  };

  const handleFilterClick = () => {
    onFilter?.();
  };

  return (
    <div className={`my-5 flex flex-col ${className}`}>
      <Row className="flex-col items-start justify-normal gap-6 lg:flex-row lg:items-center lg:justify-between">
        <Row className="justify-start">
          <div className="relative w-[280px] lg:w-[350px]">
            {SearchIcon}
            <input
              className="h-full w-full rounded-2xl border-none bg-[#262724] p-4 pl-10 text-base leading-6 tracking-[-0.2px] text-white outline-0 placeholder:text-[#737373]"
              placeholder={SEARCH_PLACEHOLDER}
              value={searchInput}
              onChange={handleSearchChange}
            />
          </div>
          <FilterScriptModal
            trigger={
              <Button
                variant="gray"
                className="hover:bg-bg-white/10 w-[50px] p-3 hover:text-white lg:w-[140px]"
                onClick={handleFilterClick}
              >
                <Image src={Filter} alt="Filter" />
                <span className="hidden lg:block">Filters</span>
              </Button>
            }
            onApplyFilters={onApplyFilters}
          />
        </Row>
        <div className="w-full overflow-x-auto overflow-y-visible lg:w-fit">
          <Tabs defaultValue={activeTab?.label || ''} className="">
            <TabsList className="flex h-[52px] w-full items-center justify-normal gap-1.5 bg-transparent md:justify-normal md:gap-4 lg:h-fit">
              {TABS_CONFIG.map((tab) => (
                <Link key={tab.label} href={tab.path}>
                  <TabsTrigger
                    value={tab.label}
                    className="whitespace-nowrap rounded-full border-gray-100 bg-[#FFFFFF1A] px-3 py-3 text-base font-bold text-white data-[state=active]:bg-white data-[state=active]:text-black lg:px-6 lg:py-[18px]"
                  >
                    {tab.label}
                  </TabsTrigger>
                </Link>
              ))}
            </TabsList>
          </Tabs>
        </div>
      </Row>

      <div className="scrollbar pb-3">{children}</div>
    </div>
  );
}
