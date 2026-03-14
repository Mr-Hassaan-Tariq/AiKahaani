import { Search, SlidersHorizontal } from 'lucide-react';

import FilterNicheModal from './FilterNicheModal';
import { Button } from 'components/ui/Button';

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
  return (
    <section className="mb-6 space-y-4 text-center">
      <div>
        <h2 className="text-xl font-semibold text-foreground">Explore Viral YouTube Niches</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Browse hundreds of proven styles to find the perfect fit for your channel.
        </p>
      </div>

      <div className="mx-auto flex max-w-xl items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            className="h-9 w-full rounded-lg border border-border bg-background pl-9 pr-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Search by topic or style…"
            value={searchInput}
            onChange={handleSearchChange}
          />
        </div>
        <FilterNicheModal
          trigger={
            <Button variant="outline" size="sm">
              <SlidersHorizontal className="h-4 w-4" /> Filters
            </Button>
          }
          availableFilters={availableFilters}
          onApply={onApplyFilters ?? (() => {})}
          initialFilters={initialFilters}
        />
      </div>
    </section>
  );
}
