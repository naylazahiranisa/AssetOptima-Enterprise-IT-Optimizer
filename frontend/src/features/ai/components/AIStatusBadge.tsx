"use client";

import { cn } from "@/lib/utils";

interface AIStatusBadgeProps {
  status: "connected" | "connecting" | "disconnected" | "error";
  className?: string;
}

const statusConfig: Record<string, { label: string; dotClass: string }> = {
  connected: { label: "Connected", dotClass: "bg-success" },
  connecting: { label: "Connecting...", dotClass: "bg-warning animate-pulse" },
  disconnected: { label: "Disconnected", dotClass: "bg-muted-foreground" },
  error: { label: "Connection Error", dotClass: "bg-danger" },
};

/** Status badge showing AI service connection state */
export function AIStatusBadge({ status, className }: AIStatusBadgeProps) {
  const config = statusConfig[status];
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-medium",
        status === "connected" && "bg-success/10 text-success",
        status === "connecting" && "bg-warning/10 text-warning",
        status === "disconnected" && "bg-muted text-muted-foreground",
        status === "error" && "bg-danger/10 text-danger",
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", config.dotClass)} />
      {config.label}
    </div>
  );
}
