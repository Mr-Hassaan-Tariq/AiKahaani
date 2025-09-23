'use client';

import React from 'react';
import { useRouter } from 'next/navigation';

import Pagination from './Pagination';

interface PaginationClientProps {
  currentPage: number;
  totalCount: number;
  pageSize: number;
  searchParams?: {
    [key: string]: string | undefined;
  };
}

const PaginationClient: React.FC<PaginationClientProps> = ({
  currentPage,
  totalCount,
  pageSize,
  searchParams,
}) => {
  const router = useRouter();

  const handlePageChange = (page: number) => {
    // Define allowed keys for the query string
    const allowedKeys = [
      'page',
      'limit',
      'offset',
      'search',
      'ordering',
      'word_count_min',
      'word_count_max',
      'duration_min',
      'duration_max',
    ];

    // Filter searchParams to include only allowed keys
    const filteredSearchParams = Object.keys(searchParams || {})
      .filter((key) => allowedKeys.includes(key))
      .reduce(
        (obj, key) => {
          obj[key] = searchParams![key];
          return obj;
        },
        {} as { [key: string]: string | undefined },
      );

    // Add the new page value
    const newSearchParams = { ...filteredSearchParams, page: page.toString() };

    // Construct the query string
    const queryString = new URLSearchParams(newSearchParams).toString();

    // Navigate to the new URL
    router.push(`?${queryString}`);
  };

  return (
    <Pagination
      currentPage={currentPage}
      totalCount={totalCount}
      pageSize={pageSize}
      onPageChange={handlePageChange}
    />
  );
};

export default PaginationClient;
