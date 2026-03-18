'use client';

import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Bell } from 'lucide-react';

import NotificationItem from './_components/NotificationItem';
import NotificationTabs from './_components/NotificationTabs';
import Pagination from './_components/Pagination';
import ProductUpdates from './_components/ProductUpdates';
import Subscription from './_components/subscription';
import { formatTimeAgo } from 'lib/utils';
import { getClientDataAction } from 'lib/utils/clientDataActions';
import { Spinner } from 'components/ui/Spinner';

type NotificationApiResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: NotificationType[];
};

type NotificationType = {
  id: number;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
  metadata: Record<string, any>;
};

export default function NotificationsPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get('query');

  const [notifications, setNotifications] = useState<NotificationType[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalItems, setTotalItems] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const components: Record<string, React.ReactElement> = {
    'product-updates': <ProductUpdates />,
    subscription: <Subscription />,
  };

  const fetchNotifications = useCallback(async (page = 1) => {
    try {
      setLoading(true);
      const offset = (page - 1) * itemsPerPage;
      const url = `v1/notifications/all-notifications/?limit=${itemsPerPage}&offset=${offset}`;
      const data = await getClientDataAction<NotificationApiResponse>(url);
      if (data?.results) {
        setNotifications(data.results);
        setTotalItems(data.count);
      }
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications(currentPage);
  }, [fetchNotifications, currentPage]);

  if (query && components[query]) {
    return <NotificationTabs>{components[query]}</NotificationTabs>;
  }

  return (
    <NotificationTabs>
      {loading ? (
        <div className="flex min-h-[200px] items-center justify-center">
          <Spinner size="md" color="primary" />
        </div>
      ) : notifications.length > 0 ? (
        <div className="flex flex-col gap-2">
          {notifications.map((item) => {
            const scriptLink = item.metadata?.script?.link;
            const outlineLink = item.metadata?.outline?.link;
            const link = scriptLink || outlineLink;
            return (
              <NotificationItem
                key={item.id}
                id={item.id}
                title={item.title}
                description={item.message}
                time={formatTimeAgo(item.created_at)}
                isNew={!item.read}
                actionText={link ? 'View' : undefined}
                actionLink={link}
                onRead={(id) =>
                  setNotifications((prev) =>
                    prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
                  )
                }
              />
            );
          })}
          {totalItems > itemsPerPage && (
            <div className="pt-4">
              <Pagination
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
                currentPage={currentPage}
                onPageChange={setCurrentPage}
              />
            </div>
          )}
        </div>
      ) : (
        <div className="flex min-h-[300px] flex-col items-center justify-center gap-3 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-accent">
            <Bell className="h-6 w-6 text-muted-foreground" />
          </div>
          <p className="text-sm font-medium text-foreground">You&apos;re all caught up!</p>
          <p className="max-w-xs text-xs text-muted-foreground">
            No new notifications at the moment. Check back later or explore the latest features.
          </p>
        </div>
      )}
    </NotificationTabs>
  );
}
