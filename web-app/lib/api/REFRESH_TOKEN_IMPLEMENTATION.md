# Automatic Refresh Token Implementation

## Overview

This implementation adds automatic refresh token functionality to the web-app that calls the `/api/auth/refresh/` endpoint whenever the browser loads, if a refresh token is available.

## Implementation Details

### 1. Backend Endpoint

- **Endpoint**: `/api/auth/refresh/`
- **Method**: POST
- **Request Body**: `{"refresh_token": "string"}`
- **Response**:
  ```json
  {
    "access_token": "string",
    "refresh_token": "string",
    "message": "string"
  }
  ```

### 2. Frontend Implementation

#### AuthService (`lib/api/auth.ts`)

- Added `refreshToken()` method that calls the refresh endpoint
- Automatically updates tokens in localStorage
- Handles errors gracefully

#### ApiClient (`lib/api/client.ts`)

- Made `getRefreshToken()` method public to allow access from AuthService
- Maintains existing token management functionality

#### AutoRefresh Hook (`lib/hooks/useAutoRefresh.tsx`)

- `useAutoRefresh()`: Hook that automatically refreshes tokens on browser load
- `AutoRefreshProvider`: Provider component that wraps the app
- Only runs on client-side
- Skips refresh if already authenticated or no refresh token available
- Updates access token cookie for server-side requests
- Clears tokens and logs out if refresh fails

#### Layout Integration (`app/layout.tsx`)

- Added `AutoRefreshProvider` to wrap the entire app
- Ensures refresh token is called on every browser load

#### Auth Hook (`lib/api/hooks.ts`)

- Added `refreshToken()` method to the `useAuth()` hook
- Provides manual refresh token functionality for components

#### API Wrapper (`lib/api/wrapper.ts`)

- Added `refreshToken()` method to the main API wrapper
- Provides access to refresh functionality throughout the app

## How It Works

1. **Browser Load**: When the browser loads, `AutoRefreshProvider` mounts
2. **Token Check**: Checks if refresh token exists in localStorage
3. **Authentication Check**: Checks if user is already authenticated
4. **Refresh Call**: If refresh token exists and user not authenticated, calls refresh endpoint
5. **Token Update**: Updates both localStorage and cookies with new tokens
6. **Error Handling**: If refresh fails, clears tokens and logs out user

## Usage

### Automatic (Default Behavior)

The refresh token is automatically called on browser load. No additional setup required.

### Manual Refresh

```typescript
import { useAuth } from 'lib/api/hooks';

function MyComponent() {
  const { refreshToken } = useAuth();

  const handleRefresh = async () => {
    try {
      await refreshToken();
      console.log('Token refreshed successfully');
    } catch (error) {
      console.error('Refresh failed:', error);
    }
  };

  return <button onClick={handleRefresh}>Refresh Token</button>;
}
```

### Direct API Usage

```typescript
import { authService } from 'lib/api';

const refreshTokens = async () => {
  try {
    const result = await authService.refreshToken();
    console.log('New tokens:', result);
  } catch (error) {
    console.error('Refresh failed:', error);
  }
};
```

## Security Considerations

- Refresh tokens are stored in localStorage (client-side only)
- Access tokens are stored in both localStorage and cookies
- Failed refresh attempts automatically clear all tokens
- Tokens are automatically updated in both storage locations
- Server-side requests use cookie-based authentication

## Error Handling

- Invalid refresh token: Clears all tokens and logs out
- Network errors: Logs warning but doesn't clear tokens
- Missing refresh token: Silently skips refresh
- Already authenticated: Skips refresh to avoid unnecessary calls
