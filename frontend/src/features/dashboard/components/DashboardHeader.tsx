"use client";

import { useMemo } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { RefreshCw, Download, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface DashboardHeaderProps {
  userName?: string;
  isLoading?: boolean;
  onRefresh?: () => void;
}

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

function formatDate(): string {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(new Date());
}

export function DashboardHeader({
  userName,
  isLoading,
  onRefresh,
}: DashboardHeaderProps) {
  const greeting = useMemo(() => getGreeting(), []);
  const dateStr = useMemo(() => formatDate(), []);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="space-y-2">
          <Skeleton className="h-8 w-72" />
          <Skeleton className="h-4 w-48" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-9 w-28 rounded-lg" />
          <Skeleton className="h-9 w-28 rounded-lg" />
          <Skeleton className="h-9 w-28 rounded-lg" />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="space-y-1">
        <h1 className="text-foreground text-2xl font-semibold tracking-tight">
          {greeting}
          {userName ? `, ${userName}` : ""}
        </h1>
        <p className="text-muted-foreground text-sm">{dateStr}</p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw size={14} />
          Refresh Data
        </Button>
        <Button variant="outline" size="sm" asChild>
          <Link href="/analytics">
            <Download size={14} />
            Export Report
          </Link>
        </Button>
        <Button variant="default" size="sm" asChild>
          <Link href="/assets/new">
            <PlusCircle size={14} />
            Quick Register
          </Link>
        </Button>
      </div>
    </motion.div>
  );
}
