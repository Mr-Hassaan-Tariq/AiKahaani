'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Bell, Sparkles, X } from 'lucide-react';

import { formatTimeAgo } from 'lib/utils';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from 'components/shadcn_ui/dropdown-menu';

export function Dropdown({ notifications }: { notifications: any[] }) {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  const getFinalURL = (link?: string) => {
    if (!link) return '#';
    if (link.startsWith('/scripts/')) return `/new-script/script/${link.replace('scripts/', '')}`;
    if (link.startsWith('/outlines/')) return `/new-script/${link.replace('/outlines/', '')}`;
    return link;
  };

  const handleNotificationClick = (extraData: Record<string, any>) => {
    const metaValue = extraData?.script || extraData?.outline;
    if (metaValue?.link) {
      router.push(getFinalURL(metaValue.link));
      setOpen(false);
    }
  };

  const items: any[] = Array.isArray(notifications) ? notifications : [];
  const hasItems = items.length > 0;

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <button
          aria-label="Notifications"
          className="relative flex h-9 w-9 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <Bell className="h-4 w-4" />
          {hasItems && (
            <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary" />
          )}
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        className="w-[340px] rounded-xl border border-border bg-card p-4 shadow-md"
      >
        {/* Header */}
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">Notifications</h2>
          <button
            onClick={() => setOpen(false)}
            className="rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Items */}
        {hasItems ? (
          <div className="flex flex-col gap-1">
            {items.map((item: any, index: number) => {
              const showTime =
                index === 0 ||
                formatTimeAgo(items[index - 1]?.created_at) !== formatTimeAgo(item?.created_at);

              return (
                <div key={item?.id}>
                  {showTime && (
                    <p className="mb-1 mt-2 px-2 text-xs text-muted-foreground first:mt-0">
                      {formatTimeAgo(item?.created_at)}
                    </p>
                  )}
                  <button
                    className="flex w-full items-start gap-3 rounded-lg px-2 py-2 text-left transition-colors hover:bg-muted"
                    onClick={() => handleNotificationClick(item?.extra_data)}
                  >
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent">
                      <Sparkles className="h-3.5 w-3.5 text-accent-foreground" />
                    </div>
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-foreground">{item.title}</p>
                      <p className="mt-0.5 truncate text-xs text-muted-foreground">
                        {item?.message?.slice(0, 60)}
                        {item?.message?.length > 60 && '…'}
                      </p>
                    </div>
                  </button>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="py-6 text-center">
            <Bell className="mx-auto mb-2 h-6 w-6 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">No notifications yet</p>
          </div>
        )}

        {/* Footer */}
        <div className="mt-3 border-t border-border pt-3 text-center">
          <button
            className="text-xs font-medium text-primary hover:underline"
            onClick={() => {
              router.push('/notifications');
              setOpen(false);
            }}
          >
            View all notifications
          </button>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
