'use client';

import { useCallback, useEffect, useState } from 'react';
import { CheckCircle, RefreshCw, Shield, UserPlus, Users } from 'lucide-react';

import StatCard from './StatCard';
import { getClientDataAction } from 'lib/utils/clientDataActions';

type StatsData = {
  total_users: number;
  active_users: number;
  inactive_users: number;
  verified_users: number;
  admin_count: number;
  user_count: number;
  recent_signups: number;
};

type StatsResponse = {
  data: StatsData;
  message?: string;
};

export default function DashboardStats() {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await getClientDataAction<StatsResponse>('v1/admin/user-stats/');
      if (!res) throw new Error('No response from API');

      setStats(res.data);
    } catch (err: any) {
      console.error('Error fetching user stats:', err);
      setError(err.message || 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  if (loading && !stats) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="animate-pulse rounded-xl bg-[#1b1b1b] p-5">
            <div className="mb-4 h-6 w-32 rounded bg-[#2a2a2a]" />
            <div className="h-8 w-full rounded bg-[#2a2a2a]" />
          </div>
        ))}
      </div>
    );
  }

  if (error && !stats) {
    return <div className="text-red-400">Error loading stats: {error}</div>;
  }

  if (!stats) {
    return <div className="text-[#AAACA6]">No statistics available.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Overview</h3>
        <button
          onClick={fetchStats}
          disabled={loading}
          className="flex items-center gap-2 rounded-md border border-[#20BF0E]/40 px-3 py-1 text-sm text-[#20BF0E] transition hover:bg-[#20BF0E]/10"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Users"
          value={stats.total_users}
          icon={<Users />}
          subtitle={`${stats.recent_signups} new`}
        />
        <StatCard
          title="Active Users"
          value={stats.active_users}
          icon={<CheckCircle />}
          subtitle={`${stats.verified_users} verified`}
        />
        <StatCard
          title="Admins"
          value={stats.admin_count}
          icon={<Shield />}
          subtitle={`${stats.user_count} users`}
        />
        <StatCard
          title="Inactive Users"
          value={stats.inactive_users}
          icon={<UserPlus />}
          subtitle={`${stats.recent_signups} recent signups`}
        />
      </div>
    </div>
  );
}
