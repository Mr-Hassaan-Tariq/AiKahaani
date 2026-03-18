'use client';

import { ChevronLeft, ChevronRight } from 'lucide-react';

import { cn } from 'lib/utils';

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
    if (end - start < maxButtons - 1) start = Math.max(1, end - maxButtons + 1);
    for (let i = start; i <= end; i++) pages.push(i);
    return pages;
  };

  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between">
      <p className="text-xs text-muted-foreground">
        {Math.min(currentPage * itemsPerPage, totalItems)} of {totalItems} notifications
      </p>

      <div className="flex items-center gap-1">
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-background text-foreground transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ChevronLeft size={14} />
        </button>

        {getVisiblePages().map((page) => (
          <button
            key={page}
            onClick={() => handlePageChange(page)}
            className={cn(
              'flex h-8 w-8 items-center justify-center rounded-lg border text-xs font-medium transition-colors',
              currentPage === page
                ? 'border-primary bg-primary text-primary-foreground'
                : 'border-border bg-background text-foreground hover:bg-accent',
            )}
          >
            {page}
          </button>
        ))}

        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-border bg-background text-foreground transition-colors hover:bg-accent disabled:cursor-not-allowed disabled:opacity-40"
        >
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  );
}
