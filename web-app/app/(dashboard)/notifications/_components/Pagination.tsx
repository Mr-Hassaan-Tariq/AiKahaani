'use client';

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
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages) return;
    onPageChange?.(page);
  };

  const getVisiblePages = () => {
    const pages: number[] = [];
    const maxButtons = 3;
    let start = Math.max(1, currentPage - 1);
    const end = Math.min(totalPages, start + maxButtons - 1);

    if (end - start < maxButtons - 1) {
      start = Math.max(1, end - maxButtons + 1);
    }

    for (let i = start; i <= end; i++) pages.push(i);
    return pages;
  };

  if (totalPages <= 1) return null;

  return (
    <div className="mt-10 flex w-full items-center justify-between">
      {/* Pagination buttons */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1C1C1C] text-white hover:bg-[#2C2C2C] disabled:opacity-40"
          disabled={currentPage === 1}
        >
          <ChevronLeft size={16} />
        </button>

        {getVisiblePages().map((page) => (
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
          className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1C1C1C] text-white hover:bg-[#2C2C2C] disabled:opacity-40"
          disabled={currentPage === totalPages}
        >
          <ChevronRight size={16} />
        </button>
      </div>

      {/* Showing text */}
      <p className="text-sm text-[#AAACA6]">
        Showing {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} notifications
      </p>
    </div>
  );
}
