import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  authenticateUser,
  saveUserToStorage,
  loadUserFromStorage,
  clearUserFromStorage,
  updatePushToken,
} from '../services/auth';
import { registerForPushNotificationsAsync } from '../services/pushNotifications';

const AuthContext = createContext(null);

/**
 * AuthProvider wraps the application and provides authentication state
 * and methods to all child components via React Context.
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!user;

  /**
   * Load saved user from SecureStore on app start.
   * This restores the session if the user was previously logged in.
   */
  const loadUser = useCallback(async () => {
    try {
      setLoading(true);
      const savedUser = await loadUserFromStorage();
      if (savedUser) {
        setUser(savedUser);
      }
    } catch (error) {
      console.error('Error loading user:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Authenticate the user with username and password.
   * On success, saves user data to SecureStore and registers for push notifications.
   */
  const login = useCallback(async (username, password) => {
    try {
      setLoading(true);
      const userData = await authenticateUser(username, password);
      setUser(userData);
      await saveUserToStorage(userData);

      // Register for push notifications after successful login
      try {
        const pushToken = await registerForPushNotificationsAsync();
        if (pushToken && userData.id) {
          await updatePushToken(userData.id, pushToken);
        }
      } catch (pushError) {
        // Push notification registration failure should not block login
        console.warn('Failed to register push notifications:', pushError);
      }

      return userData;
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Log out the user by clearing state and stored data.
   */
  const logout = useCallback(async () => {
    try {
      setLoading(true);

      // Clear push token from database before logging out
      if (user?.id) {
        try {
          await updatePushToken(user.id, null);
        } catch (error) {
          console.warn('Failed to clear push token:', error);
        }
      }

      await clearUserFromStorage();
      setUser(null);
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      setLoading(false);
    }
  }, [user]);

  /**
   * Save the push notification token for the current user.
   */
  const savePushToken = useCallback(
    async (token) => {
      if (!user?.id) return;
      try {
        await updatePushToken(user.id, token);
      } catch (error) {
        console.error('Error saving push token:', error);
      }
    },
    [user]
  );

  /**
   * Refresh the user data from storage (e.g., after profile update).
   */
  const refreshUser = useCallback(async (updatedUser) => {
    if (updatedUser) {
      setUser(updatedUser);
      await saveUserToStorage(updatedUser);
    }
  }, []);

  // Load user on mount
  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    savePushToken,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Custom hook to access the auth context.
 * Must be used within an AuthProvider.
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
