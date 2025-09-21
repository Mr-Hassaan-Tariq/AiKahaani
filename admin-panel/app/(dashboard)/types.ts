export interface UserProfileType {
  id: number;
  email: string;
  username: string;
  fullname: string;
  preferred_language: string;
  profile_picture: string;
  is_email_verified: boolean;
}

export interface NotificationSettingsType {
  in_app_notifications: boolean;
  email_notifications: boolean;
  web_push_notifications: boolean;
  new_script_generated: boolean;
  account_or_plan_changes: boolean;
  tips_content_inspiration: boolean;
  feature_updates: boolean;
  community_affiliate_updates: boolean;
}
