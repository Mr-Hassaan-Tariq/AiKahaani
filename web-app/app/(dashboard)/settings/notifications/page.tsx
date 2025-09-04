'use client';

import { useEffect, useState } from 'react';
import Card from '@/components/ui/Card';
import { toast } from 'react-toastify';

import { notificationService, NotificationSettings } from 'lib/api';
import { notificationTexts } from 'lib/localdata';
import Switch from 'components/common/Switch';

interface NotificationPreferences {
  deliveryChannels: Record<string, boolean>;
  notificationTypes: Record<string, boolean>;
}

export default function NotificationsPage() {
  const [preferences, setPreferences] = useState<NotificationPreferences>(() => {
    const deliveryChannels = notificationTexts.deliveryChannels.options.reduce(
      (acc, option) => ({ ...acc, [option.key]: false }),
      {},
    );

    const notificationTypes = notificationTexts.notificationTypes.options.reduce(
      (acc, option) => ({ ...acc, [option.key]: false }),
      {},
    );

    return { deliveryChannels, notificationTypes };
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Load notification settings on component mount
  useEffect(() => {
    const loadNotificationSettings = async () => {
      try {
        setLoading(true);
        const settings = await notificationService.getNotificationSettings();

        // Map API response to local state
        const deliveryChannels = notificationTexts.deliveryChannels.options.reduce(
          (acc, option) => ({
            ...acc,
            [option.key]: settings[option.key as keyof NotificationSettings] || false,
          }),
          {},
        );

        const notificationTypes = notificationTexts.notificationTypes.options.reduce(
          (acc, option) => ({
            ...acc,
            [option.key]: settings[option.key as keyof NotificationSettings] || false,
          }),
          {},
        );

        setPreferences({ deliveryChannels, notificationTypes });
      } catch (error) {
        console.error('Failed to load notification settings:', error);
        toast.error('Failed to load notification settings');
      } finally {
        setLoading(false);
      }
    };

    loadNotificationSettings();
  }, []);

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
    try {
      setSaving(true);

      // Convert local state to API format
      const settings: NotificationSettings = {
        in_app_notifications: newPreferences.deliveryChannels.in_app_notifications || false,
        email_notifications: newPreferences.deliveryChannels.email_notifications || false,
        web_push_notifications: newPreferences.deliveryChannels.web_push_notifications || false,
        new_script_generated: newPreferences.notificationTypes.new_script_generated || false,
        account_or_plan_changes: newPreferences.notificationTypes.account_or_plan_changes || false,
        tips_content_inspiration:
          newPreferences.notificationTypes.tips_content_inspiration || false,
        feature_updates: newPreferences.notificationTypes.feature_updates || false,
        community_affiliate_updates:
          newPreferences.notificationTypes.community_affiliate_updates || false,
      };

      await notificationService.updateNotificationSettings(settings);
      console.log('Notification settings updated successfully');
    } catch (error) {
      console.log('Failed to save notification settings:', error);

      // Revert the change on error
      setPreferences(preferences);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
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
        {notificationTexts.deliveryChannels.options.map((option, index) => (
          <Switch
            key={index}
            label={option.label}
            description={option.description}
            defaultChecked={preferences.deliveryChannels[option.key]}
            onToggle={(checked) => handleDeliveryChannelToggle(option.key, checked)}
            disabled={saving}
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
            disabled={saving}
          />
        ))}
      </Card>

      {saving && (
        <div className="flex items-center justify-center py-2">
          <div className="text-sm text-gray-400">Saving changes...</div>
        </div>
      )}
    </div>
  );
}
