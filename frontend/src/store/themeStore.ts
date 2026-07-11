"use client";

import { create } from "zustand";

interface ThemeStore {
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

export const useThemeStore = create<ThemeStore>((set) => ({
  sidebarCollapsed: false,
  setSidebarCollapsed: (sidebarCollapsed: boolean) => set({ sidebarCollapsed }),
}));
