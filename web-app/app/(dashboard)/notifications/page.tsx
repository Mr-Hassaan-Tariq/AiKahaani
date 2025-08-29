'use client';

import NotificationItem from './_components/NotificationItem';
import NotificationTabs from './_components/NotificationTabs';
import { notificationData } from 'lib/localdata';

export default function NotificationsPage() {
  return (
    <NotificationTabs>
      <div className="mx-auto">
        {notificationData.map((item, index) => (
          <NotificationItem key={index} {...item} />
        ))}
      </div>
    </NotificationTabs>
  );
}
