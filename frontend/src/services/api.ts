/** Axios instance with JWT interceptors, 401 refresh, and unified error handling. */

import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import type { ApiError } from "@/types/api";
import type { AuthError } from "@/types/auth";
import { TokenStorage } from "@/features/auth/TokenStorage";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

/** Attach the current access token to every outgoing request. */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = TokenStorage.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error),
);

/** Handle 401 responses: attempt a single token refresh before failing. */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 403) {
      const forbidden: AuthError = {
        code: "FORBIDDEN",
        message: "You do not have permission to perform this action.",
      };
      return Promise.reject(forbidden);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = TokenStorage.getRefreshToken();
        if (!refreshToken) {
          throw new Error("No refresh token available");
        }

        if (TokenStorage.isTokenExpired(refreshToken)) {
          TokenStorage.clearTokens();
          redirectToLogin();
          const expired: AuthError = {
            code: "SESSION_EXPIRED",
            message: "Your session has expired. Please sign in again.",
          };
          return Promise.reject(expired);
        }

        const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token } = response.data;
        TokenStorage.setTokens(access_token, refresh_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch {
        TokenStorage.clearTokens();
        redirectToLogin();

        const expired: AuthError = {
          code: "SESSION_EXPIRED",
          message: "Your session has expired. Please sign in again.",
        };
        return Promise.reject(expired);
      }
    }

    return Promise.reject(error);
  },
);

function redirectToLogin(): void {
  if (typeof window !== "undefined") {
    const currentPath = window.location.pathname;
    if (currentPath !== "/login") {
      window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
    }
  }
}

/** Convert raw Axios / unknown errors into a user-friendly AuthError. */
export function handleApiError(error: unknown): AuthError {
  if ((error as AuthError)?.code) {
    return error as AuthError;
  }

  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return {
        code: "NETWORK_ERROR",
        message:
          "Unable to connect to the server. Please check your connection.",
      };
    }

    const status = error.response.status;
    const detail = (error.response.data as ApiError)?.detail;

    if (status === 401) {
      return {
        code: "INVALID_CREDENTIALS",
        message: detail ?? "Invalid email or password.",
      };
    }

    if (status === 403) {
      return {
        code: "FORBIDDEN",
        message: detail ?? "Access denied.",
      };
    }

    if (status >= 500) {
      return {
        code: "SERVER_ERROR",
        message: detail ?? "A server error occurred. Please try again later.",
      };
    }

    return {
      code: "UNKNOWN",
      message: detail ?? error.message,
    };
  }

  if (error instanceof Error) {
    return {
      code: "UNKNOWN",
      message: error.message,
    };
  }

  return {
    code: "UNKNOWN",
    message: "An unexpected error occurred.",
  };
}

export default api;
