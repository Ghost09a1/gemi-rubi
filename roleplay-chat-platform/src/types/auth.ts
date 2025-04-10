export interface LoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  timezone_offset?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  expires_at: number; // Unix timestamp
}

export interface User {
  id: string;
  username: string;
  email: string;
  avatar?: string | null;
  created_at: string;
  updated_at: string;
  is_verified: boolean;
  is_admin?: boolean;
  timezone?: string;
  last_login?: string;
}

export interface TokenData {
  userId: string;
  username: string;
  exp: number; // Expiration timestamp
  iat: number; // Issued at timestamp
}

export interface AuthError {
  message: string;
  code?: string;
  status?: number;
}
