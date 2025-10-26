import { useCallback, useEffect, useState } from 'react';

import type { SignupRequest, User } from './types';
import { AdminUser, UpdateUserRequest, UpdateUserStatusRequest } from './user';
import { api, authService, userService } from './wrapper';

// Authentication hook
export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = () => {
      try {
        const currentUser = authService.getCurrentUser();
        const authenticated = api.isAuthenticated();

        setUser(currentUser);
        setIsAuthenticated(authenticated);
      } catch (err) {
        const error = err as { message: string };
        setError(`Failed to initialize authentication: ${error.message}`);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Signup function
  const signup = useCallback(async (userData: SignupRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authService.signup(userData);
      setUser(response.user);
      setIsAuthenticated(true);
      authService.setCurrentUser(response.user);
      return response;
    } catch (err) {
      const error = err as { message: string };
      const errorMessage = error.message || 'Signup failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Google authentication function
  const googleAuth = useCallback(async (idToken: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authService.googleAuth(idToken);
      // Convert the simplified user object to full User type
      const fullUser: User = {
        id: response.user.id,
        email: response.user.email,
        fullname: response.user.fullname,
        username: response.user.email.split('@')[0], // Fallback username
        date_joined: new Date().toISOString(),
        is_active: true,
      };
      setUser(fullUser);
      setIsAuthenticated(true);
      authService.setCurrentUser(fullUser);
      return response;
    } catch (err) {
      const error = err as { message: string };
      const errorMessage = error.message || 'Google authentication failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Logout function
  const logout = useCallback(() => {
    api.logout();
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
  }, []);

  return {
    user,
    isAuthenticated,
    loading,
    error,
    signup,
    googleAuth,
    logout,
  };
};

// User profile hook
export const useUserProfile = () => {
  const [profile, setProfile] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get user profile
  const getProfile = useCallback(async () => {
    if (!api.isAuthenticated()) {
      setError('User not authenticated');
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const userProfile = await userService.getProfile();
      setProfile(userProfile);
      return userProfile;
    } catch (err) {
      const error = err as { message: string };
      const errorMessage = error.message || 'Failed to get profile';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Update user profile
  const updateProfile = useCallback(async (userData: UpdateUserRequest) => {
    if (!api.isAuthenticated()) {
      setError('User not authenticated');
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await userService.updateProfile(userData);
      setProfile(response.user);
      return response;
    } catch (err) {
      const error = err as { message: string };
      const errorMessage = error.message || 'Failed to update profile';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    profile,
    loading,
    error,
    getProfile,
    updateProfile,
  };
};

// API status hook
export const useApiStatus = () => {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return { isOnline };
};

// Admin User Management hook
export const useAdminUsers = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
  });

  // Get all users
  const getUsers = useCallback(async (page: number = 1, limit: number = 20, search?: string) => {
    if (!api.isAuthenticated()) {
      setError('User not authenticated');
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await userService.getAdminUsers(page, limit, search);
      setUsers(response.results);
      setPagination({
        page: page,
        limit: limit,
        total: response.count,
      });
      return response;
    } catch (err) {
      const error = err as { message: string };
      const errorMessage = error.message || 'Failed to get users';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get a specific user
  const getUser = useCallback(async (userId: string) => {
    if (!api.isAuthenticated()) {
      setError('User not authenticated');
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const user = await userService.getAdminUser(userId);
      return user;
    } catch (err) {
      const error = err as { message: string };
      const errorMessage = error.message || 'Failed to get user';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Update user status
  const updateUserStatus = useCallback(
    async (userId: string, statusData: UpdateUserStatusRequest) => {
      if (!api.isAuthenticated()) {
        setError('User not authenticated');
        return null;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await userService.updateUserStatus(userId, statusData);

        // Update the user in the local state
        setUsers((prevUsers) =>
          prevUsers.map((user) => (user?.id === userId ? response?.user : user)),
        );
        setUsers;

        return response;
      } catch (err) {
        const error = err as { message: string };
        const errorMessage = error.message || 'Failed to update user status';
        setError(errorMessage);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  // Delete user
  const deleteUser = useCallback(async (userId: string) => {
    if (!api.isAuthenticated()) {
      setError('User not authenticated');
      return null;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await userService.deleteUser(userId);

      // Remove the user from local state
      setUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId));

      // Update total count
      setPagination((prev) => ({
        ...prev,
        total: prev.total - 1,
      }));

      return response;
    } catch (err) {
      const error = err as { message: string };
      const errorMessage = error.message || 'Failed to delete user';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Activate user
  const activateUser = useCallback(
    async (userId: string) => {
      return updateUserStatus(userId, { is_active: true });
    },
    [updateUserStatus],
  );

  // Deactivate user
  const deactivateUser = useCallback(
    async (userId: string) => {
      return updateUserStatus(userId, { is_active: false });
    },
    [updateUserStatus],
  );

  // Grant admin privileges
  const grantAdminPrivileges = useCallback(
    async (userId: string) => {
      return updateUserStatus(userId, { is_admin: true });
    },
    [updateUserStatus],
  );

  // Revoke admin privileges
  const revokeAdminPrivileges = useCallback(
    async (userId: string) => {
      return updateUserStatus(userId, { is_admin: false });
    },
    [updateUserStatus],
  );

  return {
    users,
    loading,
    error,
    pagination,
    getUsers,
    getUser,
    updateUserStatus,
    deleteUser,
    activateUser,
    deactivateUser,
    grantAdminPrivileges,
    revokeAdminPrivileges,
  };
};
