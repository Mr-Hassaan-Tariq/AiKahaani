'use server';

import { NotificationSettingsType, NotificationType, UserProfileType } from './types';
import { getServerDataAction, updateServerDataAction } from 'lib/utils/getServerDataAction';

export async function getUserProfile() {
  return await getServerDataAction<UserProfileType>('v1/users/details/');
}

export async function getNotificationSettings() {
  return await getServerDataAction<NotificationSettingsType>('v1/users/notifications');
}

export async function updateNotificationSettings(settings: NotificationSettingsType) {
  return await updateServerDataAction<NotificationSettingsType>('v1/users/notifications', settings);
}

export async function getNotifications() {
  return await getServerDataAction<NotificationType>(
    'v1/notifications/all-notifications/?limit=4&offset=0',
  );
}
