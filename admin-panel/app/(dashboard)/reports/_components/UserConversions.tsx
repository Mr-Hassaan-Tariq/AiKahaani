'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Cookies from 'js-cookie';
import { Download, Search } from 'lucide-react';

import Pagination from '../../_components/Pagination';
import { baseUrl } from 'lib/api';
import { getUserConversionFunnel } from 'lib/utils/clientDataActions';
import CustomTable from 'components/common/CustomTable';
import TextField from 'components/common/TextField';

interface UserConversionData {
  name: string;
  email: string;
  subscription_plan: string;
  subscription_status: string;
  status: string;
  has_subscription: boolean;
}

interface ApiResponse {
  data: UserConversionData[];
  count: number;
  message?: string;
}

export default function UserConversions() {
  const [allData, setAllData] = useState<UserConversionData[]>([]);
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

      const queryString = params.toString();
      const endpoint = queryString
        ? `v1/admin/conversion-funnel/?${queryString}`
        : 'v1/admin/conversion-funnel/';

      const response = await getUserConversionFunnel<ApiResponse>(endpoint);

      if (response && response.data) {
        setAllData(response.data);
        setCurrentPage(1); // Reset to first page when new data is fetched
      } else {
        setAllData([]);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load data';
      setError(errorMessage);
      setAllData([]);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Filter data based on search term
  const filteredData = useMemo(() => {
    if (!searchTerm.trim()) {
      return allData;
    }

    const search = searchTerm.toLowerCase();
    return allData.filter(
      (user) =>
        user.name.toLowerCase().includes(search) ||
        user.email.toLowerCase().includes(search) ||
        user.subscription_plan.toLowerCase().includes(search) ||
        user.subscription_status.toLowerCase().includes(search),
    );
  }, [allData, searchTerm]);

  // Paginate filtered data
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return filteredData.slice(startIndex, endIndex);
  }, [filteredData, currentPage, pageSize]);

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
        ? `${baseUrl}v1/admin/conversion-funnel/export/?${queryString}`
        : `${baseUrl}v1/admin/conversion-funnel/export/`;

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
      let filename = 'user_conversions.csv';
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
    { key: 'subscription_plan', label: 'Subscription Plan' },
    { key: 'subscription_status', label: 'Subscription Status' },
    { key: 'status', label: 'Status' },
  ];

  const tableData = paginatedData.map((user, index) => ({
    '#': (currentPage - 1) * pageSize + index + 1,
    name: user.name,
    email: user.email,
    subscription_plan: user.subscription_plan,
    subscription_status: user.subscription_status,
    status: (
      <span
        className={`rounded-full px-3 py-1 text-xs font-medium ${
          user.status === 'Active' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
        }`}
      >
        {user.status}
      </span>
    ),
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-semibold text-white">User Conversions</h2>
        <p className="mt-1 text-sm text-gray-400">
          View user conversion funnel data with date filtering
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
              placeholder="Search by name, email, plan, or status..."
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
              disabled={exporting || loading || filteredData.length === 0}
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
              Showing {paginatedData.length} of {filteredData.length} user
              {filteredData.length !== 1 ? 's' : ''}
              {searchTerm && ` (filtered from ${allData.length} total)`}
            </p>
          </div>
          {filteredData.length > 0 ? (
            <>
              <CustomTable columns={tableColumns} data={tableData} />
              {filteredData.length > pageSize && (
                <div className="mt-4">
                  <Pagination
                    currentPage={currentPage}
                    totalCount={filteredData.length}
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
                  ? 'No users found matching your search criteria.'
                  : 'No users found for the selected date range.'}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
