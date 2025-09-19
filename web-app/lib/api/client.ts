import { ApiClientConfig, ApiError, ApiResponse, RequestOptions } from './types';

export class ApiClient {
  private baseUrl: string;
  private timeout: number;
  private defaultHeaders: Record<string, string>;

  constructor(config: ApiClientConfig) {
    this.baseUrl = config.baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.timeout = config.timeout || 10000; // 10 seconds default
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...config.headers,
    };
  }

  // Get access token from cookies or localStorage
  private getAccessToken(): string | null {
    if (typeof window === 'undefined') {
      // Running on the server, return null as we can't access cookies here
      return null;
    }

    // Try to get from cookies first (preferred method)
    const cookieToken = this.getCookie('access_token');
    if (cookieToken) {
      return cookieToken;
    }

    // Fallback to localStorage
    return localStorage.getItem('access_token');
  }

  // Helper function to get cookie value
  private getCookie(name: string): string | null {
    if (typeof window === 'undefined') {
      return null;
    }

    // Try multiple cookie parsing methods
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [key, value] = cookie.trim().split('=');
      if (key === name) {
        return decodeURIComponent(value);
      }
    }

    // Fallback to regex method
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  // Get refresh token from localStorage
  private getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token');
    }
    return null;
  }

  // Set tokens in localStorage
  private setTokensInStorage(access: string, refresh: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
    }
  }

  // Clear tokens from localStorage
  private clearTokensFromStorage(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  // Create headers with authentication
  private createHeaders(customHeaders?: Record<string, string>): Record<string, string> {
    const headers = { ...this.defaultHeaders, ...customHeaders };
    const token = this.getAccessToken();

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return headers;
  }

  // Handle API errors
  private handleError(response: Response, data?: unknown): never {
    const apiError = data as ApiError;
    const error: ApiError = {
      detail: apiError?.detail || apiError?.message || 'An error occurred',
      message: apiError?.message || 'An error occurred',
      errors: apiError?.errors,
    };

    // Handle authentication errors
    if (response.status === 401) {
      this.clearTokensFromStorage();
      // You can add a redirect to login page here
      // window.location.href = '/login';
    }

    throw {
      status: response.status,
      statusText: response.statusText,
      data: error,
      response,
    };
  }

  // Make HTTP request
  private async request<T>(
    endpoint: string,
    options: RequestOptions = {},
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = this.createHeaders(options.headers);

    const config: RequestInit = {
      method: options.method || 'GET',
      headers,
      signal: options.signal,
    };

    if (options.body && options.method !== 'GET') {
      config.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      let data: unknown;
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        this.handleError(response, data);
      }

      return {
        data: data as T,
        status: response.status,
        message: (data as { message: string })?.message,
      };
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw {
          status: 408,
          statusText: 'Request Timeout',
          data: { detail: 'Request timed out' },
        };
      }

      throw error;
    }
  }

  // Public methods for different HTTP verbs
  async get<T>(
    endpoint: string,
    options?: Omit<RequestOptions, 'method'>,
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(
    endpoint: string,
    body?: unknown,
    options?: Omit<RequestOptions, 'method' | 'body'>,
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'POST', body });
  }

  async put<T>(
    endpoint: string,
    body?: unknown,
    options?: Omit<RequestOptions, 'method' | 'body'>,
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PUT', body });
  }

  async patch<T>(
    endpoint: string,
    body?: unknown,
    options?: Omit<RequestOptions, 'method' | 'body'>,
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'PATCH', body });
  }

  async delete<T>(
    endpoint: string,
    options?: Omit<RequestOptions, 'method'>,
  ): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  // Authentication methods
  setTokens(access: string, refresh: string): void {
    this.setTokensInStorage(access, refresh);
  }

  clearTokens(): void {
    this.clearTokensFromStorage();
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }
}
