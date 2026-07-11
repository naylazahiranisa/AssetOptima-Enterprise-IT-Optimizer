"use client";

import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
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
import { PieChart as PieChartIcon } from "lucide-react";
import type { AssetStatusData } from "@/features/dashboard/types/dashboard";

interface AssetStatusChartProps {
  data?: AssetStatusData[];
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
}

export function AssetStatusChart({
  data,
  isLoading,
  isError,
  onRetry,
}: AssetStatusChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      <Card>
        <CardHeader>
          <CardTitle>Asset Status</CardTitle>
          <CardDescription>Current distribution by status</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Skeleton className="h-48 w-48 rounded-full" />
            </div>
          ) : isError ? (
            <ErrorState
              title="Failed to load asset data"
              message="Could not retrieve asset status distribution."
              onRetry={onRetry}
            />
          ) : !data || data.length === 0 ? (
            <EmptyState
              icon={<PieChartIcon size={40} strokeWidth={1.5} />}
              title="No asset data"
              description="Asset status distribution will appear once assets are registered."
            />
          ) : (
            <div className="flex flex-col items-center">
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                    strokeWidth={0}
                  >
                    {data.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      borderRadius: "8px",
                      border: "1px solid var(--border)",
                      background: "var(--card)",
                      boxShadow: "var(--shadow-elevated)",
                      fontSize: "13px",
                    }}
                    formatter={(value) => [String(value ?? 0), "Count"]}
                  />
                </PieChart>
              </ResponsiveContainer>

              <div className="mt-4 grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                {data.map((entry) => (
                  <div key={entry.name} className="flex items-center gap-2">
                    <span
                      className="h-2.5 w-2.5 shrink-0 rounded-full"
                      style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-muted-foreground">{entry.name}</span>
                    <span className="text-foreground ml-auto font-medium">
                      {entry.value}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
