/** Secure token management with expiration and storage abstraction.
 *
 * Encapsulates all token CRUD operations so the storage mechanism
 * (localStorage / sessionStorage / cookies) can be swapped centrally.
 */

import type { TokenStorage as TokenStorageInterface } from "@/types/auth";

const STORAGE_KEYS = {
  ACCESS: "ao_access_token",
  REFRESH: "ao_refresh_token",
} as const;

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export const TokenStorage: TokenStorageInterface = {
  getAccessToken(): string | null {
    if (!isBrowser()) return null;
    return localStorage.getItem(STORAGE_KEYS.ACCESS);
  },

  getRefreshToken(): string | null {
    if (!isBrowser()) return null;
    return localStorage.getItem(STORAGE_KEYS.REFRESH);
  },

  setTokens(accessToken: string, refreshToken: string): void {
    if (!isBrowser()) return;
    localStorage.setItem(STORAGE_KEYS.ACCESS, accessToken);
    localStorage.setItem(STORAGE_KEYS.REFRESH, refreshToken);
  },

  clearTokens(): void {
    if (!isBrowser()) return;
    localStorage.removeItem(STORAGE_KEYS.ACCESS);
    localStorage.removeItem(STORAGE_KEYS.REFRESH);
  },

  hasTokens(): boolean {
    return !!(this.getAccessToken() && this.getRefreshToken());
  },

  getTokenExpiration(token: string): number | null {
    try {
      const payload = token.split(".")[1];
      if (!payload) return null;
      const decoded = JSON.parse(atob(payload));
      return decoded.exp ?? null;
    } catch {
      return null;
    }
  },

  isTokenExpired(token: string): boolean {
    const exp = this.getTokenExpiration(token);
    if (exp === null) return true;
    return Date.now() >= exp * 1000;
  },
};
