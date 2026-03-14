'use client';

import { useRouter } from 'next/navigation';
import { Bell, X } from 'lucide-react';

import { Drawer, DrawerClose, DrawerContent, DrawerTrigger } from 'components/shadcn_ui/drawer';

export function MobileDrawer() {
  const router = useRouter();

  return (
    <Drawer>
      <DrawerTrigger asChild>
        <button
          aria-label="Notifications"
          className="flex h-9 w-9 items-center justify-center rounded-md border border-border text-muted-foreground transition-colors hover:bg-muted"
        >
          <Bell className="h-4 w-4" />
        </button>
      </DrawerTrigger>

      <DrawerContent className="border-t border-border bg-card p-4">
        {/* Header */}
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground">Notifications</h2>
          <DrawerClose asChild>
            <button className="rounded-md p-1 text-muted-foreground hover:bg-muted">
              <X className="h-4 w-4" />
            </button>
          </DrawerClose>
        </div>

        {/* Empty state */}
        <div className="py-8 text-center">
          <Bell className="mx-auto mb-2 h-6 w-6 text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground">No notifications yet</p>
        </div>

        {/* Footer */}
        <DrawerClose asChild>
          <button
            className="mt-2 w-full text-center text-xs font-medium text-primary hover:underline"
            onClick={() => router.push('/notifications')}
          >
            View all notifications
          </button>
        </DrawerClose>
      </DrawerContent>
    </Drawer>
  );
}
