"use client";

import { useCallback } from "react";
import { useNotificationStore } from "@/store/notificationStore";

export function useNotifications() {
  const {
    notifications,
    unreadCount,
    isOpen,
    addNotification,
    markAsRead,
    markAllAsRead,
    setUnreadCount,
    setIsOpen,
  } = useNotificationStore();

  const fetchNotifications = useCallback(async () => {
    /* Implement API call when backend connected */
  }, []);

  const togglePanel = useCallback(() => {
    setIsOpen(!isOpen);
  }, [isOpen, setIsOpen]);

  return {
    notifications,
    unreadCount,
    isOpen,
    fetchNotifications,
    addNotification,
    markAsRead,
    markAllAsRead,
    setUnreadCount,
    togglePanel,
  };
}
