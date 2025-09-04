// API Response Types
export interface ApiResponse<T = unknown> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

// User Types
export interface User {
  id: string;
  email: string;
  username: string;
  fullname: string;
  date_joined: string;
  is_active: boolean;
}

// Authentication Types
export interface SignupRequest {
  email: string;
  username: string;
  fullname: string;
  password: string;
  password_confirm: string;
}

export interface SignupResponse {
  message: string;
  user: User;
}

export interface GoogleAuthRequest {
  id_token: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface GoogleAuthResponse {
  access: string;
  refresh: string;
  user: {
    id: string;
    email: string;
    fullname: string;
  };
  created: boolean;
}

// Error Types
export interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

// HTTP Methods
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

// Request Options
export interface RequestOptions {
  method?: HttpMethod;
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
}

// API Client Configuration
export interface ApiClientConfig {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface VerifiedUser {
  id: string;
  email: string;
  username: string;
  fullname: string;
}

// Notification Types
export interface NotificationSettings {
  in_app_notifications: boolean;
  email_notifications: boolean;
  web_push_notifications: boolean;
  new_script_generated: boolean;
  account_or_plan_changes: boolean;
  tips_content_inspiration: boolean;
  feature_updates: boolean;
  community_affiliate_updates: boolean;
}

// Privacy Types
export interface PrivacySettings {
  allow_product_update_emails: boolean;
  allow_anonymized_data_usage: boolean;
}
