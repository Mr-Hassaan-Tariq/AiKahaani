import { getNotificationSettings } from '@/(dashboard)/actions';

import NotificationToggles from './_components/NotificationToggles';

export default async function NotificationsPage() {
  const { data, error, isError } = await getNotificationSettings();

  return (
    <div className="flex flex-col gap-5">
      {isError && <p className="text-sm text-destructive">{error?.message?.toString()}</p>}
      {data && <NotificationToggles initialSettings={data} />}
    </div>
  );
}
