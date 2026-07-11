"use client";

import { motion } from "framer-motion";
import {
  Monitor,
  QrCode,
  RefreshCw,
  Wrench,
  LogIn,
  type LucideIcon,
} from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Clock, Activity } from "lucide-react";
import { formatDate, cn } from "@/lib/utils";
import type {
  ActivityItem,
  ActivityType,
} from "@/features/dashboard/types/dashboard";

const activityIconMap: Record<ActivityType, LucideIcon> = {
  asset_assigned: Monitor,
  qr_scan: QrCode,
  license_renewed: RefreshCw,
  maintenance: Wrench,
  employee_login: LogIn,
};

const activityColorMap: Record<ActivityType, string> = {
  asset_assigned: "text-primary",
  qr_scan: "text-success",
  license_renewed: "text-warning",
  maintenance: "text-ai",
  employee_login: "text-muted-foreground",
};

const activityBgMap: Record<ActivityType, string> = {
  asset_assigned: "bg-primary/10",
  qr_scan: "bg-success/10",
  license_renewed: "bg-warning/10",
  maintenance: "bg-ai/10",
  employee_login: "bg-muted",
};

interface ActivityTimelineProps {
  data?: ActivityItem[];
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
}

export function ActivityTimeline({
  data,
  isLoading,
  isError,
  onRetry,
}: ActivityTimelineProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.25 }}
    >
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest system events</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex gap-3">
                  <Skeleton className="h-8 w-8 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-3 w-64" />
                  </div>
                </div>
              ))}
            </div>
          ) : isError ? (
            <ErrorState
              title="Failed to load activity"
              message="Could not retrieve recent activity feed."
              onRetry={onRetry}
            />
          ) : !data || data.length === 0 ? (
            <EmptyState
              icon={<Activity size={40} strokeWidth={1.5} />}
              title="No recent activity"
              description="System activity will appear here as events occur."
            />
          ) : (
            <div className="relative space-y-0">
              <div className="bg-border absolute top-2 left-4 h-[calc(100%-16px)] w-px" />
              {data.map((item, i) => {
                const Icon = activityIconMap[item.type] || Clock;
                return (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.2, delay: i * 0.05 }}
                    className="relative flex gap-4 pb-5 last:pb-0"
                  >
                    <div
                      className={cn(
                        "relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                        activityBgMap[item.type],
                      )}
                    >
                      <Icon
                        size={14}
                        className={cn("shrink-0", activityColorMap[item.type])}
                      />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-foreground text-sm leading-tight font-medium">
                        {item.title}
                      </p>
                      <p className="text-muted-foreground mt-0.5 text-xs leading-tight">
                        {item.description}
                      </p>
                      <p className="text-muted-foreground/60 mt-1 text-xs">
                        {formatDate(item.timestamp)}
                      </p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
