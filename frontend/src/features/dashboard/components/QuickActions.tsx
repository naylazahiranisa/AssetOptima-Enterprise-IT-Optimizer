"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import {
  PlusCircle,
  UserPlus,
  QrCode,
  Sparkles,
  Settings,
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
import { cn } from "@/lib/utils";
import type { QuickAction } from "@/features/dashboard/types/dashboard";

const iconMap: Record<string, LucideIcon> = {
  PlusCircle,
  UserPlus,
  QrCode,
  Sparkles,
  Settings,
};

interface QuickActionsProps {
  data?: QuickAction[];
  isLoading?: boolean;
}

export function QuickActions({ data, isLoading }: QuickActionsProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.35 }}
    >
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks and shortcuts</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="space-y-2 rounded-lg border p-4">
                  <Skeleton className="h-8 w-8 rounded-lg" />
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-3 w-16" />
                </div>
              ))}
            </div>
          ) : !data || data.length === 0 ? null : (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
              {data.map((action, i) => {
                const Icon = iconMap[action.icon] || Settings;
                return (
                  <motion.div
                    key={action.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.2, delay: i * 0.04 }}
                  >
                    <Link
                      href={action.href ?? "#"}
                      className={cn(
                        "border-border hover:border-primary/30 hover:bg-muted/50 group flex flex-col items-center gap-2 rounded-xl border p-4 text-center transition-all duration-200",
                        "hover:shadow-elevated",
                      )}
                    >
                      <div className="bg-primary/10 text-primary group-hover:bg-primary/15 rounded-lg p-2.5 transition-colors">
                        <Icon size={18} />
                      </div>
                      <div>
                        <p className="text-foreground text-sm leading-tight font-medium">
                          {action.label}
                        </p>
                        <p className="text-muted-foreground mt-0.5 text-xs leading-tight">
                          {action.description}
                        </p>
                      </div>
                    </Link>
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
