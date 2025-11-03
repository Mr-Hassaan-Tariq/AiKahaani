'use client';

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
import { useCallback, useEffect, useMemo, useState } from 'react';

import { getDashboardStatistics } from 'lib/utils/clientDataActions';
import StatCard from './StatCard';

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

      console.log('response', response)

      if (!response) throw new Error('No response from API');
      setStats(response);
    } catch (err: any) {
      console.error('Error fetching user stats:', err);
      setError(err?.message || 'Failed to load stats');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // derived values
  const activeSubscribersTotal = useMemo(() => {
    if (!stats) return 0;
    const { active_subscribers_by_plan } = stats;
    return (
      (active_subscribers_by_plan?.['Free Trial'] || 0) +
      (active_subscribers_by_plan?.['Basic Plan'] || 0) +
      (active_subscribers_by_plan?.['Pro Plan'] || 0)
    );
  }, [stats]);

  const planPercent = useCallback(
    (planCount: number) => {
      if (!activeSubscribersTotal) return '0%';
      const pct = (planCount / activeSubscribersTotal) * 100;
      return `${Math.round(pct)}%`;
    },
    [activeSubscribersTotal],
  );

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
          title="Active Subscribers"
          value={activeSubscribersTotal}
          icon={<CheckCircle />}
          subtitle="Sum of all plans"
        />

        {/* Plan breakdowns */}
        <StatCard
          title="Free Trial"
          value={stats.active_subscribers_by_plan['Free Trial']}
          icon={<UserPlus />}
          subtitle={`${planPercent(stats.active_subscribers_by_plan['Free Trial'])} of subscribers`}
        />

        <StatCard
          title="Basic Plan"
          value={stats.active_subscribers_by_plan['Basic Plan']}
          icon={<Hash />}
          subtitle={`${planPercent(stats.active_subscribers_by_plan['Basic Plan'])} of subscribers`}
        />
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Pro Plan"
          value={stats.active_subscribers_by_plan['Pro Plan']}
          icon={<Shield />}
          subtitle={`${planPercent(stats.active_subscribers_by_plan['Pro Plan'])} of subscribers`}
        />

        <div className="hidden lg:block" />

        <div className="hidden lg:block" />
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
          icon={<FileText />}
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
