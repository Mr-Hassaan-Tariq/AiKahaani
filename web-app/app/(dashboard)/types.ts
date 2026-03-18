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
}

export interface NotificationType {
  id: number;
  title: string;
  message: string;
  read: boolean;
  created_at: string;
  metadata: Record<string, any>;
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
