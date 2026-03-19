'use client';

import { SetStateAction, useEffect, useMemo, useState } from 'react';
import { Search, Sparkles } from 'lucide-react';

import { Niche } from '../types';
import NicheCard from './_components/NicheCard';
import Pagination from './_components/Pagination';
import { cn } from 'lib/utils';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import { PaginatedApiResponse } from 'lib/utils/getServerDataAction';

const FEATURED = {
  imageUrl:
    'https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=1200&auto=format&fit=crop',
  title: 'The Ultimate Storytelling Formula',
  description:
    'Master the art of retention with a script structure designed for high-stakes narratives and massive payoff reveals.',
};

const CATEGORIES = [
  'All Niches',
  'Tech & Gadgets',
  'Finance',
  'Documentary',
  'Vlogs & Lifestyle',
  'Gaming',
];

const CATEGORY_KEYWORDS: Record<string, string[]> = {
  'Tech & Gadgets': ['tech', 'ai', 'gadget', 'review', 'future', 'work'],
  Finance: ['finance', 'invest', 'money', 'wealth'],
  Documentary: ['crime', 'documentary', 'story', 'true', 'deep dive'],
  'Vlogs & Lifestyle': [
    'lifestyle',
    'vlog',
    'self',
    'mindset',
    'improvement',
    'travel',
    'personal',
  ],
  Gaming: ['gaming', 'game', 'esport'],
};

export default function NicheVault() {
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All Niches');
  const [niches, setNiches] = useState<Niche[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const itemsPerPage = 12;

  const buildQuery = (page = 1, search = '') => {
    const offset = (page - 1) * itemsPerPage;
    const params = new URLSearchParams();
    params.append('limit', String(itemsPerPage));
    params.append('offset', String(offset));
    if (search) params.append('search', search);
    return `/v1/niches?${params.toString()}`;
  };

  const fetchNiches = async (page = 1) => {
    setIsLoading(true);
    try {
      const url = buildQuery(page, debouncedSearch);
      const data = await getClientDataAction<PaginatedApiResponse<Niche>>(url);
      setNiches(data?.data || []);
      setTotalItems(data?.meta?.total || 0);
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

  useEffect(() => {
    fetchNiches(currentPage);
  }, [currentPage, debouncedSearch]); // eslint-disable-line react-hooks/exhaustive-deps

  const filteredNiches = useMemo(() => {
    if (activeCategory === 'All Niches') return niches;
    const keywords = CATEGORY_KEYWORDS[activeCategory] || [];
    return niches.filter((n) => {
      const haystack = [n.title, n.tagline, ...(n.tone || []), ...(n.pacing || [])]
        .join(' ')
        .toLowerCase();
      return keywords.some((kw) => haystack.includes(kw));
    });
  }, [niches, activeCategory]);

  return (
    <div className="px-4 py-6 sm:px-8 sm:py-10">
      <div className="mx-auto flex w-full max-w-[1200px] flex-col gap-6 sm:gap-8">
        {/* ── Featured Hero Banner ── */}
        <div
          className="relative flex w-full items-end overflow-hidden rounded-xl"
          style={{ minHeight: 220 }}
        >
          <img
            src={FEATURED.imageUrl}
            alt="Featured"
            className="absolute inset-0 h-full w-full object-cover"
          />
          <div
            className="absolute inset-0"
            style={{
              background: 'linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.18) 100%)',
            }}
          />
          <div className="relative z-10 flex max-w-[600px] flex-col gap-2 p-5 sm:gap-3 sm:p-10">
            <span className="inline-flex w-fit items-center gap-1.5 rounded-full bg-white/90 px-2.5 py-1 text-xs font-semibold text-[#0F172A] backdrop-blur-sm">
              <Sparkles className="h-3 w-3" />
              Featured Blueprint
            </span>
            <h2 className="m-0 text-[22px] font-extrabold leading-tight tracking-tight text-white sm:text-[32px]">
              {FEATURED.title}
            </h2>
            <p className="m-0 hidden text-base leading-relaxed text-white/80 sm:block">
              {FEATURED.description}
            </p>
          </div>
        </div>

        {/* ── Controls: category pills + search ── */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
          {/* Pills — horizontal scroll on mobile */}
          <div
            className="flex gap-2 overflow-x-auto pb-2 sm:flex-wrap sm:overflow-visible sm:pb-0"
            style={{ scrollbarWidth: 'none' }}
          >
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setActiveCategory(cat)}
                className={cn(
                  'shrink-0 whitespace-nowrap rounded-full border border-transparent px-4 py-2 text-sm font-medium transition-colors',
                  activeCategory === cat
                    ? 'bg-foreground text-background'
                    : 'bg-secondary text-muted-foreground hover:bg-secondary/70',
                )}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="flex h-11 w-full items-center gap-3 rounded-full bg-secondary px-4 sm:w-[280px] sm:shrink-0">
            <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
            <input
              className="w-full border-none bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
              placeholder="Search templates..."
              value={searchInput}
              onChange={(e) => {
                setSearchInput(e.target.value);
                setCurrentPage(1);
              }}
            />
          </div>
        </div>

        {/* ── Template Grid ── */}
        {isLoading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="animate-pulse rounded-xl bg-muted" style={{ height: 320 }} />
            ))}
          </div>
        ) : filteredNiches.length > 0 ? (
          <>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filteredNiches.map((niche) => (
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
              ))}
            </div>
            {totalItems > itemsPerPage && (
              <Pagination
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
                onPageChange={(page: SetStateAction<number>) => setCurrentPage(page)}
              />
            )}
          </>
        ) : (
          <div className="py-20 text-center">
            <p className="text-sm font-medium text-foreground">No niches found</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Try a different search or category.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
