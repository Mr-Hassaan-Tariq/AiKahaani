'use client';

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

import { getClientDataAction } from 'lib/utils/clientDataActions';

type Point = { label: string; value: number };

/* -------------------- Date helpers -------------------- */
function toDate(dateStr: string) {
  const d = new Date(dateStr);
  if (!isNaN(d.getTime())) return d;
  return new Date(dateStr + 'T00:00:00');
}
function toISODate(d: Date) {
  return d.toISOString().slice(0, 10);
}
function toISOMonth(d: Date) {
  return d.toISOString().slice(0, 7);
}
function weekStartISO(d: Date) {
  const dd = new Date(d);
  const day = dd.getDay();
  const diffToMonday = (day + 6) % 7;
  dd.setDate(dd.getDate() - diffToMonday);
  return toISODate(dd);
}
function formatLabelForPeriodKey(key: string, period: string) {
  try {
    if (period === 'day') return toDate(key).toLocaleDateString(undefined, { weekday: 'short' });
    if (period === 'week')
      return toDate(key).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    if (period === 'month')
      return toDate(key + '-01').toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
    if (period === 'year') return key;
    return key;
  } catch {
    return key;
  }
}

/* -------------------- Bucket generators -------------------- */
function lastNDays(n: number): string[] {
  const days: string[] = [];
  const today = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    days.push(toISODate(d));
  }
  return days;
}
function lastNWeeks(n: number): string[] {
  const weeks: string[] = [];
  const today = new Date();
  const startOfThisWeek = toDate(weekStartISO(today));
  for (let i = n - 1; i >= 0; i--) {
    const w = new Date(startOfThisWeek);
    w.setDate(startOfThisWeek.getDate() - i * 7);
    weeks.push(weekStartISO(w));
  }
  return weeks;
}
function lastNMonths(n: number): string[] {
  const months: string[] = [];
  const today = new Date();
  const y = today.getFullYear();
  const m = today.getMonth();
  for (let i = n - 1; i >= 0; i--) {
    const mm = new Date(y, m - i, 1);
    months.push(toISOMonth(mm));
  }
  return months;
}
function lastNYears(n: number): string[] {
  const years: string[] = [];
  const y = new Date().getFullYear();
  for (let i = n - 1; i >= 0; i--) years.push(String(y - i));
  return years;
}

/* -------------------- Tooltip -------------------- */
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload?.length) {
    return (
      <div className="rounded-md border border-gray-700 bg-[#0f1720] p-2 text-white shadow-md">
        <p className="text-sm text-gray-300">{label}</p>
        <p className="text-sm font-semibold">Active Users: {payload[0].value}</p>
      </div>
    );
  }
  return null;
};

/* -------------------- Chart -------------------- */
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
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="value" stroke="none" fill="url(#colorUv)" />
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

/* -------------------- Dashboard -------------------- */
export default function Dashboard() {
  const [period, setPeriod] = useState<'day' | 'week' | 'month' | 'year'>('day');
  const [duration, setDuration] = useState<number>(7);
  const [data, setData] = useState<Point[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const durationOptions = useMemo(() => {
    switch (period) {
      case 'day':
        return [1, 3, 7, 14, 30];
      case 'week':
        return [1, 2, 4, 8, 12];
      case 'month':
        return [1, 3, 6, 12, 24];
      case 'year':
        return [1, 2, 3, 5, 10];
      default:
        return [7];
    }
  }, [period]);

  useEffect(() => {
    if (!durationOptions.includes(duration)) setDuration(durationOptions[0]);
  }, [period, durationOptions, duration]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ period, duration: String(duration) });
      const response = await getClientDataAction<any>(`v1/admin/login-stats/?${params.toString()}`);
      let payload = response?.data?.data || response?.data || response;

      let buckets: string[] = [];
      if (period === 'day') buckets = lastNDays(duration);
      else if (period === 'week') buckets = lastNWeeks(duration);
      else if (period === 'month') buckets = lastNMonths(duration);
      else buckets = lastNYears(duration);

      const lookup = new Map<string, number>();
      if (Array.isArray(payload?.data)) payload = payload.data;
      if (Array.isArray(payload)) {
        for (const item of payload) {
          const rawDate = String(item.date ?? item.timestamp ?? '');
          if (!rawDate) continue;
          const d = toDate(rawDate);
          if (isNaN(d.getTime())) continue;
          const key =
            period === 'day'
              ? toISODate(d)
              : period === 'week'
                ? weekStartISO(d)
                : period === 'month'
                  ? toISOMonth(d)
                  : String(d.getFullYear());
          lookup.set(key, (lookup.get(key) ?? 0) + (Number(item.count ?? item.value ?? 0) || 0));
        }
      }

      const mapped = buckets.map((bk) => ({
        label: formatLabelForPeriodKey(bk, period),
        value: lookup.get(bk) ?? 0,
      }));
      setData(mapped);
    } catch (err: any) {
      setError(err?.message || 'Failed to load data');
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [period, duration]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const subtitle = useMemo(
    () => `Last ${duration} ${period}${duration > 1 ? 's' : ''}`,
    [period, duration],
  );

  return (
    <div className="rounded-lg bg-transparent p-5 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between">
        <div>
          <h2 className="text-lg font-medium text-white">Active Users statistics</h2>
          <div className="text-sm text-white">{subtitle}</div>
        </div>

        {/* Filters on right side */}
        <div className="flex items-end gap-3">
          <div>
            <label className="mb-1 block text-sm text-white">Period</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as any)}
              className="h-10 w-40 appearance-none rounded-xl border border-gray-700 bg-[#1f1f1f] px-4 py-2 text-white shadow-sm"
            >
              <option value="day">Day</option>
              <option value="week">Week</option>
              <option value="month">Month</option>
              <option value="year">Year</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm text-white">Duration</label>
            <select
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="h-10 w-28 appearance-none rounded-xl border border-gray-700 bg-[#1f1f1f] px-4 py-2 text-white shadow-sm"
            >
              {durationOptions.map((opt) => (
                <option key={opt} value={opt}>
                  {opt}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Chart */}
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
  );
}
