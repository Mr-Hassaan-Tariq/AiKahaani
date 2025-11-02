'use client';

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

function Chart({ data }: { data: Point[] }) {
  return (
    <div className="w-full font-sans">
      <ResponsiveContainer width="100%" height={240}>
        <ReLineChart data={data} margin={{ top: 12, right: 12, left: 12, bottom: 12 }}>
          <defs>
            <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6366f1" stopOpacity={0.18} />
              <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>

          <XAxis dataKey="label" axisLine={false} tickLine={false} />
          <YAxis axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ background: '#111827', border: 'none', color: '#fff' }}
            itemStyle={{ color: '#fff' }}
            labelStyle={{ color: '#9ca3af' }}
          />

          <Area
            type="monotone"
            dataKey="value"
            stroke="none"
            fillOpacity={1}
            fill="url(#colorUv)"
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="green"
            strokeWidth={3}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        </ReLineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function Dashboard() {
  // dummy data
  const data: Point[] = [
    { label: 'Mon', value: 12 },
    { label: 'Tue', value: 25 },
    { label: 'Wed', value: 15 },
    { label: 'Thu', value: 30 },
    { label: 'Fri', value: 22 },
    { label: 'Sat', value: 35 },
    { label: 'Sun', value: 28 },
  ];

  return (
    <div className="rounded-lg bg-transparent p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-medium text-white">Active Users statistics</h2>
        <div className="text-sm text-white">Last 7 days</div>
      </div>
      <Chart data={data} />
    </div>
  );
}
