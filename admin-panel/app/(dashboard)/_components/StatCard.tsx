import React from 'react';

type Props = {
  title: string;
  value: number | string;
  icon?: React.ReactNode;
  subtitle?: string;
};

export default function StatCard({ title, value, icon, subtitle }: Props) {
  return (
    <div className="rounded-2xl border border-[#2b2b2b] bg-[#161616] p-5 shadow-sm transition-colors hover:border-[#20BF0E]/40">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col">
          <span className="text-sm text-[#AAACA6]">{title}</span>
          <span className="mt-1 text-3xl font-semibold text-white">{value}</span>
        </div>

        <div className="ml-2 flex h-11 w-11 items-center justify-center rounded-lg bg-[#1E1E1E] group-hover:bg-[#20BF0E]/10">
          <div className="text-[#20BF0E]">{icon}</div>
        </div>
      </div>

      {subtitle && <div className="mt-3 text-sm font-medium text-[#20BF0E]/80">{subtitle}</div>}
    </div>
  );
}
