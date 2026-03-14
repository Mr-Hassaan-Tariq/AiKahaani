'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useSearchParams } from 'next/navigation';
import { CheckCheck } from 'lucide-react';
import { toast } from 'sonner';

import { postClientDataAction } from 'lib/utils/clientDataActions';
import { Button } from 'components/ui/Button';
import Topbar from 'components/layout/Topbar';
import { cn } from 'lib/utils';

const tabsPath = [
  { label: 'All',             path: '/notifications' },
  { label: 'Product Updates', path: '/notifications?query=product-updates' },
  { label: 'Subscription',    path: '/notifications?query=subscription' },
] as const;

export default function NotificationTabs({ children }: { children: React.ReactNode }) {
  const pathname    = usePathname();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);

  const query     = searchParams.get('query');
  const activeTab = tabsPath.find((tab) => tab.path === pathname + '?query=' + query) ?? tabsPath[0];

  const handleMarkAllRead = async () => {
    try {
      setLoading(true);
      await postClientDataAction('v1/notifications/read-all/');
      toast.success('All notifications marked as read');
    } catch {
      toast.error('Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col">
      <Topbar
        title="Notifications"
        actions={
          <Button variant="outline" size="sm" onClick={handleMarkAllRead} loading={loading} disabled={loading}>
            <CheckCheck className="h-4 w-4" />
            Mark all read
          </Button>
        }
      />

      {/* ── Tab bar ── */}
      <div className="border-b border-border bg-background px-7">
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
      <div className="p-7">
        <div className="mx-auto max-w-2xl">
          {children}
        </div>
      </div>
    </div>
  );
}
