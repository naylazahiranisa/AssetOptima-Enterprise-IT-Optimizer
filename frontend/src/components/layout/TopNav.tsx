"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Bell,
  Sun,
  Moon,
  LogOut,
  User,
  Menu,
  X,
  CheckCheck,
  AlertCircle,
  Info,
  AlertTriangle,
} from "lucide-react";
import { useTheme } from "@/hooks/useTheme";
import { useAuth } from "@/hooks/useAuth";
import { useNotificationStore } from "@/store/notificationStore";
import { cn, getInitials } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Avatar } from "@/components/ui/avatar";
import api from "@/services/api";
import type { NotificationItem } from "@/types/api";

interface TopNavProps {
  onMenuToggle: () => void;
}

export function TopNav({ onMenuToggle }: TopNavProps) {
  const router = useRouter();
  const { isDark, toggle } = useTheme();
  const { user, logout } = useAuth();
  const notifications = useNotificationStore((s) => s.notifications);
  const unreadCount = useNotificationStore((s) => s.unreadCount);
  const isOpen = useNotificationStore((s) => s.isOpen);
  const setIsOpen = useNotificationStore((s) => s.setIsOpen);
  const setNotifications = useNotificationStore((s) => s.setNotifications);
  const markAsRead = useNotificationStore((s) => s.markAsRead);
  const markAllAsRead = useNotificationStore((s) => s.markAllAsRead);

  const [searchQuery, setSearchQuery] = useState("");
  const [searchFocused, setSearchFocused] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [notiLoading, setNotiLoading] = useState(false);
  const profileRef = useRef<HTMLDivElement>(null);
  const notiRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Close profile on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        profileRef.current &&
        !profileRef.current.contains(event.target as Node)
      ) {
        setProfileOpen(false);
      }
      if (
        notiRef.current &&
        !notiRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [setIsOpen]);

  // Cmd+K shortcut
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      if (e.key === "Escape") {
        setIsOpen(false);
        setSearchFocused(false);
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [setIsOpen]);

  const fetchNotifications = useCallback(async () => {
    setNotiLoading(true);
    try {
      const res = await api.get("/api/v1/notifications");
      const items = (res.data as any).data ?? [];
      const mapped: NotificationItem[] = (Array.isArray(items) ? items : []).map(
        (n: any) => ({
          id: n.id,
          title: n.title ?? "Notification",
          message: n.message ?? "",
          category: n.category ?? "system",
          priority: n.priority ?? "medium",
          status: n.status ?? "unread",
          created_at: n.created_at ?? new Date().toISOString(),
        }),
      );
      setNotifications(mapped);
    } catch {
      // silently fail — notifications are non-critical
    } finally {
      setNotiLoading(false);
    }
  }, [setNotifications]);

  const handleNotificationToggle = useCallback(() => {
    const next = !isOpen;
    setIsOpen(next);
    if (next && notifications.length === 0) {
      fetchNotifications();
    }
  }, [isOpen, setIsOpen, notifications.length, fetchNotifications]);

  const handleSearch = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (searchQuery.trim()) {
        router.push(`/assets?search=${encodeURIComponent(searchQuery.trim())}`);
        setSearchQuery("");
        setSearchFocused(false);
        searchInputRef.current?.blur();
      }
    },
    [searchQuery, router],
  );

  const handleLogout = async () => {
    setProfileOpen(false);
    await logout();
  };

  const displayName = user?.full_name ?? "User";
  const displayEmail = user?.email ?? "user@assetoptima.com";
  const initials = getInitials(displayName);
  const roleLabel =
    user?.role === "super_admin"
      ? "Super Admin"
      : user?.role === "it_manager"
        ? "IT Manager"
        : user?.role === "it_support"
          ? "IT Support"
          : "User";

  const priorityIcon = (p: string) => {
    switch (p) {
      case "high":
        return <AlertCircle size={14} className="text-danger" />;
      case "medium":
        return <AlertTriangle size={14} className="text-warning" />;
      default:
        return <Info size={14} className="text-info" />;
    }
  };

  const timeAgo = (dateStr: string) => {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  };

  return (
    <header className="border-border bg-card flex h-16 items-center justify-between border-b px-4 lg:px-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuToggle}
          className="lg:hidden"
          aria-label="Toggle navigation menu"
        >
          <Menu size={20} />
        </Button>

        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="hidden sm:block">
          <ol className="text-muted-foreground flex items-center gap-2 text-sm">
            <li className="flex items-center gap-2">
              <span className="text-foreground font-medium">Pages</span>
              <span className="text-muted-foreground/40">/</span>
            </li>
          </ol>
        </nav>

        {/* Search */}
        <form onSubmit={handleSearch} className="relative hidden md:block">
          <Search
            size={16}
            className="text-muted-foreground/50 pointer-events-none absolute top-1/2 left-3 -translate-y-1/2"
            aria-hidden="true"
          />
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search assets, software..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setTimeout(() => setSearchFocused(false), 200)}
            aria-label="Search"
            className={cn(
              "border-border bg-muted/50 text-foreground placeholder-muted-foreground/50 h-9 w-64 rounded-lg border px-9 text-sm outline-none",
              "transition-all duration-200",
              "focus:border-primary/50 focus:bg-card focus:ring-primary/20 focus:w-80 focus:ring-1",
            )}
          />
          <kbd className="border-border bg-card text-muted-foreground/60 pointer-events-none absolute top-1/2 right-3 hidden -translate-y-1/2 items-center gap-0.5 rounded border px-1.5 py-0.5 text-[10px] font-medium sm:flex">
            ⌘K
          </kbd>
          {searchFocused && searchQuery.length > 0 && (
            <div className="border-border bg-card shadow-modal absolute top-full left-0 z-50 mt-1 w-80 rounded-lg border p-3">
              <p className="text-muted-foreground text-xs">
                Press <kbd className="bg-muted rounded px-1 py-0.5 text-[10px]">Enter</kbd> to search &quot;{searchQuery}&quot; in Assets
              </p>
            </div>
          )}
        </form>
      </div>

      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggle}
          aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
          className="text-muted-foreground"
        >
          {isDark ? <Sun size={18} /> : <Moon size={18} />}
        </Button>

        {/* Notification bell + panel */}
        <div className="relative" ref={notiRef}>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleNotificationToggle}
            className="text-muted-foreground relative"
            aria-label={`Notifications${unreadCount > 0 ? `, ${unreadCount} unread` : ""}`}
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span className="bg-danger text-danger-foreground absolute top-1.5 right-1.5 flex h-4 min-w-[16px] items-center justify-center rounded-full px-1 text-[10px] font-bold">
                {unreadCount > 99 ? "99+" : unreadCount}
              </span>
            )}
          </Button>

          {isOpen && (
            <div className="border-border bg-card shadow-modal absolute top-full right-0 z-50 mt-2 w-80 overflow-hidden rounded-xl border">
              <div className="border-border flex items-center justify-between border-b px-4 py-3">
                <p className="text-foreground text-sm font-semibold">
                  Notifications
                </p>
                <div className="flex items-center gap-1">
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="text-primary hover:text-primary/80 text-xs"
                    >
                      <CheckCheck size={14} />
                    </button>
                  )}
                  <button
                    onClick={() => setIsOpen(false)}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <X size={14} />
                  </button>
                </div>
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notiLoading && notifications.length === 0 ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="border-muted-foreground/30 border-t-primary h-5 w-5 animate-spin rounded-full border-2" />
                  </div>
                ) : notifications.length === 0 ? (
                  <div className="py-8 text-center">
                    <Bell size={20} className="text-muted-foreground/30 mx-auto mb-2" />
                    <p className="text-muted-foreground text-xs">No notifications</p>
                  </div>
                ) : (
                  notifications.slice(0, 10).map((n) => (
                    <button
                      key={n.id}
                      onClick={() => {
                        if (n.status === "unread") markAsRead(n.id);
                      }}
                      className={cn(
                        "border-border flex w-full items-start gap-3 border-b px-4 py-3 text-left transition-colors hover:bg-muted/50 last:border-b-0",
                        n.status === "unread" && "bg-primary/5",
                      )}
                    >
                      <div className="mt-0.5 shrink-0">{priorityIcon(n.priority)}</div>
                      <div className="min-w-0 flex-1">
                        <p className="text-foreground truncate text-xs font-medium">
                          {n.title}
                        </p>
                        <p className="text-muted-foreground mt-0.5 line-clamp-2 text-[11px]">
                          {n.message}
                        </p>
                        <p className="text-muted-foreground/60 mt-1 text-[10px]">
                          {timeAgo(n.created_at)}
                        </p>
                      </div>
                      {n.status === "unread" && (
                        <div className="bg-primary mt-1.5 h-2 w-2 shrink-0 rounded-full" />
                      )}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="relative" ref={profileRef}>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setProfileOpen(!profileOpen)}
            className="ml-2"
            aria-label="User profile menu"
            aria-expanded={profileOpen}
            aria-haspopup="true"
          >
            <Avatar size="sm" fallback={initials} />
          </Button>

          {profileOpen && (
            <div
              className="border-border bg-card shadow-modal absolute top-full right-0 mt-2 w-56 overflow-hidden rounded-xl border"
              role="menu"
            >
              <div className="border-border border-b px-4 py-3">
                <p className="text-foreground text-sm font-medium">
                  {displayName}
                </p>
                <p className="text-muted-foreground text-xs">{displayEmail}</p>
                <span className="bg-primary/10 text-primary mt-1.5 inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium">
                  {roleLabel}
                </span>
              </div>
              <div className="p-1">
                <button
                  onClick={() => {
                    setProfileOpen(false);
                    router.push("/profile");
                  }}
                  className="text-foreground hover:bg-muted flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors"
                  role="menuitem"
                >
                  <User size={16} className="text-muted-foreground" />
                  Profile
                </button>
                <button
                  onClick={() => {
                    setProfileOpen(false);
                    router.push("/settings");
                  }}
                  className="text-foreground hover:bg-muted flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors"
                  role="menuitem"
                >
                  <User size={16} className="text-muted-foreground" />
                  Settings
                </button>
              </div>
              <div className="border-border border-t p-1">
                <button
                  onClick={handleLogout}
                  className="text-danger hover:bg-danger/5 flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors"
                  role="menuitem"
                >
                  <LogOut size={16} />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
