'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { User, AuthError, LoginRequest, RegisterRequest } from '@/types/auth';
import { authService } from '@/services/auth.service';

// Define the context shape
type AuthContextType = {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  error: string | null;
  clearError: () => void;
};

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  error: null,
  clearError: () => {},
});

// Create a provider component
export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check auth state on component mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (authService.isAuthenticated()) {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        }
      } catch (err) {
        console.error('Auth error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (credentials: LoginRequest) => {
    setError(null);
    setIsLoading(true);

    try {
      const response = await authService.login(credentials);
      setUser(response.user);
      router.push('/dashboard');
    } catch (err) {
      setError((err as AuthError).message || 'Login failed. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Register function
  const register = async (data: RegisterRequest) => {
    setError(null);
    setIsLoading(true);

    try {
      const response = await authService.register(data);
      setUser(response.user);
      router.push('/onboarding');
    } catch (err) {
      setError((err as AuthError).message || 'Registration failed. Please try again.');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    authService.logout();
    setUser(null);
    router.push('/');
  };

  // Clear error
  const clearError = () => {
    setError(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        error,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => useContext(AuthContext);
