'use client';

import { SetStateAction, useEffect, useMemo, useState } from 'react';
import { X } from 'lucide-react';

import { NichePaginatedResponse } from '../types';
import NicheCard from './_components/NicheCard';
import Pagination from './_components/Pagination';
import SearchHeader from './_components/SearchHeader';
import Topbar from 'components/layout/Topbar';
import { getClientDataAction } from 'lib/utils/clientDataActions';

export default function NicheVault() {
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [niches, setNiches] = useState<NichePaginatedResponse['results']>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const itemsPerPage = 12;
  const [activeFilters, setActiveFilters] = useState<Record<string, string[]>>({});

  const availableFilters = useMemo(() => ({
    Tone: ['Neutral', 'Professional', 'Educational', 'Engaging', 'Conversational'],
  }), []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
    setCurrentPage(1);
  };

  const handleApplyFilters = (filters: Record<string, string[]>) => {
    setActiveFilters(filters);
    setCurrentPage(1);
  };

  const toQueryKey = (displayName: string) => displayName.toLowerCase().replace(/\s+/g, '_');

  const buildQuery = (page = 1, search = '', filters: Record<string, string[]>) => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    if (search) params.append('search', search);
    Object.entries(filters).forEach(([displayKey, values]) => {
      if (!values || values.length === 0) return;
      params.append(toQueryKey(displayKey), values.join(','));
    });
    return `auth/niches/?${params.toString()}`;
  };

  const fetchNiches = async (page = 1) => {
    setIsLoading(true);
    try {
      const url = buildQuery(page, debouncedSearch, activeFilters);
      const data = await getClientDataAction<NichePaginatedResponse>(url);
      setNiches(data.results || []);
      setTotalItems(data.count || 0);
    } catch {
      setNiches([]);
      setTotalItems(0);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedSearch(searchInput.trim()), 500);
    return () => clearTimeout(handler);
  }, [searchInput]);

  useEffect(() => { fetchNiches(currentPage); }, [currentPage, debouncedSearch, activeFilters]); // eslint-disable-line react-hooks/exhaustive-deps

  const filteredNiches = niches.filter((niche) =>
    niche.title.toLowerCase().includes(debouncedSearch.toLowerCase()),
  );

  const removeFilter = (category: string, valueToRemove: string) => {
    setActiveFilters((prev) => {
      const next = { ...prev };
      const nextValues = (prev[category] || []).filter((v) => v !== valueToRemove);
      if (nextValues.length > 0) next[category] = nextValues;
      else delete next[category];
      setCurrentPage(1);
      return next;
    });
  };

  const activeChips = useMemo(() => {
    const chips: { category: string; value: string }[] = [];
    Object.entries(activeFilters).forEach(([category, values]) => {
      (values || []).forEach((v) => chips.push({ category, value: v }));
    });
    return chips;
  }, [activeFilters]);

  return (
    <div className="flex flex-col">
      <Topbar
        title="Niche Vault"
        subtitle="Explore proven content styles and apply them to your scripts."
      />

      <div className="px-6 py-6">
        <SearchHeader
          searchInput={searchInput}
          handleSearchChange={handleSearchChange}
          availableFilters={availableFilters}
          onApplyFilters={handleApplyFilters}
          initialFilters={activeFilters}
        />

        {/* Active filter chips */}
        {activeChips.length > 0 && (
          <div className="mb-4 flex flex-wrap gap-2">
            {activeChips.map((chip) => (
              <span
                key={`${chip.category}-${chip.value}`}
                className="flex items-center gap-1.5 rounded-full border border-border bg-accent px-2.5 py-1 text-xs text-foreground"
              >
                {chip.category}: {chip.value}
                <button
                  onClick={() => removeFilter(chip.category, chip.value)}
                  className="text-muted-foreground hover:text-foreground"
                  aria-label={`Remove ${chip.category} ${chip.value}`}
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Grid */}
        {isLoading ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-64 animate-pulse rounded-xl bg-muted" />
            ))}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredNiches.length > 0 ? (
                filteredNiches.map((niche) => (
                  <NicheCard
                    key={niche.id}
                    id={niche.id}
                    title={niche.title}
                    description={niche.tagline || 'No description available'}
                    tone={niche.tone || []}
                    pacing={niche.pacing || []}
                    topChannels={niche.top_channels || []}
                    thumbnailUrl={niche.thumbnail_url}
                  />
                ))
              ) : (
                <div className="col-span-full py-16 text-center">
                  <p className="text-sm font-medium text-foreground">No niches found</p>
                  <p className="mt-1 text-xs text-muted-foreground">Try a different search term or clear filters.</p>
                </div>
              )}
            </div>

            {totalItems > itemsPerPage && (
              <Pagination
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
                onPageChange={(page: SetStateAction<number>) => setCurrentPage(page)}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}
