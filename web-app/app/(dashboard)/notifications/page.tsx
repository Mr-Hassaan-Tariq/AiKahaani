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
import { PaginatedApiResponse } from 'lib/utils/getServerDataAction';
import { Spinner } from 'components/ui/Spinner';

type NotificationType = {
  id: number;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  extra_data: Record<string, any>;
  created_at: string;
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
      const url = `/v1/notifications?limit=${itemsPerPage}&offset=${offset}`;
      const data = await getClientDataAction<PaginatedApiResponse<NotificationType>>(url);
      if (data?.data) {
        setNotifications(data.data);
        setTotalItems(data.meta?.total ?? 0);
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
            const scriptLink = item.extra_data?.script?.link;
            const outlineLink = item.extra_data?.outline?.link;
            const link = scriptLink || outlineLink;
            return (
              <NotificationItem
                key={item.id}
                id={item.id}
                title={item.title}
                description={item.message}
                time={formatTimeAgo(item.created_at)}
                isNew={!item.is_read}
                actionText={link ? 'View' : undefined}
                actionLink={link}
                onRead={(id) =>
                  setNotifications((prev) =>
                    prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)),
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
