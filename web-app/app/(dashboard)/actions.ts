'use server';

import { NotificationSettingsType, NotificationType, UserProfileType } from './types';
import { getServerDataAction, updateServerDataAction } from 'lib/utils/getServerDataAction';

export async function getUserProfile() {
  return await getServerDataAction<UserProfileType>('/v1/users/me');
}

export async function getNotificationSettings() {
  return await getServerDataAction<NotificationSettingsType>('/v1/users/me/settings/notification');
}

export async function updateNotificationSettings(settings: NotificationSettingsType) {
  // Backend PATCH expects flat fields from notification_preferences
  const payload = settings.notification_preferences ?? (settings as any);
  return await updateServerDataAction<NotificationSettingsType>(
    '/v1/users/me/settings/notification',
    payload,
  );
}

export async function getNotifications() {
  return await getServerDataAction<{ data: NotificationType[]; meta: { total: number } }>(
    '/v1/notifications?limit=4&offset=0',
  );
}
