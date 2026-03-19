export interface UserProfileType {
  id: number;
  email: string;
  username: string;
  fullname: string;
  preferred_language: string;
  /** Backend field name is profile_picture_url */
  profile_picture_url: string | null;
  /** Alias for profile_picture_url kept for layout compatibility */
  profile_picture?: string | null;
  is_email_verified: boolean;
  is_active: boolean;
  role: string;
  plan: string;
  plan_expires_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface NotificationPreferencesType {
  in_app_notifications?: boolean;
  email_notifications?: boolean;
  web_push_notifications?: boolean;
  new_script_generated?: boolean;
  account_or_plan_changes?: boolean;
  tips_content_inspiration?: boolean;
  feature_updates?: boolean;
  [key: string]: boolean | undefined;
}

export interface NotificationSettingsType {
  notification_preferences: NotificationPreferencesType;
  privacy_preferences: Record<string, unknown>;
}

export interface NotificationType {
  id: number;
  notification_type: string;
  title: string;
  message: string;
  /** Backend field name is is_read */
  is_read: boolean;
  /** Alias kept for component compatibility */
  read?: boolean;
  extra_data: Record<string, any>;
  created_at: string;
}

export type NicheChannel = {
  name: string;
  link: string;
};

export type NicheStructure = {
  intro?: string;
  body?: string;
  outro?: string;
};

export type Niche = {
  thumbnail_url: string | null;
  id: number;
  admin: number;
  title: string;
  tagline: string;
  thumbnail: string | null;
  script_structure: NicheStructure | null;
  tone: string[];
  pacing: string[];
  top_channels: NicheChannel[];
  best_for: string[];
  status: string;
  created: string;
  modified: string;
};

export type NichePaginatedResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Niche[];
};
