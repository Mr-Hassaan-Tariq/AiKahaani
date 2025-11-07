'use client';

import { useEffect, useMemo, useState } from 'react';

import { NichePaginatedResponse } from '../types';
import NicheCard from './_components/NicheCard';
import Pagination from './_components/Pagination';
import SearchHeader from './_components/SearchHeader';
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

  const availableFilters = useMemo(
    () => ({
      Tone: [
        'Neutral',
        'Professional',
        'Educational',
        'Engaging',
        'Conversational',
        'Conversational',
      ],
    }),
    [],
  );

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
    params.append('page_size', String(itemsPerPage));
    const offset = (page - 1) * itemsPerPage;
    params.append('limit', String(itemsPerPage));
    params.append('offset', String(offset));

    if (search) params.append('search', search);

    Object.entries(filters).forEach(([displayKey, values]) => {
      if (!values || values.length === 0) return;
      const key = toQueryKey(displayKey);
      params.append(key, values.join(','));
    });

    const url = `v1/admin/niches/?${params.toString()}`;

    return url;
  };

  const fetchNiches = async (page = 1) => {
    setIsLoading(true);
    try {
      const url = buildQuery(page, debouncedSearch, activeFilters);
      const data = await getClientDataAction<NichePaginatedResponse>(url);
      setNiches(data.results || []);
      setTotalItems(data.count || 0);
    } catch (error) {
      console.error('Error fetching niches:', error);
      setNiches([]);
      setTotalItems(0);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [searchInput]);

  useEffect(() => {
    fetchNiches(currentPage);
  }, [currentPage, debouncedSearch, activeFilters]);

  const filteredNiches = niches.filter((niche) =>
    niche.title.toLowerCase().includes(debouncedSearch.toLowerCase()),
  );

  const removeFilter = (category: string, valueToRemove: string) => {
    setActiveFilters((prev) => {
      const prevValues = prev[category] || [];
      const nextValues = prevValues.filter((v) => v !== valueToRemove);

      const next = { ...prev };
      if (nextValues.length > 0) {
        next[category] = nextValues;
      } else {
        delete next[category];
      }

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
    <main>
      <SearchHeader
        searchInput={searchInput}
        handleSearchChange={handleSearchChange}
        availableFilters={availableFilters}
        onApplyFilters={handleApplyFilters}
        initialFilters={activeFilters}
      />

      <div className="mx-auto mb-5 max-w-xl">
        <div className="flex flex-wrap gap-2">
          {activeChips.length === 0
            ? null
            : activeChips.map((chip) => (
                <div
                  key={`${chip.category}-${chip.value}`}
                  className="flex items-center gap-2 rounded-full bg-transparent px-3 py-1 text-sm text-white"
                >
                  <span className="text-xs font-medium">
                    {chip.category}: {chip.value}
                  </span>
                  <button
                    onClick={() => removeFilter(chip.category, chip.value)}
                    aria-label={`Remove ${chip.category} ${chip.value}`}
                    className="flex h-5 w-5 items-center justify-center rounded-full hover:bg-white/20"
                  >
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
              ))}
        </div>
      </div>

      {isLoading ? (
        <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="h-64 rounded-lg bg-white/10"></div>
            </div>
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredNiches.length > 0 ? (
              filteredNiches.map((niche) => (
                <NicheCard
                  id={niche.id}
                  key={niche.id}
                  title={niche.title}
                  description={niche.tagline || 'No description available'}
                  tone={niche.tone || []}
                  pacing={niche.pacing || []}
                  topChannels={niche.top_channels || []}
                  thumbnailUrl={niche.thumbnail_url}
                />
              ))
            ) : (
              <div className="col-span-full flex min-h-[200px] items-center justify-center">
                <p className="text-gray-400">No niches found.</p>
              </div>
            )}
          </div>

          {totalItems > itemsPerPage && (
            <Pagination
              totalItems={totalItems}
              itemsPerPage={itemsPerPage}
              currentPage={currentPage}
              onPageChange={(page: number) => setCurrentPage(page)}
            />
          )}
        </>
      )}
    </main>
  );
}
