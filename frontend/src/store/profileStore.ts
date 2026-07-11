"use client";

import { create } from "zustand";
import type { UserProfile } from "@/types/auth";

interface ProfileState {
  profile: UserProfile | null;
}

interface ProfileActions {
  setProfile: (profile: UserProfile) => void;
  updateProfile: (
    updates: Partial<Omit<UserProfile, "id" | "created_at">>,
  ) => void;
  clearProfile: () => void;
}

export type ProfileStore = ProfileState & ProfileActions;

export const useProfileStore = create<ProfileStore>((set) => ({
  profile: null,

  setProfile: (profile: UserProfile) => set({ profile }),

  updateProfile: (updates) =>
    set((state) => ({
      profile: state.profile ? { ...state.profile, ...updates } : null,
    })),

  clearProfile: () => set({ profile: null }),
}));
