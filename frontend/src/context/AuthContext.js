import React, { createContext, useContext, useState, useEffect } from 'react';
import { useUser, useAuth as useClerkAuth } from '@clerk/clerk-react';
import { authAPI } from '../services/api';

// Check if Clerk is enabled
const clerkPubKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;
const isClerkEnabled = clerkPubKey && 
  clerkPubKey !== 'your-clerk-publishable-key-here' && 
  clerkPubKey.startsWith('pk_');

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [devLoginAttempted] = useState(false);

  // Clerk hooks (always call hooks to avoid React hooks rules violation)
  const clerkUser = useUser();
  const clerkAuth = useClerkAuth();
  
  // Extract values conditionally
  const { isSignedIn, user: actualClerkUser } = isClerkEnabled ? clerkUser : { isSignedIn: false, user: null };
  const { signOut } = isClerkEnabled ? clerkAuth : { signOut: null };

  useEffect(() => {
    const initAuth = async () => {
      // If Clerk is enabled and user is signed in via Clerk, use that
      if (isClerkEnabled && isSignedIn && actualClerkUser) {
        setUser({
          id: actualClerkUser.id,
          email: actualClerkUser.emailAddresses[0]?.emailAddress,
          full_name: actualClerkUser.fullName || `${actualClerkUser.firstName} ${actualClerkUser.lastName}`,
          created_at: actualClerkUser.createdAt,
          updated_at: actualClerkUser.updatedAt
        });
        setLoading(false);
        return;
      }
      
      // Fallback to JWT authentication
      if (token) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Error fetching user:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      } else {
        // Disable automatic dev login to prevent infinite loops
        // Users can manually login with test@example.com / password123
        console.log('No authentication found. Please login manually.');
      }
      setLoading(false);
    };

    initAuth();
  }, [token, isSignedIn, actualClerkUser, devLoginAttempted]);

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      setToken(response.access_token);
      localStorage.setItem('token', response.access_token);
      
      // Fetch user data
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const newUser = await authAPI.register(userData);
      
      // Auto login after registration
      await login({
        email: userData.email,
        password: userData.password
      });
      
      return { success: true, user: newUser };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const logout = async () => {
    try {
      // If using Clerk and signed in, sign out via Clerk
      if (isClerkEnabled && isSignedIn && signOut) {
        await signOut();
      }
      
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  };

  const updateUserProfile = async (profileData) => {
    try {
      const updatedUser = await authAPI.updateProfile(profileData);
      setUser(prevUser => ({ ...prevUser, ...updatedUser }));
      return { success: true, user: updatedUser };
    } catch (error) {
      console.error('Profile update error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Profile update failed' 
      };
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateUserProfile,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};