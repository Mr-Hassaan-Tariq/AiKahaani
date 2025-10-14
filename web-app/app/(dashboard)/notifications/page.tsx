'use client';

import { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import BellIcon from '@assets/svg/bell-notification.svg';

import EmptyState from '../_components/EmptyState';
import NotificationItem from './_components/NotificationItem';
import NotificationTabs from './_components/NotificationTabs';
import Pagination from './_components/Pagination';
import ProductUpdates from './_components/ProductUpdates';
import Subscription from './_components/subscription';
import { formatTimeAgo } from 'lib/utils';
import { getClientDataAction } from 'lib/utils/clientDataActions';

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
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications(currentPage);
  }, [fetchNotifications, currentPage]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const hasNotifications = notifications.length > 0;

  return (
    <div className="px-10">
      <NotificationTabs>
        {query && components[query] ? (
          components[query]
        ) : loading ? (
          <p className="text-gray-400">Loading notifications...</p>
        ) : hasNotifications ? (
          <>
            {notifications.map((item) => (
              <NotificationItem
                key={item.id}
                id={item.id}
                title={item.title}
                description={item.message}
                time={formatTimeAgo(item.created_at)}
                isNew={!item.read}
                icon={BellIcon}
                onRead={(id: number) =>
                  setNotifications((prev) =>
                    prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
                  )
                }
              />
            ))}

            <Pagination
              totalItems={totalItems}
              itemsPerPage={itemsPerPage}
              currentPage={currentPage}
              onPageChange={handlePageChange}
            />
          </>
        ) : (
          <EmptyState
            icon={BellIcon}
            title="You’re all caught up!"
            description="There are no new notifications at the moment. Check back later or explore the latest features in the meantime."
          />
        )}
      </NotificationTabs>
    </div>
  );
}
