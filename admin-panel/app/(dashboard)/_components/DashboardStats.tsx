'use client';

import { useCallback, useEffect, useState } from 'react';
import {
  CheckCircle,
  FileText,
  FolderOpen,
  Hash,
  RefreshCw,
  Shield,
  UserPlus,
  Users,
} from 'lucide-react';

import StatCard from './StatCard';
import { getDashboardStatistics } from 'lib/utils/clientDataActions';

type StatsData = {
  total_users: number;
  new_users_this_week: number;
  active_subscribers_by_plan: {
    'Free Trial': number;
    'Basic Plan': number;
    'Pro Plan': number;
  };
  feature_usage: {
    script_generator: number;
    title_generator: number;
    niche_vault: number;
  };
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
      const response = await getDashboardStatistics<StatsResponse>('v1/admin/admin-stats/');

      if (!response || !response.data) throw new Error('No response from API');
      setStats(response.data);
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
          subtitle={`${stats.new_users_this_week} new this week`}
        />
        <StatCard
          title="Basic Plan"
          value={stats.active_subscribers_by_plan['Basic Plan']}
          icon={<CheckCircle />}
          subtitle="Active subscribers"
        />
        <StatCard
          title="Pro Plan"
          value={stats.active_subscribers_by_plan['Pro Plan']}
          icon={<Shield />}
          subtitle="Active subscribers"
        />
        <StatCard
          title="Free Trial"
          value={stats.active_subscribers_by_plan['Free Trial']}
          icon={<UserPlus />}
          subtitle="Active subscribers"
        />
      </div>

      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white">Feature Usage</h3>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Script Generator"
          value={stats.feature_usage.script_generator}
          icon={<FileText />}
          subtitle="Total uses"
        />
        <StatCard
          title="Title Generator"
          value={stats.feature_usage.title_generator}
          icon={<Hash />}
          subtitle="Total uses"
        />
        <StatCard
          title="Niche Vault"
          value={stats.feature_usage.niche_vault}
          icon={<FolderOpen />}
          subtitle="Total uses"
        />
      </div>
    </div>
  );
}
