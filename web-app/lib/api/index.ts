import { env } from '../../env.mjs';

// Legacy exports for backward compatibility
export const method = {
  post: 'POST',
  get: 'GET',
  delete: 'DELETE',
  put: 'PUT',
  patch: 'PATCH',
};

export const baseUrl = env.NEXT_PUBLIC_API_URL;

// New API wrapper exports
export { AuthService } from './auth';
export { ApiClient } from './client';
export { NotificationService } from './notifications';
export { PrivacyService } from './privacy';
export { UserService } from './user';
export {
  api,
  ApiWrapper,
  authService,
  notificationService,
  privacyService,
  userService,
} from './wrapper';

// Type exports
export type {
  ApiClientConfig,
  ApiError,
  ApiResponse,
  AuthTokens,
  GoogleAuthRequest,
  GoogleAuthResponse,
  HttpMethod,
  NotificationSettings,
  PrivacySettings,
  RequestOptions,
  SignupRequest,
  SignupResponse,
  User,
} from './types';
