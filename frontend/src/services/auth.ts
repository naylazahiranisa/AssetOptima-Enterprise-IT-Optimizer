/** Auth API service — proxies every auth-related backend endpoint. */

import api from "./api";
import type {
  LoginRequest,
  LoginResponse,
  RefreshResponse,
  UserProfile,
} from "@/types/auth";
import type { ApiResponse, PaginatedResponse } from "@/types/api";

export const authService = {
  /** Authenticate user credentials and receive JWT pair. */
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>("/api/v1/auth/login", data);
    return response.data;
  },

  /** Exchange a refresh token for a new JWT pair. */
  async refresh(refreshToken: string): Promise<RefreshResponse> {
    const response = await api.post<RefreshResponse>("/api/v1/auth/refresh", {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  /** Invalidate the current session on the server. */
  async logout(): Promise<void> {
    await api.post("/api/v1/auth/logout");
  },

  /** Fetch the authenticated user's profile. */
  async getMe(): Promise<UserProfile> {
    const response = await api.get<UserProfile>("/api/v1/auth/me");
    return response.data;
  },

  /** List all users (super_admin only). */
  async listUsers(
    page = 1,
    perPage = 20,
  ): Promise<ApiResponse<PaginatedResponse<UserProfile>>> {
    const response = await api.get<ApiResponse<PaginatedResponse<UserProfile>>>(
      "/api/v1/users",
      { params: { page, per_page: perPage } },
    );
    return response.data;
  },
};
