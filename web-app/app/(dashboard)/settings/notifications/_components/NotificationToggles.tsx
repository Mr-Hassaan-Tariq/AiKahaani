'use client';

import { useState, useTransition } from 'react';
import { toast } from 'sonner';

import { updateNotificationSettings } from '@/(dashboard)/actions';
import { NotificationSettingsType } from '@/(dashboard)/types';
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
    const newPreferences = { ...preferences, deliveryChannels: { ...preferences.deliveryChannels, [key]: checked } };
    setPreferences(newPreferences);
    await saveNotificationSettings(newPreferences);
  };

  const handleNotificationTypeToggle = async (key: string, checked: boolean) => {
    const newPreferences = { ...preferences, notificationTypes: { ...preferences.notificationTypes, [key]: checked } };
    setPreferences(newPreferences);
    await saveNotificationSettings(newPreferences);
  };

  const saveNotificationSettings = async (newPreferences: NotificationPreferences) => {
    startTransition(async () => {
      try {
        const settings: NotificationSettingsType = {
          in_app_notifications:       newPreferences.deliveryChannels.in_app_notifications       || false,
          email_notifications:        newPreferences.deliveryChannels.email_notifications        || false,
          web_push_notifications:     newPreferences.deliveryChannels.web_push_notifications     || false,
          new_script_generated:       newPreferences.notificationTypes.new_script_generated      || false,
          account_or_plan_changes:    newPreferences.notificationTypes.account_or_plan_changes   || false,
          tips_content_inspiration:   newPreferences.notificationTypes.tips_content_inspiration  || false,
          feature_updates:            newPreferences.notificationTypes.feature_updates           || false,
        };
        const result = await updateNotificationSettings(settings);
        if (result.isError) throw new Error(result.error?.message?.toString() || 'Failed to update');
        toast.success('Notification settings updated');
      } catch {
        toast.error('Failed to save notification settings');
        setPreferences(preferences);
      }
    });
  };

  return (
    <div className="flex flex-col gap-4">

      {/* Delivery channels */}
      <div className="rounded-xl border border-border bg-card p-6">
        <h3 className="mb-4 text-sm font-semibold text-foreground">
          {notificationTexts.deliveryChannels.title}
        </h3>
        <div className="flex flex-col gap-4">
          {notificationTexts.deliveryChannels.options.map((option) => (
            <Switch
              key={option.key}
              label={option.label}
              description={option.description}
              defaultChecked={preferences.deliveryChannels[option.key]}
              onToggle={(checked) => handleDeliveryChannelToggle(option.key, checked)}
              disabled={isPending}
            />
          ))}
        </div>
      </div>

      {/* Notification types */}
      <div className="rounded-xl border border-border bg-card p-6">
        <h3 className="mb-4 text-sm font-semibold text-foreground">
          {notificationTexts.notificationTypes.title}
        </h3>
        <div className="flex flex-col gap-4">
          {notificationTexts.notificationTypes.options.map((option) => (
            <Switch
              key={option.key}
              label={option.label}
              defaultChecked={preferences.notificationTypes[option.key]}
              onToggle={(checked) => handleNotificationTypeToggle(option.key, checked)}
              disabled={isPending}
            />
          ))}
        </div>
      </div>

      {isPending && (
        <p className="text-xs text-muted-foreground">Saving…</p>
      )}
    </div>
  );
}
