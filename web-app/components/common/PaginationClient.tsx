'use client';

import React from 'react';

import Pagination from './Pagination';

interface PaginationClientProps {
  currentPage: number;
  totalCount: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
}

const PaginationClient: React.FC<PaginationClientProps> = ({
  currentPage,
  totalCount,
  pageSize,
  onPageChange,
}) => {
  return (
    <Pagination
      currentPage={currentPage}
      totalCount={totalCount}
      pageSize={pageSize}
      onPageChange={onPageChange}
    />
  );
};

export default PaginationClient;
