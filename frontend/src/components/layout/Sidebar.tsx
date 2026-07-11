"use client";

import { useCallback } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Monitor,
  Package,
  Bot,
  BarChart3,
  Settings,
  LogOut,
  X,
  HardDrive,
  Key,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  isCollapsed: boolean;
  onCollapse: () => void;
}

interface NavItem {
  label: string;
  href: string;
  icon: typeof LayoutDashboard;
}

const navItems: NavItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Assets", href: "/assets", icon: Monitor },
  { label: "Software", href: "/software", icon: Package },
  { label: "Licenses", href: "/licenses", icon: Key },
  { label: "AI Assistant", href: "/ai-assistant", icon: Bot },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar({
  isOpen,
  onToggle,
  isCollapsed,
  onCollapse,
}: SidebarProps) {
  const pathname = usePathname();
  const { logout, user } = useAuth();

  const handleLogout = useCallback(async () => {
    await logout();
  }, [logout]);

  const sidebarContent = (
    <div
      className={cn(
        "bg-card border-border flex h-full flex-col border-r transition-all duration-300",
        isCollapsed ? "w-16" : "w-60",
      )}
    >
      {/* Logo */}
      <div
        className={cn(
          "border-border flex h-16 items-center border-b px-4",
          isCollapsed ? "justify-center" : "justify-between",
        )}
      >
        {isCollapsed ? (
          <div className="bg-primary text-primary-foreground flex h-8 w-8 items-center justify-center rounded-lg">
            <HardDrive size={16} />
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <div className="bg-primary text-primary-foreground flex h-8 w-8 items-center justify-center rounded-lg">
              <HardDrive size={16} />
            </div>
            <div>
              <span className="text-foreground text-sm font-semibold">
                AssetOptima
              </span>
              <p className="text-muted-foreground text-[10px] leading-tight">
                Command Center
              </p>
            </div>
          </div>
        )}
        {/* Mobile close */}
        <button
          onClick={onToggle}
          className="text-muted-foreground hover:bg-muted rounded-md p-1 lg:hidden"
          aria-label="Close sidebar"
        >
          <X size={16} />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => {
                if (window.innerWidth < 1024) onToggle();
              }}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
                isCollapsed && "justify-center px-2",
              )}
              title={isCollapsed ? item.label : undefined}
            >
              <Icon size={18} strokeWidth={isActive ? 2.5 : 1.5} />
              {!isCollapsed && <span>{item.label}</span>}
              {isActive && !isCollapsed && (
                <span className="bg-primary ml-auto h-1.5 w-1.5 rounded-full" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="border-border border-t p-3">
        {!isCollapsed && user && (
          <div className="mb-3 flex items-center gap-3 rounded-lg px-3 py-2">
            <div className="bg-primary/10 text-primary flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium">
              {user.full_name
                ? user.full_name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .toUpperCase()
                    .slice(0, 2)
                : "U"}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-foreground truncate text-sm font-medium">
                {user.full_name ?? "User"}
              </p>
              <p className="text-muted-foreground truncate text-xs">
                {user.role
                  ?.replace("_", " ")
                  .replace(/\b\w/g, (c) => c.toUpperCase())}
              </p>
            </div>
          </div>
        )}
        <div className="space-y-1">
          {!isCollapsed && (
            <Button
              variant="ghost"
              size="sm"
              className="text-muted-foreground w-full justify-start gap-3"
              onClick={handleLogout}
            >
              <LogOut size={16} />
              Sign Out
            </Button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden h-full shrink-0 lg:block">
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            className="bg-foreground/20 absolute inset-0 backdrop-blur-sm"
            onClick={onToggle}
            aria-hidden="true"
          />
          <aside className="shadow-elevated absolute top-0 left-0 h-full w-60">
            {sidebarContent}
          </aside>
        </div>
      )}
    </>
  );
}
