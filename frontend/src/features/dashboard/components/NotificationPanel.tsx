"use client";

import { motion } from "framer-motion";
import {
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCheck,
  type LucideIcon,
} from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Bell, BellDot } from "lucide-react";
import { formatDate, cn } from "@/lib/utils";
import type { DashboardNotification } from "@/features/dashboard/types/dashboard";

interface NotificationPanelProps {
  data?: DashboardNotification[];
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
}

const priorityConfig: Record<
  string,
  {
    icon: LucideIcon;
    badgeVariant: "danger" | "warning" | "default" | "primary";
    borderColor: string;
  }
> = {
  critical: {
    icon: AlertTriangle,
    badgeVariant: "danger",
    borderColor: "border-l-danger",
  },
  high: {
    icon: AlertCircle,
    badgeVariant: "warning",
    borderColor: "border-l-warning",
  },
  medium: {
    icon: Info,
    badgeVariant: "default",
    borderColor: "border-l-primary",
  },
  low: {
    icon: Info,
    badgeVariant: "primary",
    borderColor: "border-l-muted-foreground",
  },
};

const priorityLabel: Record<string, string> = {
  critical: "Critical",
  high: "High",
  medium: "Medium",
  low: "Low",
};

export function NotificationPanel({
  data,
  isLoading,
  isError,
  onRetry,
}: NotificationPanelProps) {
  const unreadCount = data?.filter((n) => !n.read).length ?? 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.3 }}
    >
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CardTitle>Notifications</CardTitle>
              {unreadCount > 0 && (
                <Badge variant="danger" className="h-5 px-1.5 text-xs">
                  {unreadCount}
                </Badge>
              )}
            </div>
            {unreadCount > 0 && (
              <Button variant="ghost" size="sm" className="h-7 gap-1 text-xs">
                <CheckCheck size={12} />
                Mark all read
              </Button>
            )}
          </div>
          <CardDescription>System alerts and reminders</CardDescription>
        </CardHeader>
        <CardContent className="pb-2">
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="space-y-2 rounded-lg border p-3">
                  <div className="flex items-center justify-between">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-14 rounded-full" />
                  </div>
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-24" />
                </div>
              ))}
            </div>
          ) : isError ? (
            <ErrorState
              title="Failed to load notifications"
              message="Could not retrieve system notifications."
              onRetry={onRetry}
            />
          ) : !data || data.length === 0 ? (
            <EmptyState
              icon={<Bell size={40} strokeWidth={1.5} />}
              title="No notifications"
              description="You're all caught up. Notifications will appear here."
            />
          ) : (
            <div className="space-y-2">
              {data.map((notification, i) => {
                const config =
                  priorityConfig[notification.priority] || priorityConfig.low;
                const Icon = config.icon;
                return (
                  <motion.div
                    key={notification.id}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: i * 0.03 }}
                    className={cn(
                      "border-border hover:bg-muted/50 cursor-pointer rounded-lg border border-l-3 p-3 transition-colors",
                      config.borderColor,
                      !notification.read && "bg-muted/30",
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2.5">
                        <Icon
                          size={14}
                          className={cn(
                            "mt-0.5 shrink-0",
                            notification.priority === "critical" &&
                              "text-danger",
                            notification.priority === "high" && "text-warning",
                            notification.priority === "medium" &&
                              "text-primary",
                            notification.priority === "low" &&
                              "text-muted-foreground",
                          )}
                        />
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-foreground text-sm leading-tight font-medium">
                              {notification.title}
                            </p>
                            {!notification.read && (
                              <span className="bg-primary h-1.5 w-1.5 shrink-0 rounded-full" />
                            )}
                          </div>
                          <p className="text-muted-foreground mt-0.5 text-xs leading-tight">
                            {notification.message}
                          </p>
                          <p className="text-muted-foreground/50 mt-1 text-xs">
                            {formatDate(notification.timestamp)}
                          </p>
                        </div>
                      </div>
                      <Badge
                        variant={config.badgeVariant}
                        className="shrink-0 text-[10px] capitalize"
                      >
                        {priorityLabel[notification.priority]}
                      </Badge>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Button variant="ghost" size="sm" className="w-full text-xs">
            <BellDot size={14} />
            View all notifications
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
}
