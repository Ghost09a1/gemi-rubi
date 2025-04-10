import jwt from 'jsonwebtoken';
import { LoginRequest, RegisterRequest, AuthResponse, User, AuthError, TokenData } from '@/types/auth';

// For mock data - in a real app this would interact with a real API
import { mockUsers } from './mock/users';

// Mock JWT secret - in production this would be a proper secret key
const JWT_SECRET = 'roleplay-hub-jwt-secret-key';
const ACCESS_TOKEN_EXPIRY = 60 * 60; // 1 hour in seconds
const REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 * 60; // 7 days in seconds

class AuthService {
  private static instance: AuthService;
  private currentUser: User | null = null;

  private constructor() {}

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  /**
   * Login a user with username and password
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      // In a real app, this would be an API call
      const user = this.findUserByCredentials(credentials.username, credentials.password);

      if (!user) {
        throw { message: 'Invalid credentials', code: 'auth/invalid-credentials', status: 401 } as AuthError;
      }

      // Generate tokens
      const accessToken = this.generateToken(user, 'access');
      const refreshToken = this.generateToken(user, 'refresh');

      // Calculate expiry timestamp
      const expiresAt = Math.floor(Date.now() / 1000) + ACCESS_TOKEN_EXPIRY;

      // Set current user
      this.currentUser = user;

      // Store tokens based on rememberMe preference
      if (credentials.rememberMe) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        localStorage.setItem('token_expiry', expiresAt.toString());
      } else {
        sessionStorage.setItem('access_token', accessToken);
        sessionStorage.setItem('refresh_token', refreshToken);
        sessionStorage.setItem('token_expiry', expiresAt.toString());
      }

      return {
        user,
        access_token: accessToken,
        refresh_token: refreshToken,
        expires_at: expiresAt
      };
    } catch (error) {
      if ((error as AuthError).code) {
        throw error;
      }
      throw { message: 'Login failed', code: 'auth/unknown-error', status: 500 } as AuthError;
    }
  }

  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    try {
      // Check if user already exists (in real app this would be an API call)
      const existingUser = mockUsers.find(u =>
        u.username.toLowerCase() === data.username.toLowerCase() ||
        u.email.toLowerCase() === data.email.toLowerCase()
      );

      if (existingUser) {
        if (existingUser.username.toLowerCase() === data.username.toLowerCase()) {
          throw { message: 'Username already taken', code: 'auth/username-exists', status: 409 } as AuthError;
        } else {
          throw { message: 'Email already in use', code: 'auth/email-exists', status: 409 } as AuthError;
        }
      }

      // Create new user (in real app this would be an API call)
      const newUser: User = {
        id: `user_${Date.now()}`,
        username: data.username,
        email: data.email,
        avatar: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        is_verified: false,
        timezone: data.timezone_offset || 'UTC',
        last_login: new Date().toISOString()
      };

      // In a real app, we would add the user to the database
      // For now, we'll just pretend it worked

      // Generate tokens
      const accessToken = this.generateToken(newUser, 'access');
      const refreshToken = this.generateToken(newUser, 'refresh');

      // Calculate expiry timestamp
      const expiresAt = Math.floor(Date.now() / 1000) + ACCESS_TOKEN_EXPIRY;

      // Set current user
      this.currentUser = newUser;

      // Store tokens in localStorage by default for new registrations
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      localStorage.setItem('token_expiry', expiresAt.toString());

      return {
        user: newUser,
        access_token: accessToken,
        refresh_token: refreshToken,
        expires_at: expiresAt
      };
    } catch (error) {
      if ((error as AuthError).code) {
        throw error;
      }
      throw { message: 'Registration failed', code: 'auth/unknown-error', status: 500 } as AuthError;
    }
  }

  /**
   * Logout the current user
   */
  logout(): void {
    // Clear tokens from storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token_expiry');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('token_expiry');

    this.currentUser = null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;

    try {
      // Verify token
      const decoded = jwt.verify(token, JWT_SECRET) as TokenData;
      const currentTime = Math.floor(Date.now() / 1000);

      // Check if token is expired
      if (decoded.exp <= currentTime) {
        // Try to refresh token
        this.refreshToken();
        // Check again after refresh attempt
        return !!this.getAccessToken();
      }

      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get the current user
   */
  async getCurrentUser(): Promise<User | null> {
    if (this.currentUser) {
      return this.currentUser;
    }

    // Try to get user from token
    try {
      const token = this.getAccessToken();
      if (!token) return null;

      const decoded = jwt.verify(token, JWT_SECRET) as TokenData;

      // In a real app, this would be an API call to get the full user data
      const user = mockUsers.find(u => u.id === decoded.userId);

      if (user) {
        this.currentUser = user;
        return user;
      }

      return null;
    } catch (error) {
      return null;
    }
  }

  /**
   * Refresh the access token using the refresh token
   */
  async refreshToken(): Promise<AuthResponse | null> {
    try {
      const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');

      if (!refreshToken) {
        return null;
      }

      // Verify refresh token
      const decoded = jwt.verify(refreshToken, JWT_SECRET) as TokenData;

      // In a real app, this would be an API call to validate and get a new token
      const user = mockUsers.find(u => u.id === decoded.userId);

      if (!user) {
        throw { message: 'Invalid refresh token', code: 'auth/invalid-token', status: 401 } as AuthError;
      }

      // Generate new tokens
      const accessToken = this.generateToken(user, 'access');
      const refreshToken2 = this.generateToken(user, 'refresh');

      // Calculate expiry timestamp
      const expiresAt = Math.floor(Date.now() / 1000) + ACCESS_TOKEN_EXPIRY;

      // Store new tokens (in the same storage that had the refresh token)
      if (localStorage.getItem('refresh_token')) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken2);
        localStorage.setItem('token_expiry', expiresAt.toString());
      } else {
        sessionStorage.setItem('access_token', accessToken);
        sessionStorage.setItem('refresh_token', refreshToken2);
        sessionStorage.setItem('token_expiry', expiresAt.toString());
      }

      // Set current user
      this.currentUser = user;

      return {
        user,
        access_token: accessToken,
        refresh_token: refreshToken2,
        expires_at: expiresAt
      };
    } catch (error) {
      // If refresh token is invalid, logout
      this.logout();
      return null;
    }
  }

  // Private helper methods

  /**
   * Get the current access token from storage
   */
  private getAccessToken(): string | null {
    return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  }

  /**
   * Generate a JWT token
   */
  private generateToken(user: User, type: 'access' | 'refresh'): string {
    const payload: TokenData = {
      userId: user.id,
      username: user.username,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (type === 'access' ? ACCESS_TOKEN_EXPIRY : REFRESH_TOKEN_EXPIRY)
    };

    return jwt.sign(payload, JWT_SECRET);
  }

  /**
   * Find a user by username and password
   */
  private findUserByCredentials(username: string, password: string): User | null {
    // In a real app, this would validate the password against a hash
    // For the demo, we're just checking the raw values
    const user = mockUsers.find(u =>
      u.username.toLowerCase() === username.toLowerCase() &&
      password === 'password' // Mock check - in real app would use bcrypt.compare
    );

    return user || null;
  }
}

// Export a singleton instance
export const authService = AuthService.getInstance();
