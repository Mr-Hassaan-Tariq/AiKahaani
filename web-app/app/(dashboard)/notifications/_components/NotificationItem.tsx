'use client';

import { ArrowRight, Bell } from 'lucide-react';

import { cn } from 'lib/utils';
import { postClientDataAction } from 'lib/utils/clientDataActions';

interface NotificationItemProps {
  id: number;
  title: string;
  description: string;
  time: string;
  actionText?: string;
  actionLink?: string;
  isNew?: boolean;
  icon?: any;
  onRead?: (id: number) => void;
}

export default function NotificationItem({
  id,
  title,
  description,
  time,
  actionText,
  actionLink,
  isNew = false,
  onRead,
}: NotificationItemProps) {
  const handleMarkAsRead = async () => {
    if (!isNew) return;
    try {
      await postClientDataAction(`/v1/notifications/${id}/read`, {});
      onRead?.(id);
    } catch {
      // silently fail
    }
  };

  const getFinalURL = (link?: string) => {
    if (!link) return '#';
    if (link.startsWith('/scripts/')) return `/new-script/script/${link.replace('scripts/', '')}`;
    if (link.startsWith('/outlines/')) return `/new-script/${link.replace('/outlines/', '')}`;
    return link;
  };

  const finalActionLink = getFinalURL(actionLink);

  return (
    <div
      onClick={handleMarkAsRead}
      className={cn(
        'cursor-pointer rounded-xl border p-4 transition-colors hover:bg-accent/40',
        isNew ? 'border-primary/20 bg-accent/20' : 'border-border bg-card',
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 flex-1 items-start gap-3">
          <div
            className={cn(
              'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
              isNew ? 'bg-primary/10' : 'bg-muted',
            )}
          >
            <Bell className={cn('h-4 w-4', isNew ? 'text-primary' : 'text-muted-foreground')} />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <p className="text-sm font-semibold text-foreground">{title}</p>
              {isNew && (
                <span className="flex h-4 items-center rounded-full bg-primary px-1.5 text-[10px] font-medium text-primary-foreground">
                  New
                </span>
              )}
            </div>
            <p className="mt-1 text-xs text-muted-foreground">{description}</p>
            {actionText && actionLink && (
              <a
                href={finalActionLink}
                onClick={(e) => e.stopPropagation()}
                className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
              >
                {actionText} <ArrowRight className="h-3 w-3" />
              </a>
            )}
          </div>
        </div>

        <span className="shrink-0 text-xs text-muted-foreground">{time}</span>
      </div>
    </div>
  );
}
