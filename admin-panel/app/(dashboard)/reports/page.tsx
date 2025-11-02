'use client';

import { useState } from 'react';

import Dashboard from './_components/Dashboard';
import UserConversions from './_components/UserConversions';
import UserReport from './_components/UserReport';

export default function Page() {
  const tabs = [
    { key: 'users', label: 'User Report' },
    { key: 'conversions', label: 'User Conversions' },
  ];

  const [active, setActive] = useState<string>('users');
  // track which tabs have been mounted (visited) to avoid remounting
  const [mounted, setMounted] = useState<Record<string, boolean>>({ users: true });

  return (
    <div>
      <Dashboard />
      {/* Tabs header */}
      <div className="mt-6 flex items-center justify-start gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => {
              setActive(tab.key);
              setMounted((s) => ({ ...s, [tab.key]: true }));
            }}
            className={`rounded-xl px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-green-500/40 ${active === tab.key ? 'border border-green-500/30 bg-green-500/10 text-green-300' : 'border border-transparent bg-[#2d2d2d] text-gray-300'}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Active panel */}
      <div className="mt-6">
        {/* Lazy-mount panels and keep them mounted to avoid repeated API calls on toggle */}
        {mounted.users && (
          <div className={active === 'users' ? 'block' : 'hidden'}>
            <UserReport />
          </div>
        )}
        {mounted.conversions && (
          <div className={active === 'conversions' ? 'block' : 'hidden'}>
            <UserConversions />
          </div>
        )}
      </div>
    </div>
  );
}
