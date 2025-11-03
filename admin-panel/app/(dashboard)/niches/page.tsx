'use client';

import { useEffect, useMemo, useState } from 'react';

import { getClientDataAction } from 'lib/utils/clientDataActions';
import { NichePaginatedResponse } from '../types';
import NicheCard from './_components/NicheCard';
import Pagination from './_components/Pagination';
import SearchHeader from './_components/SearchHeader';

export default function NicheVault() {
  const [searchInput, setSearchInput] = useState('');
  const [niches, setNiches] = useState<NichePaginatedResponse['results']>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const itemsPerPage = 12;

  const [activeFilters, setActiveFilters] = useState<Record<string, string[]>>({});

  const availableFilters = useMemo(
    () => ({
      Tone: ['Educational', 'Casual', 'Emotional', 'Satirical'],
      Format: ['Storytelling', 'Review', 'Explainer', 'Interview'],
      Popularity: ['Hype', 'Classic', 'Trending', 'New'],
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
      const url = buildQuery(page, searchInput, activeFilters);
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
    fetchNiches(currentPage);
  }, [currentPage, searchInput, activeFilters]);

  const filteredNiches = niches.filter((niche) =>
    niche.title.toLowerCase().includes(searchInput.toLowerCase()),
  );

  const visibleNiches = filteredNiches.slice(0, itemsPerPage);

  return (
    <main>
      <SearchHeader
        searchInput={searchInput}
        handleSearchChange={handleSearchChange}
        availableFilters={availableFilters}
        onApplyFilters={handleApplyFilters}
      />

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
            {visibleNiches.length > 0 ? (
              visibleNiches.map((niche) => (
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
