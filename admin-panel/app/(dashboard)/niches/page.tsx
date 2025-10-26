'use client';

import { SetStateAction, useEffect, useState } from 'react';

import { NichePaginatedResponse } from '../types';
import NicheCard from './_components/NicheCard';
import Pagination from './_components/Pagination';
import SearchHeader from './_components/SearchHeader';
import { getClientDataAction } from 'lib/utils/clientDataActions';

export default function NicheVault() {
  const [searchInput, setSearchInput] = useState('');
  const [niches, setNiches] = useState<NichePaginatedResponse['results']>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
  };

  const fetchNiches = async (page = 1) => {
    try {
      const data = await getClientDataAction<NichePaginatedResponse>(
        `v1/admin/niches/?page=${page}`,
      );
      setNiches(data.results || []);
      setTotalItems(data.count || 0);
    } catch (error) {
      console.error('Error fetching niches:', error);
    }
  };

  useEffect(() => {
    fetchNiches(currentPage);
  }, [currentPage]);

  const filteredNiches = niches.filter((niche) =>
    niche.title.toLowerCase().includes(searchInput.toLowerCase()),
  );

  return (
    <main>
      <SearchHeader searchInput={searchInput} handleSearchChange={handleSearchChange} />

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
          <p className="text-gray-400">No niches found.</p>
        )}
      </div>

      {totalItems > itemsPerPage && (
        <Pagination
          totalItems={totalItems}
          itemsPerPage={itemsPerPage}
          onPageChange={(page: SetStateAction<number>) => setCurrentPage(page)}
        />
      )}
    </main>
  );
}
