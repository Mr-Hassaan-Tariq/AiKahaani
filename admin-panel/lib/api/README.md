# API Wrapper Documentation

This API wrapper provides a clean, type-safe interface for interacting with the Tubegenius backend API. It includes authentication, user management, and proper error handling.

## Features

- 🔐 **Authentication Management** - JWT token handling with automatic storage
- 👤 **User Management** - Profile operations and account management
- 🎯 **Type Safety** - Full TypeScript support with proper types
- ⚡ **React Hooks** - Ready-to-use React hooks for state management
- 🛡️ **Error Handling** - Comprehensive error handling and validation
- 🔄 **Auto-refresh** - Automatic token refresh (future enhancement)

## Quick Start

### Basic Usage

```typescript
import { api, authService, userService } from '@/lib/api';

// Check if user is authenticated
const isAuth = api.isAuthenticated();

// Sign up a new user
const signupData = {
  email: 'user@example.com',
  username: 'username',
  fullname: 'John Doe',
  password: 'password123',
  password_confirm: 'password123',
};

try {
  const response = await authService.signup(signupData);
  console.log('User created:', response.user);
} catch (error) {
  console.error('Signup failed:', error.message);
}

// Google authentication
try {
  const response = await authService.googleAuth(googleIdToken);
  console.log('Authenticated:', response.user);
} catch (error) {
  console.error('Google auth failed:', error.message);
}

// Get user profile
try {
  const profile = await userService.getProfile();
  console.log('Profile:', profile);
} catch (error) {
  console.error('Failed to get profile:', error.message);
}
```

### Using React Hooks

```typescript
import { useAuth, useUserProfile } from '@/lib/api/hooks';

function MyComponent() {
  const { user, isAuthenticated, loading, error, signup, googleAuth, logout } = useAuth();
  const { profile, getProfile, updateProfile } = useUserProfile();

  const handleSignup = async () => {
    try {
      await signup({
        email: 'user@example.com',
        username: 'username',
        fullname: 'John Doe',
        password: 'password123',
        password_confirm: 'password123'
      });
    } catch (error) {
      console.error('Signup failed:', error);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {isAuthenticated ? (
        <div>
          <p>Welcome, {user?.fullname}!</p>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <button onClick={handleSignup}>Sign Up</button>
      )}
    </div>
  );
}
```

## API Reference

### Core Classes

#### `ApiWrapper`

Main wrapper class that provides access to all services.

```typescript
const api = new ApiWrapper();

// Check authentication status
const isAuth = api.isAuthenticated();

// Logout user
api.logout();

// Get underlying client
const client = api.getClient();
```

#### `ApiClient`

Low-level HTTP client with authentication and error handling.

```typescript
const client = new ApiClient({
  baseUrl: 'https://api.example.com',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Make requests
const response = await client.get('/api/endpoint');
const response = await client.post('/api/endpoint', data);
const response = await client.put('/api/endpoint', data);
const response = await client.patch('/api/endpoint', data);
const response = await client.delete('/api/endpoint');
```

### Services

#### `AuthService`

Handles authentication operations.

```typescript
const authService = new AuthService(apiClient);

// Sign up
const response = await authService.signup(signupData);

// Google authentication
const response = await authService.googleAuth(idToken);

// Check authentication
const isAuth = authService.isAuthenticated();

// Logout
authService.logout();

// User data management
const user = authService.getCurrentUser();
authService.setCurrentUser(user);
authService.clearCurrentUser();
```

#### `UserService`

Handles user profile operations.

```typescript
const userService = new UserService(apiClient);

// Get profile
const profile = await userService.getProfile();

// Update profile
const response = await userService.updateProfile({
  fullname: 'New Name',
  username: 'newusername',
});

// Change password
await userService.changePassword('currentPassword', 'newPassword', 'confirmPassword');

// Delete account
await userService.deleteAccount();
```

### React Hooks

#### `useAuth()`

Authentication hook with state management.

```typescript
const {
  user, // Current user data
  isAuthenticated, // Authentication status
  loading, // Loading state
  error, // Error message
  signup, // Signup function
  googleAuth, // Google auth function
  logout, // Logout function
} = useAuth();
```

#### `useUserProfile()`

User profile management hook.

```typescript
const {
  profile, // User profile data
  loading, // Loading state
  error, // Error message
  getProfile, // Get profile function
  updateProfile, // Update profile function
} = useUserProfile();
```

#### `useApiStatus()`

Network status hook.

```typescript
const { isOnline } = useApiStatus();
```

## Types

### User Types

```typescript
interface User {
  id: string;
  email: string;
  username: string;
  fullname: string;
  date_joined: string;
  is_active: boolean;
}
```

### Authentication Types

```typescript
interface SignupRequest {
  email: string;
  username: string;
  fullname: string;
  password: string;
  password_confirm: string;
}

interface GoogleAuthRequest {
  id_token: string;
}

interface GoogleAuthResponse {
  access: string;
  refresh: string;
  user: {
    id: string;
    email: string;
    fullname: string;
  };
  created: boolean;
}
```

### API Response Types

```typescript
interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

interface ApiError {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
}
```

## Error Handling

The API wrapper provides comprehensive error handling:

```typescript
try {
  const response = await authService.signup(userData);
} catch (error: any) {
  console.error('Error:', error.message);
  console.error('Status:', error.status);
  console.error('Details:', error.data?.errors);
}
```

Common error scenarios:

- **401 Unauthorized** - Invalid or expired token
- **400 Bad Request** - Validation errors
- **500 Internal Server Error** - Server-side errors
- **Network errors** - Connection issues

## Configuration

The API wrapper uses environment variables for configuration:

```typescript
// env.mjs
export const env = createEnv({
  client: {
    NEXT_PUBLIC_API_URL: z.string().url(),
    NEXT_PUBLIC_GOOGLE_CLIENT_ID: z.string(),
  },
  // ...
});
```

## Best Practices

1. **Always handle errors** - Wrap API calls in try-catch blocks
2. **Use React hooks** - For components that need authentication state
3. **Check authentication** - Before making authenticated requests
4. **Handle loading states** - Show loading indicators during API calls
5. **Validate data** - Validate user input before sending to API

## Examples

### Protected Route Component

```typescript
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" />;

  return <>{children}</>;
}
```

### Login Form

```typescript
function LoginForm() {
  const { googleAuth, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Handle regular login or Google auth
      await googleAuth(googleIdToken);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Loading...' : 'Login'}
      </button>
    </form>
  );
}
```

## Migration from Legacy Code

If you're migrating from the old API structure:

```typescript
// Old way
// New way
import { api, authService, baseUrl, method } from '@/lib/api';

// Old way
const response = await fetch(`${baseUrl}/api/auth/signup/`, {
  method: method.post,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(userData),
});

// New way
const response = await authService.signup(userData);
```
