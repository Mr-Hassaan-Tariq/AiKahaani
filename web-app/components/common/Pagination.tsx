'use client';

import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

import { cn } from 'lib/utils';

interface PaginationProps {
  currentPage: number;
  totalCount: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({ currentPage, totalCount, pageSize, onPageChange }) => {
  const totalPages = Math.ceil(totalCount / pageSize);
  if (totalPages <= 1) return null;

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) onPageChange(page);
  };

  return (
    <div className="flex items-center justify-center gap-1">
      <button
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-background text-foreground transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-40"
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        <ChevronLeft size={14} />
      </button>

      {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
        <button
          key={page}
          className={cn(
            'flex h-8 w-8 items-center justify-center rounded-lg border text-xs font-medium transition-colors',
            currentPage === page
              ? 'border-primary bg-primary text-primary-foreground'
              : 'border-border bg-background text-foreground hover:bg-accent',
          )}
          onClick={() => handlePageChange(page)}
          disabled={currentPage === page}
        >
          {page}
        </button>
      ))}

      <button
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-background text-foreground transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-40"
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        <ChevronRight size={14} />
      </button>
    </div>
  );
};

export default Pagination;
