'use client';

import { useState } from 'react';
import Card from '@/components/ui/Card';

import { notificationTexts } from 'lib/localdata';
import Switch from 'components/common/Switch';

interface NotificationPreferences {
  deliveryChannels: Record<string, boolean>;
  notificationTypes: Record<string, boolean>;
}

export default function NotificationsPage() {
  const [preferences, setPreferences] = useState<NotificationPreferences>(() => {
    const deliveryChannels = notificationTexts.deliveryChannels.options.reduce(
      (acc, option) => ({ ...acc, [option.label]: false }),
      {},
    );

    const notificationTypes = notificationTexts.notificationTypes.options.reduce(
      (acc, option) => ({ ...acc, [option.label]: false }),
      {},
    );

    return { deliveryChannels, notificationTypes };
  });

  const handleDeliveryChannelToggle = (label: string, checked: boolean) => {
    setPreferences((prev) => ({
      ...prev,
      deliveryChannels: {
        ...prev.deliveryChannels,
        [label]: checked,
      },
    }));
  };

  const handleNotificationTypeToggle = (label: string, checked: boolean) => {
    setPreferences((prev) => ({
      ...prev,
      notificationTypes: {
        ...prev.notificationTypes,
        [label]: checked,
      },
    }));
  };

  console.log(preferences);

  return (
    <div className="mx-auto space-y-6">
      <Card title={notificationTexts.deliveryChannels.title}>
        {notificationTexts.deliveryChannels.options.map((option, index) => (
          <Switch
            key={index}
            {...option}
            defaultChecked={preferences.deliveryChannels[option.label]}
            onToggle={(checked) => handleDeliveryChannelToggle(option.label, checked)}
          />
        ))}
      </Card>

      <Card title={notificationTexts.notificationTypes.title}>
        {notificationTexts.notificationTypes.options.map((option, index) => (
          <Switch
            key={index}
            {...option}
            defaultChecked={preferences.notificationTypes[option.label]}
            onToggle={(checked) => handleNotificationTypeToggle(option.label, checked)}
          />
        ))}
      </Card>
    </div>
  );
}
