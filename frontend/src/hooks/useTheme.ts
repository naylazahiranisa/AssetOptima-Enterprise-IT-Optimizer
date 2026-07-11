"use client";

import { useTheme as useNextTheme } from "next-themes";
import { useCallback } from "react";

export function useTheme() {
  const { theme, setTheme, systemTheme } = useNextTheme();

  const toggle = useCallback(() => {
    setTheme(theme === "dark" ? "light" : "dark");
  }, [theme, setTheme]);

  const isDark =
    theme === "dark" || (theme === "system" && systemTheme === "dark");

  return {
    mode: theme as "light" | "dark" | "system",
    toggle,
    isDark,
    setTheme,
  };
}
