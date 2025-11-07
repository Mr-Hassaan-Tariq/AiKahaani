import Link from 'next/link';
import { Plus, SlidersHorizontal } from 'lucide-react';

import { SearchIcon } from './components';
import FilterNicheModal from './FilterNicheModal';
import Button from 'components/ui/Button';
import Text from 'components/ui/Text';

interface SearchHeaderProps {
  searchInput: string;
  handleSearchChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  availableFilters?: Record<string, string[]>;
  onApplyFilters?: (filters: Record<string, string[]>) => void;
  initialFilters?: Record<string, string[]>;
}

export default function SearchHeader({
  searchInput,
  handleSearchChange,
  availableFilters,
  onApplyFilters,
  initialFilters = {},
}: SearchHeaderProps) {
  const handleApply = (filters: Record<string, string[]>) => {
    if (onApplyFilters) onApplyFilters(filters);
  };

  return (
    <section className="mb-5 w-full space-y-6 text-center">
      {/* Heading */}
      <div>
        <h1 className="text-2xl font-semibold text-white md:text-3xl">
          Explore Viral YouTube Niches
        </h1>
        <Text className="mt-2 text-[#AAACA6]" variant="base">
          Browse hundreds of proven styles to find the perfect fit <br /> for your channel — or
          create your own.
        </Text>
      </div>

      <div className="mx-auto flex max-w-3xl items-center justify-center gap-2">
        <div className="relative w-full">
          {SearchIcon}
          <input
            className="h-full w-full rounded-2xl border-none bg-[#262724] p-4 pl-10 text-base leading-6 tracking-[-0.2px] text-white outline-0 placeholder:text-[#737373]"
            placeholder="Search by topic or style..."
            value={searchInput}
            onChange={handleSearchChange}
          />
        </div>

        <FilterNicheModal
          trigger={
            <Button variant="gray" className="w-[160px]">
              <SlidersHorizontal />
              <span className="hidden lg:block">Filters</span>
            </Button>
          }
          availableFilters={availableFilters}
          onApply={handleApply}
          initialFilters={initialFilters}
        />
        <Link href={'/niches/create'}>
          <Button variant="gray" className="w-[160px]">
            <Plus />
            <span className="hidden lg:block">Create</span>
          </Button>
        </Link>
      </div>
    </section>
  );
}
