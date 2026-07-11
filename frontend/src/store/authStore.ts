"use client";

import { create } from "zustand";
import type { AuthState, LoginResponse, UserProfile } from "@/types/auth";

interface AuthActions {
  setAuth: (response: LoginResponse) => void;
  setUser: (user: UserProfile) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setInitialized: (initialized: boolean) => void;
  logout: () => void;
  updateTokens: (accessToken: string, refreshToken: string) => void;
}

export type AuthStore = AuthState & AuthActions;

const initialState: AuthState = {
  isAuthenticated: false,
  accessToken: null,
  refreshToken: null,
  user: null,
  role: null,
  isLoading: false,
  isInitialized: false,
  error: null,
};

export const useAuthStore = create<AuthStore>((set) => ({
  ...initialState,

  setAuth: (response: LoginResponse) =>
    set({
      isAuthenticated: true,
      accessToken: response.access_token,
      refreshToken: response.refresh_token,
      isLoading: false,
      error: null,
    }),

  setUser: (user: UserProfile) => set({ user, role: user.role }),

  setLoading: (isLoading: boolean) =>
    set({ isLoading, error: isLoading ? null : undefined }),

  setError: (error: string | null) => set({ error, isLoading: false }),

  setInitialized: (isInitialized: boolean) => set({ isInitialized }),

  logout: () =>
    set({
      ...initialState,
      isInitialized: true,
    }),

  updateTokens: (accessToken: string, refreshToken: string) =>
    set({ accessToken, refreshToken }),
}));
