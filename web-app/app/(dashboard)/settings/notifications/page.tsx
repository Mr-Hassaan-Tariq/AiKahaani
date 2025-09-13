'use client';

import Card from '@/components/ui/Card';
import { toast } from 'react-toastify';

import { NotificationSettings } from 'lib/api';
import { useGetNotificationSettings, useUpdateNotificationSettings } from 'lib/hooks/useSettings';
import { notificationTexts } from 'lib/localdata';
import Switch from 'components/common/Switch';

export default function NotificationsPage() {
  const { data: notificationSettings, isLoading } = useGetNotificationSettings();
  const { mutate: updateNotificationSettings, isPending: isUpdating } =
    useUpdateNotificationSettings();

  const handleDeliveryChannelToggle = (key: string, checked: boolean) => {
    if (!notificationSettings) return;

    const updatedSettings = {
      ...notificationSettings,
      [key]: checked,
    };

    saveNotificationSettings(updatedSettings);
  };

  const handleNotificationTypeToggle = (key: string, checked: boolean) => {
    if (!notificationSettings) return;

    const updatedSettings = {
      ...notificationSettings,
      [key]: checked,
    };

    saveNotificationSettings(updatedSettings);
  };

  const saveNotificationSettings = (updatedSettings: NotificationSettings) => {
    updateNotificationSettings(updatedSettings, {
      onSuccess: () => {
        toast.success('Notification settings updated successfully');
      },
      onError: (error) => {
        // eslint-disable-next-line no-console
        console.error('Failed to save notification settings:', error);
        toast.error('Failed to save notification settings');
      },
    });
  };

  if (isLoading) {
    return (
      <div className="mx-auto space-y-6">
        <div className="flex items-center justify-center py-8">
          <div className="text-gray-400">Loading notification settings...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto space-y-6">
      <Card title={notificationTexts.deliveryChannels.title}>
        {notificationTexts.deliveryChannels.options.map((option) => (
          <Switch
            key={option.key}
            label={option.label}
            description={option.description}
            defaultChecked={notificationSettings?.[option.key as keyof NotificationSettings]}
            onToggle={(checked) => handleDeliveryChannelToggle(option.key, checked)}
            disabled={isUpdating}
          />
        ))}
      </Card>

      <Card title={notificationTexts.notificationTypes.title}>
        {notificationTexts.notificationTypes.options.map((option) => (
          <Switch
            key={option.key}
            label={option.label}
            defaultChecked={notificationSettings?.[option.key as keyof NotificationSettings]}
            onToggle={(checked) => handleNotificationTypeToggle(option.key, checked)}
            disabled={isUpdating}
          />
        ))}
      </Card>

      {isUpdating && (
        <div className="flex items-center justify-center py-2">
          <div className="text-sm text-gray-400">Saving changes...</div>
        </div>
      )}
    </div>
  );
}
