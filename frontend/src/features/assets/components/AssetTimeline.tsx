"use client";

import { motion } from "framer-motion";
import {
  Package,
  UserCheck,
  Undo2,
  ArrowRightLeft,
  Wrench,
  Archive,
  type LucideIcon,
} from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn, formatDate } from "@/lib/utils";
import { Activity, Clock } from "lucide-react";
import type {
  LifecycleEvent,
  LifecycleEventType,
} from "@/features/assets/types/assets";

const eventIconMap: Record<LifecycleEventType, LucideIcon> = {
  registered: Package,
  assigned: UserCheck,
  returned: Undo2,
  transferred: ArrowRightLeft,
  maintenance: Wrench,
  retired: Archive,
};

const eventColorMap: Record<LifecycleEventType, string> = {
  registered: "text-primary",
  assigned: "text-success",
  returned: "text-muted-foreground",
  transferred: "text-warning",
  maintenance: "text-ai",
  retired: "text-danger",
};

const eventBgMap: Record<LifecycleEventType, string> = {
  registered: "bg-primary/10",
  assigned: "bg-success/10",
  returned: "bg-muted",
  transferred: "bg-warning/10",
  maintenance: "bg-ai/10",
  retired: "bg-danger/10",
};

interface AssetTimelineProps {
  events?: LifecycleEvent[];
  isLoading?: boolean;
}

export function AssetTimeline({ events, isLoading }: AssetTimelineProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Asset Timeline</CardTitle>
        <CardDescription>Lifecycle events and history</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex gap-3">
                <Skeleton className="h-8 w-8 rounded-full" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-40" />
                  <Skeleton className="h-3 w-56" />
                </div>
              </div>
            ))}
          </div>
        ) : !events || events.length === 0 ? (
          <EmptyState
            icon={<Activity size={40} strokeWidth={1.5} />}
            title="No history yet"
            description="Asset lifecycle events will appear here."
          />
        ) : (
          <div className="relative space-y-0">
            <div className="bg-border absolute top-2 left-4 h-[calc(100%-16px)] w-px" />
            {events.map((event, i) => {
              const Icon = eventIconMap[event.event_type] || Clock;
              return (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: i * 0.04 }}
                  className="relative flex gap-4 pb-5 last:pb-0"
                >
                  <div
                    className={cn(
                      "relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                      eventBgMap[event.event_type],
                    )}
                  >
                    <Icon
                      size={14}
                      className={cn(
                        "shrink-0",
                        eventColorMap[event.event_type],
                      )}
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-foreground text-sm leading-tight font-medium">
                      {event.title}
                    </p>
                    <p className="text-muted-foreground mt-0.5 text-xs leading-tight">
                      {event.description}
                    </p>
                    <div className="text-muted-foreground/60 mt-1 flex items-center gap-2 text-xs">
                      <span>{formatDate(event.timestamp)}</span>
                      <span>·</span>
                      <span>{event.user}</span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
