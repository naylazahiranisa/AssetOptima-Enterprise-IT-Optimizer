/** Authentication domain types */

export type UserRole = "super_admin" | "it_manager" | "it_support";

export interface AuthState {
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  role: UserRole | null;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  department?: string;
  avatar_url?: string;
  is_active: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface RefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TokenPayload {
  sub: string;
  exp: number;
  role: string;
  iat?: number;
}

export interface TokenStorage {
  getAccessToken(): string | null;
  getRefreshToken(): string | null;
  setTokens(accessToken: string, refreshToken: string): void;
  clearTokens(): void;
  hasTokens(): boolean;
  getTokenExpiration(token: string): number | null;
  isTokenExpired(token: string): boolean;
}

export type AuthErrorCode =
  | "INVALID_CREDENTIALS"
  | "SERVER_ERROR"
  | "NETWORK_ERROR"
  | "SESSION_EXPIRED"
  | "UNAUTHORIZED"
  | "FORBIDDEN"
  | "UNKNOWN";

export interface AuthError {
  code: AuthErrorCode;
  message: string;
}
