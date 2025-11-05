'use client';

import { getClientDataAction } from 'lib/utils/clientDataActions';
import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Area,
  Line,
  LineChart as ReLineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

type Point = { label: string; value: number };

function formatLabelFromDate(dateStr: string, period: string) {
  try {
    const d = new Date(dateStr);
    if (Number.isNaN(d.getTime())) return dateStr;
    if (period === 'day') return d.toLocaleDateString(undefined, { weekday: 'short' });
    if (period === 'week')
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    if (period === 'month')
      return d.toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
    return d.toLocaleDateString();
  } catch {
    return dateStr;
  }
}

function lastNDays(n: number): string[] {
  const days: string[] = [];
  const today = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    days.push(d.toISOString().slice(0, 10));
  }
  return days;
}

function formatLabelForPeriod(dateIso: string, period: string) {
  if (period === 'day') {
    const d = new Date(dateIso);
    return d.toLocaleDateString(undefined, { weekday: 'short' });
  }
  return formatLabelFromDate(dateIso, period);
}

function Chart({ data }: { data: Point[] }) {
  return (
    <div className="w-full font-sans">
      <ResponsiveContainer width="100%" height={320}>
        <ReLineChart data={data} margin={{ top: 12, right: 12, left: 12, bottom: 12 }}>
          <defs>
            <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#064e3b" stopOpacity={0.16} />
              <stop offset="100%" stopColor="#064e3b" stopOpacity={0} />
            </linearGradient>
          </defs>

          <XAxis dataKey="label" axisLine={false} tickLine={false} />
          <YAxis axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ background: '#0f1720', border: 'none', color: '#fff' }}
            itemStyle={{ color: '#fff' }}
            labelStyle={{ color: '#9ca3af' }}
          />

          <Area type="monotone" dataKey="value" stroke="none" fillOpacity={1} fill="url(#colorUv)" />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#16a34a"
            strokeWidth={3}
            dot={{ r: 4, stroke: '#071011', strokeWidth: 2 }}
            activeDot={{ r: 6 }}
          />
        </ReLineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function Dashboard() {
  const [period, setPeriod] = useState<'day' | 'week' | 'month' | 'year'>('day');
  const [duration, setDuration] = useState<number>(7);

  const [data, setData] = useState<Point[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('period', period);
      params.append('duration', String(duration));

      const endpoint = `v1/admin/login-stats/?${params.toString()}`;
      const response = await getClientDataAction<any>(endpoint);
      const payload = response?.data ?? response;

      let mapped: Point[] = [];

      if (payload && typeof payload === 'object' && Array.isArray(payload.data)) {
        const apiData = payload.data as Array<{ date?: string; count?: number;[k: string]: any }>;

        if (period === 'day') {
          const buckets = lastNDays(duration);
          const lookup = new Map<string, number>();
          for (const item of apiData) {
            const dateIso = String(item.date ?? item.timestamp ?? '').slice(0, 10);
            if (!dateIso) continue;
            lookup.set(dateIso, Number(item.count ?? item.value ?? item.total ?? 0));
          }

          mapped = buckets.map((dateIso) => ({
            label: formatLabelForPeriod(dateIso, period),
            value: Number(lookup.get(dateIso) ?? 0),
          }));
        } else {
          mapped = apiData.map((it) => ({
            label: formatLabelFromDate(String(it.date ?? it.timestamp ?? ''), period),
            value: Number(it.count ?? it.value ?? it.total ?? 0) || 0,
          }));
        }
      }
      else if (Array.isArray(payload)) {
        mapped = payload.map((item: any) => {
          if (typeof item.label === 'string' && typeof item.value === 'number') {
            return { label: item.label, value: item.value };
          }
          if (
            (item.date || item.timestamp || item.ts) &&
            (item.count ?? item.value ?? item.total) !== undefined
          ) {
            const rawDate = item.date ?? item.timestamp ?? item.ts;
            const rawValue = item.count ?? item.value ?? item.total;
            return {
              label: formatLabelFromDate(String(rawDate), period),
              value: Number(rawValue) || 0,
            };
          }
          if (item.x !== undefined && item.y !== undefined) {
            const label =
              typeof item.x === 'string' ? formatLabelFromDate(item.x, period) : String(item.x);
            return { label, value: Number(item.y) || 0 };
          }

          const keys = Object.keys(item || {});
          const labelKey = keys.find((k) => typeof item[k] === 'string') ?? keys[0] ?? '';
          const valueKey =
            keys.find((k) => typeof item[k] === 'number') ||
            keys.find((k) => !isNaN(Number(item[k]))) ||
            keys[1] ||
            keys[0] ||
            '';

          return {
            label: String(item[labelKey as keyof typeof item] ?? ''),
            value: Number(item[valueKey as keyof typeof item] ?? 0),
          };
        });
      }
      else if (payload && typeof payload === 'object') {
        if (Array.isArray(payload.labels) && Array.isArray(payload.values)) {
          mapped = payload.labels.map((lab: any, i: number) => ({
            label: String(lab),
            value: Number(payload.values[i]) || 0,
          }));
        } else {
          mapped = [];
        }
      } else {
        mapped = [];
      }

      const allDateLike = mapped.every((p) => !Number.isNaN(Date.parse(p.label)));
      const sorted = allDateLike
        ? mapped.slice().sort((a, b) => new Date(a.label).getTime() - new Date(b.label).getTime())
        : mapped;

      setData(sorted);
    } catch (err: any) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [period, duration]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Clear filters
  const clearFilters = useCallback(() => {
    setPeriod('day');
    setDuration(7);
  }, []);

  const subtitle = useMemo(
    () => `Last ${duration} ${period}${duration > 1 ? 's' : ''}`,
    [period, duration],
  );

  return (
    <div className="rounded-lg bg-transparent p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-medium text-white">Active Users statistics</h2>
        <div className="text-sm text-white">{subtitle}</div>
      </div>

      {/* FILTER ROW */}
      <div className="mb-4 flex flex-wrap items-center gap-3">
        {/* Period Dropdown */}
        <div>
          <label className="mb-1 block text-sm text-white">Period</label>
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value as any)}
            className="h-10 w-44 appearance-none rounded-xl border border-gray-700 bg-[#1f1f1f] px-4 py-2 text-white shadow-sm"
          >
            <option value="day">Day</option>
            <option value="week">Week</option>
            <option value="month">Month</option>
            <option value="year">Year</option>
          </select>
        </div>

        {/* Duration Input */}
        <div>
          <label className="mb-1 block text-sm text-white">Duration</label>
          <input
            type="number"
            min={1}
            step={1}
            value={duration}
            onChange={(e) => setDuration(Math.max(1, Number(e.target.value) || 1))}
            className="h-10 w-28 rounded-xl border border-gray-700 bg-[#1f1f1f] px-4 py-2 text-white shadow-sm"
          />
        </div>

        {/* Spacer + Clear Button */}
        <div className="flex-1" />
        <button
          onClick={() => {
            clearFilters();
            setTimeout(() => fetchData(), 0);
          }}
          className="h-10 rounded-xl border border-gray-600 bg-[#2b2b2b] px-4 py-2 text-sm text-white"
        >
          Clear
        </button>
      </div>

      {/* Chart */}
      <div>
        {loading ? (
          <div className="py-16 text-center text-gray-300">Loading...</div>
        ) : error ? (
          <div className="py-8 text-center text-red-400">Error: {error}</div>
        ) : data.length === 0 ? (
          <div className="py-8 text-center text-gray-400">No data</div>
        ) : (
          <Chart data={data} />
        )}
      </div>
    </div>
  );
}
