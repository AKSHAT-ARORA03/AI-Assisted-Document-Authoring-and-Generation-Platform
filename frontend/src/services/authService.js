import { useUser, useAuth } from '@clerk/clerk-react';
import axios from 'axios';
import { authAPI } from './api';

// Hybrid authentication service supporting both Clerk and JWT
export class AuthService {
  static async getToken() {
    // Try Clerk first if available
    if (window.Clerk && window.Clerk.session) {
      try {
        return await window.Clerk.session.getToken();
      } catch (error) {
        console.warn('Clerk token not available:', error);
      }
    }
    
    // Fallback to JWT token from localStorage
    return localStorage.getItem(process.env.REACT_APP_TOKEN_STORAGE_KEY);
  }

  static async login(email, password) {
    try {
      // Try JWT login first
      const response = await authAPI.login({ email, password });
      if (response.access_token) {
        localStorage.setItem(process.env.REACT_APP_TOKEN_STORAGE_KEY, response.access_token);
        return { success: true, user: response.user };
      }
    } catch (error) {
      console.warn('JWT login failed:', error);
      throw error;
    }
  }

  static async register(userData) {
    try {
      // Try JWT registration
      const response = await authAPI.register(userData);
      return { success: true, user: response };
    } catch (error) {
      console.warn('JWT registration failed:', error);
      throw error;
    }
  }

  static async logout() {
    // Clear JWT token
    localStorage.removeItem(process.env.REACT_APP_TOKEN_STORAGE_KEY);
    
    // Sign out from Clerk if available
    if (window.Clerk && window.Clerk.signOut) {
      try {
        await window.Clerk.signOut();
      } catch (error) {
        console.warn('Clerk signout failed:', error);
      }
    }
  }

  static async getCurrentUser() {
    const token = await this.getToken();
    if (!token) return null;

    try {
      const response = await authAPI.getCurrentUser();
      return response;
    } catch (error) {
      console.warn('Get current user failed:', error);
      return null;
    }
  }
}

// Clerk authentication hook
export const useClerkAuth = () => {
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();

  return {
    user,
    isLoaded,
    getToken,
    isAuthenticated: !!user
  };
};

export default AuthService;