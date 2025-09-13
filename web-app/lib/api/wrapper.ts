import { env } from '../../env.mjs';
import { AuthService } from './auth';
import { ApiClient } from './client';
import { NotificationService } from './notifications';
import { SubscriptionService } from './subscription';
import { UserService } from './user';

/**
 * Main API wrapper class that provides access to all API services
 */
export class ApiWrapper {
  private client: ApiClient;
  public auth: AuthService;
  public user: UserService;
  public notifications: NotificationService;
  public subscription: SubscriptionService;
  constructor() {
    // Initialize the API client with configuration
    this.client = new ApiClient({
      baseUrl: env.NEXT_PUBLIC_API_URL,
      timeout: 10000, // 10 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Initialize services
    this.auth = new AuthService(this.client);
    this.user = new UserService(this.client);
    this.notifications = new NotificationService(this.client);
    this.subscription = new SubscriptionService(this.client);
  }

  /**
   * Get the underlying API client instance
   * @returns ApiClient instance
   */
  getClient(): ApiClient {
    return this.client;
  }

  /**
   * Check if user is authenticated
   * @returns boolean indicating authentication status
   */
  isAuthenticated(): boolean {
    return this.client.isAuthenticated();
  }

  /**
   * Logout user by clearing all tokens and user data
   */
  logout(): void {
    this.auth.logout();
    this.auth.clearCurrentUser();
  }

  /**
   * Initialize authentication state from localStorage
   * This should be called on app startup to restore authentication state
   */
  initializeAuth(): void {
    // The client automatically handles token management
    // This method can be used for additional initialization if needed
  }
}

// Create and export a singleton instance
export const api = new ApiWrapper();

// Export individual services for direct access
export const authService = api.auth;
export const userService = api.user;
export const notificationService = api.notifications;
export const subscriptionService = api.subscription;
