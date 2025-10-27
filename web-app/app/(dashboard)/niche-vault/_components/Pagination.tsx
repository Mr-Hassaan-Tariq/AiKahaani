'use client';

import { useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

type PaginationProps = {
  totalItems: number;
  itemsPerPage: number;
  onPageChange?: (page: number) => void;
};

export default function Pagination({ totalItems, itemsPerPage, onPageChange }: PaginationProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  useEffect(() => {
    onPageChange?.(currentPage);
  }, [currentPage]);

  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages) return;
    setCurrentPage(page);
  };

  return (
    <div className="mt-10 flex w-full items-center justify-between">
      {/* Pagination buttons */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1C1C1C] text-white hover:bg-[#2C2C2C]"
          disabled={currentPage === 1}
        >
          <ChevronLeft size={16} />
        </button>

        {[...Array(totalPages)].slice(0, 3).map((_, i) => {
          const page = i + 1;
          return (
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
          );
        })}

        <button
          onClick={() => handlePageChange(currentPage + 1)}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1C1C1C] text-white hover:bg-[#2C2C2C]"
          disabled={currentPage === totalPages}
        >
          <ChevronRight size={16} />
        </button>
      </div>

      {/* Showing text */}
      <p className="text-sm text-[#AAACA6]">
        Page {currentPage} of {totalPages} — Showing{' '}
        {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} niches
      </p>
    </div>
  );
}
