"use client";

import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
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
import { BarChart3 } from "lucide-react";
import type { SoftwareUsageData } from "@/features/dashboard/types/dashboard";

interface SoftwareUsageChartProps {
  data?: SoftwareUsageData[];
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
}

export function SoftwareUsageChart({
  data,
  isLoading,
  isError,
  onRetry,
}: SoftwareUsageChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.15 }}
    >
      <Card>
        <CardHeader>
          <CardTitle>Software Usage</CardTitle>
          <CardDescription>Active licenses by title</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3 py-8">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="flex items-center gap-3">
                  <Skeleton className="h-3 w-20" />
                  <Skeleton className="h-3 flex-1" />
                  <Skeleton className="h-3 w-8" />
                </div>
              ))}
            </div>
          ) : isError ? (
            <ErrorState
              title="Failed to load software data"
              message="Could not retrieve software usage information."
              onRetry={onRetry}
            />
          ) : !data || data.length === 0 ? (
            <EmptyState
              icon={<BarChart3 size={40} strokeWidth={1.5} />}
              title="No software data"
              description="Software usage will appear once licenses are tracked."
            />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart
                data={data}
                layout="vertical"
                margin={{ top: 0, right: 40, left: 0, bottom: 0 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--border)"
                  horizontal={false}
                />
                <XAxis
                  type="number"
                  domain={[0, 100]}
                  tickFormatter={(v: number) => `${v}%`}
                  tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
                  axisLine={{ stroke: "var(--border)" }}
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
                  axisLine={false}
                  tickLine={false}
                  width={100}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid var(--border)",
                    background: "var(--card)",
                    boxShadow: "var(--shadow-elevated)",
                    fontSize: "13px",
                  }}
                  formatter={(value, name) => {
                    const item = data?.find((d) => d.name === String(name));
                    return [
                      item ? `${item.value} licenses` : String(value ?? 0),
                      "Usage",
                    ];
                  }}
                  labelFormatter={(label) => String(label ?? "")}
                />
                <Bar
                  dataKey="percentage"
                  radius={[0, 4, 4, 0]}
                  fill="var(--primary)"
                  maxBarSize={14}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
