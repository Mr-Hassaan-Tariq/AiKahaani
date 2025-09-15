'use client';

import { useState, useTransition } from 'react';
import { updateNotificationSettings } from '@/(dashboard)/actions';
import { NotificationSettingsType } from '@/(dashboard)/types';
import Card from '@/components/ui/Card';
import { toast } from 'react-toastify';

import { notificationTexts } from 'lib/localdata';
import Switch from 'components/common/Switch';

interface NotificationTogglesProps {
  initialSettings: NotificationSettingsType;
}

interface NotificationPreferences {
  deliveryChannels: Record<string, boolean>;
  notificationTypes: Record<string, boolean>;
}

export default function NotificationToggles({ initialSettings }: NotificationTogglesProps) {
  const [preferences, setPreferences] = useState<NotificationPreferences>(() => {
    const deliveryChannels = notificationTexts.deliveryChannels.options.reduce(
      (acc, option) => ({
        ...acc,
        [option.key]: initialSettings[option.key as keyof NotificationSettingsType] || false,
      }),
      {},
    );

    const notificationTypes = notificationTexts.notificationTypes.options.reduce(
      (acc, option) => ({
        ...acc,
        [option.key]: initialSettings[option.key as keyof NotificationSettingsType] || false,
      }),
      {},
    );

    return { deliveryChannels, notificationTypes };
  });

  const [isPending, startTransition] = useTransition();

  const handleDeliveryChannelToggle = async (key: string, checked: boolean) => {
    const newPreferences = {
      ...preferences,
      deliveryChannels: {
        ...preferences.deliveryChannels,
        [key]: checked,
      },
    };

    setPreferences(newPreferences);
    await saveNotificationSettings(newPreferences);
  };

  const handleNotificationTypeToggle = async (key: string, checked: boolean) => {
    const newPreferences = {
      ...preferences,
      notificationTypes: {
        ...preferences.notificationTypes,
        [key]: checked,
      },
    };

    setPreferences(newPreferences);
    await saveNotificationSettings(newPreferences);
  };

  const saveNotificationSettings = async (newPreferences: NotificationPreferences) => {
    startTransition(async () => {
      try {
        // Convert local state to API format
        const settings: NotificationSettingsType = {
          in_app_notifications: newPreferences.deliveryChannels.in_app_notifications || false,
          email_notifications: newPreferences.deliveryChannels.email_notifications || false,
          web_push_notifications: newPreferences.deliveryChannels.web_push_notifications || false,
          new_script_generated: newPreferences.notificationTypes.new_script_generated || false,
          account_or_plan_changes:
            newPreferences.notificationTypes.account_or_plan_changes || false,
          tips_content_inspiration:
            newPreferences.notificationTypes.tips_content_inspiration || false,
          feature_updates: newPreferences.notificationTypes.feature_updates || false,
          community_affiliate_updates:
            newPreferences.notificationTypes.community_affiliate_updates || false,
        };

        const result = await updateNotificationSettings(settings);

        if (result.isError) {
          throw new Error(
            result.error?.message?.toString() || 'Failed to update notification settings',
          );
        }

        toast.success('Notification settings updated successfully');
      } catch (error) {
        console.error('Failed to save notification settings:', error);
        toast.error('Failed to save notification settings');

        // Revert the change on error
        setPreferences(preferences);
      }
    });
  };

  return (
    <div className="space-y-6">
      <Card title={notificationTexts.deliveryChannels.title}>
        {notificationTexts.deliveryChannels.options.map((option, index) => (
          <Switch
            key={index}
            label={option.label}
            description={option.description}
            defaultChecked={preferences.deliveryChannels[option.key]}
            onToggle={(checked) => handleDeliveryChannelToggle(option.key, checked)}
            disabled={isPending}
          />
        ))}
      </Card>

      <Card title={notificationTexts.notificationTypes.title}>
        {notificationTexts.notificationTypes.options.map((option, index) => (
          <Switch
            key={index}
            label={option.label}
            defaultChecked={preferences.notificationTypes[option.key]}
            onToggle={(checked) => handleNotificationTypeToggle(option.key, checked)}
            disabled={isPending}
          />
        ))}
      </Card>

      {isPending && (
        <div className="flex items-center justify-center py-2">
          <div className="text-sm text-gray-400">Saving changes...</div>
        </div>
      )}
    </div>
  );
}
