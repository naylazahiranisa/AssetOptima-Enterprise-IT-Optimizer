"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import { authService } from "@/services/auth";
import { handleApiError } from "@/services/api";
import { TokenStorage } from "@/features/auth/TokenStorage";
import {
  hasPermission,
  getFallbackRoute,
  type Permission,
} from "@/features/auth/rbac";
import type { UserProfile, UserRole } from "@/types/auth";

const PROFILE_CACHE_KEY = "ao_profile";

function setCachedProfile(profile: UserProfile): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(PROFILE_CACHE_KEY, JSON.stringify(profile));
  } catch { /* quota */ }
}

function clearCachedProfile(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(PROFILE_CACHE_KEY);
}

export function useAuth() {
  const router = useRouter();
  const store = useAuthStore();
  const { setProfile, clearProfile } = useProfileStore();

  const login = useCallback(
    async (email: string, password: string): Promise<boolean> => {
      store.setLoading(true);
      store.setError(null);

      try {
        const response = await authService.login({ email, password });
        TokenStorage.setTokens(response.access_token, response.refresh_token);
        store.setAuth(response);

        const profile = await authService.getMe();
        store.setUser(profile);
        setProfile(profile);
        setCachedProfile(profile);

        return true;
      } catch (err) {
        const authError = handleApiError(err);
        store.setError(authError.message);
        return false;
      }
    },
    [store, setProfile],
  );

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch { /* best-effort */ }
    TokenStorage.clearTokens();
    clearCachedProfile();
    clearProfile();
    store.logout();
    router.replace("/login");
  }, [store, clearProfile, router]);

  const can = useCallback(
    (permission: Permission): boolean => hasPermission(store.role, permission),
    [store.role],
  );

  const fallbackRoute = getFallbackRoute(store.role);

  return {
    user: store.user,
    role: store.role as UserRole | null,
    isAuthenticated: store.isAuthenticated,
    isInitialized: store.isInitialized,
    isLoading: store.isLoading,
    error: store.error,
    login,
    logout,
    can,
    fallbackRoute,
  };
}
