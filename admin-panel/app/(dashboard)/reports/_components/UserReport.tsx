'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Cookies from 'js-cookie';
import { Download, Search } from 'lucide-react';

import Pagination from '../../_components/Pagination';
import { baseUrl } from 'lib/api';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import CustomTable from 'components/common/CustomTable';
import TextField from 'components/common/TextField';

interface UserReportData {
  name: string;
  email: string;
  total_titles_generated: number;
  total_short_scripts: number;
  total_medium_scripts: number;
  total_long_scripts: number;
}

interface PaginatedApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: UserReportData[];
}

export default function UserReport() {
  const [data, setData] = useState<UserReportData[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const [exporting, setExporting] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Build query parameters
      const params = new URLSearchParams();
      if (startDate) {
        params.append('start_date', startDate);
      }
      if (endDate) {
        params.append('end_date', endDate);
      }
      // Add pagination parameters
      const offset = (currentPage - 1) * pageSize;
      params.append('limit', pageSize.toString());
      params.append('offset', offset.toString());

      const queryString = params.toString();
      const endpoint = `v1/admin/users-report/?${queryString}`;

      const response = await getClientDataAction<PaginatedApiResponse>(endpoint);

      if (response) {
        // Handle paginated response from backend
        setData(response.results || []);
        setTotalCount(response.count || 0);
      } else {
        setData([]);
        setTotalCount(0);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load data';
      setError(errorMessage);
      setData([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, currentPage, pageSize]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Note: Search is currently client-side only. For better performance with large datasets,
  // consider implementing server-side search in the backend.
  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) {
      return data;
    }

    const search = searchTerm.toLowerCase();
    return data.filter(
      (user) =>
        user.name.toLowerCase().includes(search) ||
        user.email.toLowerCase().includes(search) ||
        user.total_titles_generated.toString().includes(search) ||
        user.total_short_scripts.toString().includes(search) ||
        user.total_medium_scripts.toString().includes(search) ||
        user.total_long_scripts.toString().includes(search),
    );
  }, [data, searchTerm]);

  // When search term changes, reset to page 1
  useEffect(() => {
    if (searchTerm) {
      setCurrentPage(1);
    }
  }, [searchTerm]);

  // When date filters change, reset to page 1
  useEffect(() => {
    setCurrentPage(1);
  }, [startDate, endDate]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const token = Cookies.get('access_token');
      if (!token) {
        setError('Authentication token not found');
        return;
      }

      // Build query parameters for export
      const params = new URLSearchParams();
      if (startDate) {
        params.append('start_date', startDate);
      }
      if (endDate) {
        params.append('end_date', endDate);
      }

      const queryString = params.toString();
      const endpoint = queryString
        ? `${baseUrl}v1/admin/users-report/export/?${queryString}`
        : `${baseUrl}v1/admin/users-report/export/`;

      const response = await fetch(endpoint, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to export data');
      }

      // Get the blob and create a download link
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Extract filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'users_report.csv';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to export data';
      setError(errorMessage);
    } finally {
      setExporting(false);
    }
  };

  const tableColumns = [
    { key: '#', label: '#' },
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'total_titles_generated', label: 'Total Titles' },
    { key: 'total_short_scripts', label: 'Short Scripts' },
    { key: 'total_medium_scripts', label: 'Medium Scripts' },
    { key: 'total_long_scripts', label: 'Long Scripts' },
  ];

  const tableData = filteredData.map((user, index) => ({
    '#': (currentPage - 1) * pageSize + index + 1,
    name: user.name,
    email: user.email,
    total_titles_generated: user.total_titles_generated,
    total_short_scripts: user.total_short_scripts,
    total_medium_scripts: user.total_medium_scripts,
    total_long_scripts: user.total_long_scripts,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-white">User Report</h2>
        <p className="mt-1 text-sm text-gray-400">
          View user activity report with titles and scripts generated statistics
        </p>
      </div>

      {/* Search and Filters Row */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        {/* Search Field */}
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name, email, or script counts..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1); // Reset to first page when searching
              }}
              className="w-full rounded-xl border border-transparent bg-[#2d2d2d] px-4 py-3 pl-10 text-white placeholder-[#aaaca6] outline-none focus:border-green-500"
            />
          </div>
        </div>

        {/* Date Range Filters - Right Side */}
        <div className="flex flex-col gap-4 sm:flex-row lg:items-end">
          <div className="w-full sm:w-48">
            <TextField type="date" label="Start Date" value={startDate} onChange={setStartDate} />
          </div>
          <div className="w-full sm:w-48">
            <TextField type="date" label="End Date" value={endDate} onChange={setEndDate} />
          </div>
          <div className="flex gap-2 sm:w-auto">
            <button
              onClick={() => {
                setStartDate('');
                setEndDate('');
              }}
              className="whitespace-nowrap rounded-xl border border-gray-600 bg-[#2d2d2d] px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-[#3d3d3d]"
            >
              Clear
            </button>
            <button
              onClick={handleExport}
              disabled={exporting || loading || totalCount === 0}
              className="flex items-center gap-2 whitespace-nowrap rounded-xl border border-green-500/50 bg-green-500/10 px-4 py-3 text-sm font-medium text-green-400 transition-colors hover:bg-green-500/20 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Download className="h-4 w-4" />
              {exporting ? 'Exporting...' : 'Export'}
            </button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-400">Loading data...</div>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
          <p className="text-red-400">Error: {error}</p>
        </div>
      )}

      {/* Table */}
      {!loading && !error && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-400">
              Showing {filteredData.length} of {totalCount} user
              {totalCount !== 1 ? 's' : ''}
              {searchTerm && ` (filtered from ${data.length} on this page)`}
            </p>
          </div>
          {data.length > 0 || totalCount > 0 ? (
            <>
              <CustomTable columns={tableColumns} data={tableData} />
              {totalCount > pageSize && (
                <div className="mt-4">
                  <Pagination
                    currentPage={currentPage}
                    totalCount={totalCount}
                    pageSize={pageSize}
                    onPageChange={setCurrentPage}
                  />
                </div>
              )}
            </>
          ) : (
            <div className="rounded-lg border border-[#BAFF3812] bg-brand-surface p-12 text-center">
              <p className="text-gray-400">
                {searchTerm
                  ? 'No users found matching your search criteria on this page.'
                  : 'No users found for the selected date range.'}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
