'use client';

import { useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

type PaginationProps = {
  totalItems: number;
  itemsPerPage: number;
  currentPage: number;
  onPageChange?: (page: number) => void;
};

export default function Pagination({
  totalItems,
  itemsPerPage,
  currentPage,
  onPageChange,
}: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));

  useEffect(() => {
    if (currentPage < 1 && onPageChange) onPageChange(1);
    if (currentPage > totalPages && onPageChange) onPageChange(totalPages);
  }, [currentPage, totalPages]);

  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages) return;
    onPageChange?.(page);
  };

  const getPageRange = () => {
    const maxButtons = 7;
    const half = Math.floor(maxButtons / 2);
    let start = Math.max(1, currentPage - half);
    const end = Math.min(totalPages, start + maxButtons - 1);

    if (end - start + 1 < maxButtons) {
      start = Math.max(1, end - maxButtons + 1);
    }

    const pages = [];
    for (let i = start; i <= end; i++) pages.push(i);
    return pages;
  };

  const pages = getPageRange();

  return (
    <div className="mt-10 flex w-full items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1C1C1C] text-white hover:bg-[#2C2C2C]"
          disabled={currentPage === 1}
        >
          <ChevronLeft size={16} />
        </button>

        {pages.map((page) => (
          <button
            key={page}
            onClick={() => handlePageChange(page)}
            className={`flex h-8 w-8 items-center justify-center rounded-full ${
              currentPage === page
                ? 'bg-white text-black'
                : 'bg-[#1C1C1C] text-white hover:bg-[#2C2C2C]'
            }`}
          >
            {page}
          </button>
        ))}

        <button
          onClick={() => handlePageChange(currentPage + 1)}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1C1C1C] text-white hover:bg-[#2C2C2C]"
          disabled={currentPage === totalPages}
        >
          <ChevronRight size={16} />
        </button>
      </div>

      <p className="text-sm text-[#AAACA6]">
        Page {currentPage} of {totalPages} — Showing{' '}
        {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} niches
      </p>
    </div>
  );
}
