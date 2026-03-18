'use client';

import { SetStateAction, useEffect, useMemo, useState } from 'react';
import { Search, Sparkles } from 'lucide-react';

import { NichePaginatedResponse } from '../types';
import NicheCard from './_components/NicheCard';
import Pagination from './_components/Pagination';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import { cn } from 'lib/utils';

const FEATURED = {
  imageUrl: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?q=80&w=1200&auto=format&fit=crop',
  title: 'The Ultimate Storytelling Formula',
  description: 'Master the art of retention with a script structure designed for high-stakes narratives and massive payoff reveals.',
};

const CATEGORIES = ['All Niches', 'Tech & Gadgets', 'Finance', 'Documentary', 'Vlogs & Lifestyle', 'Gaming'];

const CATEGORY_KEYWORDS: Record<string, string[]> = {
  'Tech & Gadgets': ['tech', 'ai', 'gadget', 'review', 'future', 'work'],
  'Finance': ['finance', 'invest', 'money', 'wealth'],
  'Documentary': ['crime', 'documentary', 'story', 'true', 'deep dive'],
  'Vlogs & Lifestyle': ['lifestyle', 'vlog', 'self', 'mindset', 'improvement', 'travel', 'personal'],
  'Gaming': ['gaming', 'game', 'esport'],
};

export default function NicheVault() {
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All Niches');
  const [niches, setNiches] = useState<NichePaginatedResponse['results']>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const itemsPerPage = 12;

  const buildQuery = (page = 1, search = '') => {
    const params = new URLSearchParams();
    params.append('page', String(page));
    if (search) params.append('search', search);
    return `auth/niches/?${params.toString()}`;
  };

  const fetchNiches = async (page = 1) => {
    setIsLoading(true);
    try {
      const url = buildQuery(page, debouncedSearch);
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

  useEffect(() => { fetchNiches(currentPage); }, [currentPage, debouncedSearch]); // eslint-disable-line react-hooks/exhaustive-deps

  const filteredNiches = useMemo(() => {
    if (activeCategory === 'All Niches') return niches;
    const keywords = CATEGORY_KEYWORDS[activeCategory] || [];
    return niches.filter((n) => {
      const haystack = [n.title, n.tagline, ...(n.tone || []), ...(n.pacing || [])].join(' ').toLowerCase();
      return keywords.some((kw) => haystack.includes(kw));
    });
  }, [niches, activeCategory]);

  return (
    <div className="px-8 py-10">
      <div className="w-full max-w-[1200px] mx-auto flex flex-col gap-8">

        {/* ── Featured Hero Banner ── */}
        <div
          className="relative w-full rounded-xl overflow-hidden flex items-end"
          style={{ height: 280 }}
        >
          <img
            src={FEATURED.imageUrl}
            alt="Featured"
            className="absolute inset-0 w-full h-full object-cover"
          />
          <div
            className="absolute inset-0"
            style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.18) 100%)' }}
          />
          <div className="relative z-10 flex flex-col gap-3 p-10 max-w-[600px]">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/90 backdrop-blur-sm text-[#0F172A] text-xs font-semibold w-fit">
              <Sparkles className="h-3 w-3" />
              Featured Blueprint
            </span>
            <h2 className="text-[32px] font-extrabold text-white leading-tight tracking-tight m-0">
              {FEATURED.title}
            </h2>
            <p className="text-base text-white/80 leading-relaxed m-0">
              {FEATURED.description}
            </p>
          </div>
        </div>

        {/* ── Controls: category pills + search ── */}
        <div className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-2 flex-wrap">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setActiveCategory(cat)}
                className={cn(
                  'px-4 py-2 rounded-full text-sm font-medium transition-colors whitespace-nowrap border border-transparent',
                  activeCategory === cat
                    ? 'bg-foreground text-background'
                    : 'bg-secondary text-muted-foreground hover:bg-secondary/70',
                )}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3 bg-secondary rounded-full h-11 px-4 w-[280px] shrink-0">
            <Search className="h-4 w-4 text-muted-foreground shrink-0" />
            <input
              className="bg-transparent border-none outline-none text-sm text-foreground placeholder:text-muted-foreground w-full"
              placeholder="Search templates..."
              value={searchInput}
              onChange={(e) => { setSearchInput(e.target.value); setCurrentPage(1); }}
            />
          </div>
        </div>

        {/* ── Template Grid ── */}
        {isLoading ? (
          <div className="grid gap-6" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))' }}>
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-xl bg-muted animate-pulse" style={{ height: 320 }} />
            ))}
          </div>
        ) : filteredNiches.length > 0 ? (
          <>
            <div className="grid gap-6" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))' }}>
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
            <p className="mt-1 text-xs text-muted-foreground">Try a different search or category.</p>
          </div>
        )}

      </div>
    </div>
  );
}
