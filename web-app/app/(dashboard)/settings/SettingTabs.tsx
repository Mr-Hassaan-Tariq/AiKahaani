import { headers } from 'next/headers';
import Link from 'next/link';

import { cn } from 'lib/utils';

const tabsPath = [
  { label: 'Profile', path: '/settings/profile' },
  { label: 'Notifications', path: '/settings/notifications' },
  { label: 'Privacy & Security', path: '/settings/privacy-security' },
] as const;

export default async function SettingTabs({ children }: { children: React.ReactNode }) {
  const headersList = await headers();
  const pathname = headersList.get('current_page');
  const activeTab = tabsPath.find((tab) => pathname?.includes(tab.path));

  return (
    <div className="flex min-h-full flex-col">
      {/* Tab nav */}
      <div className="border-b border-border bg-background px-8">
        <nav className="-mb-px flex gap-8 overflow-x-auto">
          {tabsPath.map((tab) => {
            const isActive = activeTab?.label === tab.label;
            return (
              <Link
                key={tab.label}
                href={tab.path}
                className={cn(
                  'whitespace-nowrap border-b-2 py-4 text-[15px] font-medium transition-colors',
                  isActive
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground',
                )}
              >
                {tab.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="min-h-full bg-muted/40 px-8 py-8">
        <div className="mx-auto flex w-full max-w-[900px] flex-col gap-6">{children}</div>
      </div>
    </div>
  );
}
