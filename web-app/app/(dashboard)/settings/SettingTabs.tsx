import { headers } from 'next/headers';
import Link from 'next/link';

import { cn } from 'lib/utils';

const tabsPath = [
  { label: 'Profile', path: '/settings/profile' },
  { label: 'Notifications', path: '/settings/notifications' },
  { label: 'Subscription Plan', path: '/settings/subscription-plan' },
  { label: 'Privacy & Security', path: '/settings/privacy-security' },
] as const;

export default async function SettingTabs({ children }: { children: React.ReactNode }) {
  const headersList = await headers();
  const pathname = headersList.get('current_page');
  const activeTab = tabsPath.find((tab) => pathname?.includes(tab.path));

  return (
    <div className="flex flex-col">
      {/* Settings topbar */}
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-border bg-background px-6">
        <h1 className="text-base font-semibold text-foreground">Settings</h1>
      </header>

      {/* Tab nav */}
      <div className="border-b border-border bg-background px-6">
        <nav className="-mb-px flex gap-1 overflow-x-auto">
          {tabsPath.map((tab) => {
            const isActive = activeTab?.label === tab.label;
            return (
              <Link
                key={tab.label}
                href={tab.path}
                className={cn(
                  'whitespace-nowrap border-b-2 px-3 py-3 text-sm font-medium transition-colors',
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

      <div className="px-6 py-6">{children}</div>
    </div>
  );
}
