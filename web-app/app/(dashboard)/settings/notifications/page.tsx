import { getNotificationSettings } from '@/(dashboard)/actions';

import NotificationToggles from './_components/NotificationToggles';
import Col from 'components/ui/Col';
import Text from 'components/ui/Text';

export default async function NotificationsPage() {
  const { data, error, isError } = await getNotificationSettings();

  return (
    <Col className="gap-10 text-white">
      {isError && (
        <Text variant="base" className="text-brand-secondary">
          {error.message?.toString()}
        </Text>
      )}
      {data && <NotificationToggles initialSettings={data} />}
    </Col>
  );
}
