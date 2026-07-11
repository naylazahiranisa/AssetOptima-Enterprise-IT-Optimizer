"use client";

import { motion } from "framer-motion";
import {
  Monitor,
  Package,
  Key,
  Users,
  DollarSign,
  AlertTriangle,
  type LucideIcon,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import type { DashboardKpi } from "@/features/dashboard/types/dashboard";

const iconMap: Record<string, LucideIcon> = {
  Monitor,
  Package,
  Key,
  Users,
  DollarSign,
  AlertTriangle,
};

interface StatCardProps {
  data?: DashboardKpi;
  isLoading?: boolean;
  index?: number;
}

export function StatCard({ data, isLoading, index = 0 }: StatCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="space-y-3 p-6">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-3 w-28" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const Icon = iconMap[data.icon] || Monitor;
  const trendColors: Record<string, string> = {
    up: "text-success",
    down: "text-danger",
    neutral: "text-muted-foreground",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
    >
      <Card className="group hover:shadow-elevated transition-shadow duration-200">
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <p className="text-muted-foreground text-sm">{data.label}</p>
              <p className="text-foreground text-2xl font-semibold tracking-tight">
                {data.value}
              </p>
            </div>
            <div className="bg-primary/10 text-primary rounded-lg p-2.5">
              <Icon size={18} />
            </div>
          </div>
          {data.trend && (
            <p
              className={cn("mt-3 text-xs", trendColors[data.trend.direction])}
            >
              {data.trend.direction === "up" && "↑ "}
              {data.trend.direction === "down" && "↓ "}
              {data.trend.value}
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
