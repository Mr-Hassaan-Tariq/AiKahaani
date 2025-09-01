'use client';

import { useSearchParams } from 'next/navigation';
import BellIcon from '@assets/svg/bell-notification.svg';

import EmptyState from './_components/EmptyState';
import NotificationItem from './_components/NotificationItem';
import NotificationTabs from './_components/NotificationTabs';
import ProductUpdates from './_components/ProductUpdates';
import Subscription from './_components/subscription';
import { notificationData } from 'lib/localdata';

export default function NotificationsPage() {
  const searchParams = useSearchParams();
  const query = searchParams.get('query');

  const components: Record<string, React.ReactElement> = {
    'product-updates': <ProductUpdates />,
    subscription: <Subscription />,
  };

  const hasNotifications = notificationData.length > 0;

  return (
    <NotificationTabs>
      {query && components[query] ? (
        components[query]
      ) : hasNotifications ? (
        notificationData.map((item) => (
          <NotificationItem
            key={`${item.title}-${item.time}`}
            title={item.title}
            description={item.description}
            time={item.time}
            actionText={item.actionText}
            actionLink={item.actionLink}
            isNew={item.isNew}
            icon={item.icon}
          />
        ))
      ) : (
        <EmptyState
          icon={BellIcon}
          title="You’re all caught up!"
          description="There are no new notifications at the moment. Check back later or explore the latest features in the meantime."
        />
      )}
    </NotificationTabs>
  );
}
