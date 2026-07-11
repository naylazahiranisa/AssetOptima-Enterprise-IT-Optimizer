"use client";

import { type ReactNode, useEffect, useRef } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Loader2, HardDrive } from "lucide-react";
import { useAuthStore } from "@/store/authStore";
import { useProfileStore } from "@/store/profileStore";
import type { UserProfile } from "@/types/auth";
import { TokenStorage } from "./TokenStorage";
import { canAccessRoute } from "./rbac";

interface AuthGuardProps {
  children: ReactNode;
  requiredRole?: string;
}

const PUBLIC_ROUTES = ["/login", "/403", "/404"];

const PROFILE_CACHE_KEY = "ao_profile";

function getCachedProfile(): UserProfile | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(PROFILE_CACHE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function setCachedProfile(profile: UserProfile): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(PROFILE_CACHE_KEY, JSON.stringify(profile));
  } catch { /* quota */ }
}

function LoadingScreen() {
  return (
    <div className="bg-background flex h-screen flex-col items-center justify-center">
      <div className="bg-primary flex h-12 w-12 items-center justify-center rounded-xl shadow-sm">
        <HardDrive size={24} className="text-primary-foreground" />
      </div>
      <Loader2 size={20} className="text-primary mt-4 animate-spin" />
      <p className="text-muted-foreground mt-3 text-sm">
        Loading AssetOptima...
      </p>
    </div>
  );
}

function fetchProfile(store: ReturnType<typeof useAuthStore.getState>, setProfile: (p: UserProfile) => void) {
  import("@/services/auth").then(({ authService }) => {
    authService.getMe().then((profile) => {
      store.setUser(profile);
      setProfile(profile);
      setCachedProfile(profile);
    }).catch(() => {
      localStorage.removeItem(PROFILE_CACHE_KEY);
    });
  });
}

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const store = useAuthStore();
  const { setProfile } = useProfileStore();
  const { isAuthenticated, role, isInitialized } = store;
  const redirected = useRef(false);

  useEffect(() => {
    if (store.isInitialized) return;

    const init = async () => {
      const hasTokens = TokenStorage.hasTokens();

      if (!hasTokens) {
        store.setInitialized(true);
        return;
      }

      const accessToken = TokenStorage.getAccessToken()!;
      const refreshToken = TokenStorage.getRefreshToken()!;

      if (TokenStorage.isTokenExpired(accessToken)) {
        if (TokenStorage.isTokenExpired(refreshToken)) {
          TokenStorage.clearTokens();
          store.setInitialized(true);
          return;
        }

        try {
          const { authService } = await import("@/services/auth");
          const refreshed = await authService.refresh(refreshToken);
          TokenStorage.setTokens(refreshed.access_token, refreshed.refresh_token);
          store.setAuth(refreshed);
          store.setInitialized(true);
          fetchProfile(store, setProfile);
          return;
        } catch {
          TokenStorage.clearTokens();
          store.setInitialized(true);
          return;
        }
      }

      store.setAuth({
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: "bearer",
      });
      store.setInitialized(true);

      const cached = getCachedProfile();
      if (cached) {
        store.setUser(cached);
        setProfile(cached);
      }
      fetchProfile(store, setProfile);
    };

    init();
  }, []);

  useEffect(() => {
    if (redirected.current || !isInitialized) return;
    redirected.current = true;

    const isPublic = PUBLIC_ROUTES.includes(pathname);

    if (!isPublic) {
      const hasTokens = TokenStorage.hasTokens();
      if (!hasTokens) {
        router.replace("/login");
        return;
      }

      if (!isAuthenticated && hasTokens) {
        router.replace("/loading");
        return;
      }

      if (role && !canAccessRoute(role, pathname)) {
        router.replace("/403");
        return;
      }
    }

    if (pathname === "/login" && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [pathname, router, isInitialized, isAuthenticated, role]);

  if (!isInitialized) {
    return <LoadingScreen />;
  }

  const isPublic = PUBLIC_ROUTES.includes(pathname);

  if (isPublic) {
    return <>{children}</>;
  }

  if (!isAuthenticated) {
    return null;
  }

  if (role && !canAccessRoute(role, pathname)) {
    return null;
  }

  return <>{children}</>;
}
