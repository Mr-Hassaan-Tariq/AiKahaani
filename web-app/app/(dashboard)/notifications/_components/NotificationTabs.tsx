'use client';

import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';

import { cn } from 'lib/utils';

const tabsPath = [
  { label: 'All', path: '/notifications' },
  { label: 'Product Updates', path: '/notifications?query=product-updates' },
  { label: 'Subscription', path: '/notifications?query=subscription' },
] as const;

export default function NotificationTabs({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const query = searchParams.get('query');
  const activeTab =
    tabsPath.find((tab) => tab.path === pathname + '?query=' + query) ?? tabsPath[0];

  return (
    <div className="flex flex-col">
      {/* ── Tab bar ── */}
      <div className="border-b border-border bg-background px-4 sm:px-7">
        <nav className="-mb-px flex gap-0 overflow-x-auto">
          {tabsPath.map((tab) => {
            const isActive = activeTab.label === tab.label;
            return (
              <Link
                key={tab.label}
                href={tab.path}
                className={cn(
                  'whitespace-nowrap border-b-2 px-4 py-3 text-sm font-medium transition-colors',
                  isActive
                    ? 'border-primary text-foreground'
                    : 'border-transparent text-muted-foreground hover:text-foreground',
                )}
              >
                {tab.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* ── Content ── */}
      <div className="p-4 sm:p-7">
        <div className="mx-auto max-w-2xl">{children}</div>
      </div>
    </div>
  );
}
