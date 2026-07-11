"use client";

import { create } from "zustand";
import type { NotificationItem } from "@/types/api";

interface NotificationStore {
  notifications: NotificationItem[];
  unreadCount: number;
  isOpen: boolean;
  setNotifications: (notifications: NotificationItem[]) => void;
  addNotification: (notification: NotificationItem) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  setUnreadCount: (count: number) => void;
  setIsOpen: (isOpen: boolean) => void;
}

export const useNotificationStore = create<NotificationStore>((set) => ({
  notifications: [],
  unreadCount: 0,
  isOpen: false,

  setNotifications: (notifications: NotificationItem[]) =>
    set({
      notifications,
      unreadCount: notifications.filter((n) => n.status === "unread").length,
    }),

  addNotification: (notification: NotificationItem) =>
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount:
        notification.status === "unread"
          ? state.unreadCount + 1
          : state.unreadCount,
    })),

  markAsRead: (id: string) =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id && n.status === "unread"
          ? { ...n, status: "read" as const }
          : n,
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  markAllAsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.status === "unread" ? { ...n, status: "read" as const } : n,
      ),
      unreadCount: 0,
    })),

  setUnreadCount: (unreadCount: number) => set({ unreadCount }),

  setIsOpen: (isOpen: boolean) => set({ isOpen }),
}));
