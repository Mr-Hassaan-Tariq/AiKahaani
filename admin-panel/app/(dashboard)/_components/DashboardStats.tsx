'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { CheckCircle, FileText, FolderOpen, RefreshCw, Users } from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import StatCard from './StatCard';
import { getDashboardStatistics } from 'lib/utils/clientDataActions';
import { Skeleton } from 'components/shadcn_ui/skeleton';

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

      if (!response) throw new Error('No response from API');
      setStats(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load stats';
      setError(errorMessage);
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

  // Chart data for subscription plans pie chart
  const subscriptionPlanData = useMemo(() => {
    if (!stats) return [];
    return [
      {
        name: 'Free Trial',
        value: stats.active_subscribers_by_plan['Free Trial'] || 0,
        color: '#20BF0E',
      },
      {
        name: 'Basic Plan',
        value: stats.active_subscribers_by_plan['Basic Plan'] || 0,
        color: '#2BFF13',
      },
      {
        name: 'Pro Plan',
        value: stats.active_subscribers_by_plan['Pro Plan'] || 0,
        color: '#16a34a',
      },
    ].filter((item) => item.value > 0);
  }, [stats]);

  // Chart data for active vs total users donut chart
  const userDistributionData = useMemo(() => {
    if (!stats) return [];
    const activeUsers = activeSubscribersTotal;
    const inactiveUsers = Math.max(0, stats.total_users - activeUsers);
    return [
      {
        name: 'Active Subscribers',
        value: activeUsers,
        color: '#20BF0E',
      },
      {
        name: 'Inactive Users',
        value: inactiveUsers,
        color: '#2b2b2b',
      },
    ].filter((item) => item.value > 0);
  }, [stats, activeSubscribersTotal]);

  // Chart data for Script Generator vs Title Generator comparison
  const generatorComparisonData = useMemo(() => {
    if (!stats) return [];
    return [
      {
        name: 'Script Generator',
        value: stats.feature_usage.script_generator || 0,
      },
      {
        name: 'Title Generator',
        value: stats.feature_usage.title_generator || 0,
      },
    ];
  }, [stats]);

  // Custom tooltip for pie chart
  const CustomPieTooltip = ({
    active,
    payload,
  }: {
    active?: boolean;
    payload?: Array<{ name: string; value: number }>;
  }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const total = subscriptionPlanData.reduce((sum, item) => sum + item.value, 0);
      const percentage = total > 0 ? ((data.value / total) * 100).toFixed(1) : '0';
      return (
        <div className="rounded-md border border-[#2b2b2b] bg-[#161616] p-3 text-white shadow-lg">
          <p className="text-sm font-semibold text-[#20BF0E]">{data.name}</p>
          <p className="text-sm text-white">Subscribers: {data.value.toLocaleString()}</p>
          <p className="text-xs text-[#AAACA6]">{percentage}% of total</p>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for donut chart
  const CustomDonutTooltip = ({
    active,
    payload,
  }: {
    active?: boolean;
    payload?: Array<{ name: string; value: number }>;
  }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const total = stats?.total_users || 0;
      const percentage = total > 0 ? ((data.value / total) * 100).toFixed(1) : '0';
      return (
        <div className="rounded-md border border-[#2b2b2b] bg-[#161616] p-3 text-white shadow-lg">
          <p className="text-sm font-semibold text-[#20BF0E]">{data.name}</p>
          <p className="text-sm text-white">Users: {data.value.toLocaleString()}</p>
          <p className="text-xs text-[#AAACA6]">{percentage}% of total</p>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for bar chart
  const CustomBarTooltip = ({
    active,
    payload,
  }: {
    active?: boolean;
    payload?: Array<{ payload: { name: string }; value: number }>;
  }) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-md border border-[#2b2b2b] bg-[#161616] p-3 text-white shadow-lg">
          <p className="text-sm font-semibold text-[#20BF0E]">{payload[0].payload.name}</p>
          <p className="text-sm text-white">Total Uses: {payload[0].value.toLocaleString()}</p>
        </div>
      );
    }
    return null;
  };

  // Skeleton component for stat cards
  const StatCardSkeleton = () => (
    <div className="rounded-2xl border border-[#2b2b2b] bg-[#161616] p-5 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-1 flex-col">
          <Skeleton className="mb-3 h-4 w-24 bg-[#2a2a2a]" />
          <Skeleton className="h-8 w-20 bg-[#2a2a2a]" />
        </div>
        <Skeleton className="h-11 w-11 rounded-lg bg-[#2a2a2a]" />
      </div>
      <Skeleton className="mt-3 h-4 w-32 bg-[#2a2a2a]" />
    </div>
  );

  // Skeleton component for bar chart
  const BarChartSkeleton = () => (
    <div className="rounded-2xl border border-[#2b2b2b] bg-[#161616] p-6 shadow-sm">
      <Skeleton className="mb-4 h-6 w-64 bg-[#2a2a2a]" />
      <Skeleton className="h-[300px] w-full rounded-lg bg-[#2a2a2a]" />
    </div>
  );

  // Skeleton component for niche vault
  const NicheVaultSkeleton = () => (
    <div className="rounded-2xl border border-[#2b2b2b] bg-[#161616] p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <Skeleton className="mb-2 h-6 w-32 bg-[#2a2a2a]" />
          <Skeleton className="h-4 w-64 bg-[#2a2a2a]" />
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-[#1E1E1E] px-4 py-3">
          <Skeleton className="h-5 w-5 rounded bg-[#2a2a2a]" />
          <div>
            <Skeleton className="mb-1 h-7 w-16 bg-[#2a2a2a]" />
            <Skeleton className="h-3 w-20 bg-[#2a2a2a]" />
          </div>
        </div>
      </div>
    </div>
  );

  // Compact chart skeleton for grid layout
  const CompactChartSkeleton = () => (
    <div className="rounded-2xl border border-[#2b2b2b] bg-[#161616] p-4 shadow-sm">
      <Skeleton className="mb-3 h-5 w-40 bg-[#2a2a2a]" />
      <Skeleton className="h-[220px] w-full rounded-lg bg-[#2a2a2a]" />
    </div>
  );

  if (loading && !stats) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-6 w-24 bg-[#2a2a2a]" />
          <Skeleton className="h-8 w-24 rounded-md bg-[#2a2a2a]" />
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <CompactChartSkeleton />
          <CompactChartSkeleton />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <BarChartSkeleton />
          </div>
          <NicheVaultSkeleton />
        </div>
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
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-white">Dashboard Overview</h3>
        <button
          onClick={fetchStats}
          disabled={loading}
          className="flex items-center gap-2 rounded-md border border-[#20BF0E]/40 px-3 py-1.5 text-sm text-[#20BF0E] transition hover:bg-[#20BF0E]/10 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Stat Cards Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {loading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <StatCardSkeleton key={i} />
            ))}
          </>
        ) : (
          <>
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
          </>
        )}
      </div>

      {/* Charts Row - Side by Side */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* User Distribution Donut Chart */}
        {loading ? (
          <CompactChartSkeleton />
        ) : (
          stats.total_users > 0 && (
            <div className="rounded-2xl border border-[#2b2b2b] bg-[#161616] p-4 shadow-sm">
              <h3 className="mb-3 text-base font-semibold text-white">User Distribution</h3>
              <div className="flex flex-col items-center gap-4 lg:flex-row">
                <div className="w-full lg:w-1/2">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={userDistributionData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        innerRadius={50}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {userDistributionData.map((entry) => (
                          <Cell key={`cell-${entry.name}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip content={<CustomDonutTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex w-full flex-col gap-2 lg:w-1/2">
                  {userDistributionData.map((item) => {
                    const percentage =
                      stats.total_users > 0
                        ? ((item.value / stats.total_users) * 100).toFixed(1)
                        : '0';
                    return (
                      <div
                        key={item.name}
                        className="flex items-center justify-between rounded-lg bg-[#1E1E1E] p-3"
                      >
                        <div className="flex items-center gap-2">
                          <div
                            className="h-3 w-3 rounded-full"
                            style={{ backgroundColor: item.color }}
                          />
                          <span className="text-xs font-medium text-white">{item.name}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-white">
                            {item.value.toLocaleString()}
                          </div>
                          <div className="text-xs text-[#AAACA6]">{percentage}%</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )
        )}

        {/* Subscription Plans Distribution Chart */}
        {loading ? (
          <CompactChartSkeleton />
        ) : (
          activeSubscribersTotal > 0 && (
            <div className="rounded-2xl border border-[#2b2b2b] bg-[#161616] p-4 shadow-sm">
              <h3 className="mb-3 text-base font-semibold text-white">
                Subscription Plans Distribution
              </h3>
              <div className="flex flex-col items-center gap-4 lg:flex-row">
                <div className="w-full lg:w-1/2">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={subscriptionPlanData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {subscriptionPlanData.map((entry) => (
                          <Cell key={`cell-${entry.name}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip content={<CustomPieTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex w-full flex-col gap-2 lg:w-1/2">
                  {subscriptionPlanData.map((item) => {
                    const percentage =
                      activeSubscribersTotal > 0
                        ? ((item.value / activeSubscribersTotal) * 100).toFixed(1)
                        : '0';
                    return (
                      <div
                        key={item.name}
                        className="flex items-center justify-between rounded-lg bg-[#1E1E1E] p-3"
                      >
                        <div className="flex items-center gap-2">
                          <div
                            className="h-3 w-3 rounded-full"
                            style={{ backgroundColor: item.color }}
                          />
                          <span className="text-xs font-medium text-white">{item.name}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-white">
                            {item.value.toLocaleString()}
                          </div>
                          <div className="text-xs text-[#AAACA6]">{percentage}%</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )
        )}
      </div>

      {/* Bottom Row - Bar Chart and Niche Vault */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Generator Comparison Bar Chart */}
        {loading ? (
          <div className="lg:col-span-2">
            <BarChartSkeleton />
          </div>
        ) : (
          <div className="rounded-2xl border border-[#2b2b2b] bg-[#161616] p-4 shadow-sm lg:col-span-2">
            <h3 className="mb-3 text-base font-semibold text-white">
              Script vs Title Generator Usage
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart
                data={generatorComparisonData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <defs>
                  <linearGradient id="colorBar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#20BF0E" stopOpacity={0.8} />
                    <stop offset="100%" stopColor="#2BFF13" stopOpacity={0.4} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2b2b2b" />
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#AAACA6', fontSize: 12 }}
                  axisLine={{ stroke: '#2b2b2b' }}
                  tickLine={{ stroke: '#2b2b2b' }}
                />
                <YAxis
                  tick={{ fill: '#AAACA6', fontSize: 12 }}
                  axisLine={{ stroke: '#2b2b2b' }}
                  tickLine={{ stroke: '#2b2b2b' }}
                />
                <Tooltip content={<CustomBarTooltip />} />
                <Bar dataKey="value" fill="url(#colorBar)" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Niche Vault Section */}
        {loading ? (
          <NicheVaultSkeleton />
        ) : (
          <div className="rounded-2xl border border-[#2b2b2b] bg-[#161616] p-4 shadow-sm">
            <div className="flex h-full flex-col justify-between">
              <div>
                <h3 className="mb-1 text-base font-semibold text-white">Niche Vault</h3>
                <p className="mb-4 text-xs text-[#AAACA6]">Templates used for script generation</p>
              </div>
              <div className="flex items-center gap-3 rounded-lg bg-[#1E1E1E] px-4 py-4">
                <FolderOpen className="h-6 w-6 text-[#20BF0E]" />
                <div>
                  <div className="text-2xl font-bold text-white">
                    {stats.feature_usage.niche_vault.toLocaleString()}
                  </div>
                  <div className="text-xs text-[#AAACA6]">Template uses</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
