"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Sparkles, TrendingUp, DollarSign, AlertCircle } from "lucide-react";
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
import { formatCurrency, cn } from "@/lib/utils";
import type { AiInsight } from "@/features/dashboard/types/dashboard";

interface AiInsightCardProps {
  data?: AiInsight;
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
}

const riskBadgeMap: Record<
  string,
  { variant: "warning" | "danger" | "success"; label: string }
> = {
  low: { variant: "success", label: "Low Risk" },
  medium: { variant: "warning", label: "Medium Risk" },
  high: { variant: "danger", label: "High Risk" },
};

export function AiInsightCard({
  data,
  isLoading,
  isError,
  onRetry,
}: AiInsightCardProps) {
  const router = useRouter();
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      <Card className="border-ai/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="bg-ai/10 text-ai rounded-lg p-2">
                <Sparkles size={16} />
              </div>
              <CardTitle>AI Insight</CardTitle>
            </div>
            {data && (
              <Badge variant={riskBadgeMap[data.riskLevel].variant}>
                {riskBadgeMap[data.riskLevel].label}
              </Badge>
            )}
          </div>
          <CardDescription>
            Predictive license optimization summary
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="space-y-2">
                    <Skeleton className="h-3 w-16" />
                    <Skeleton className="h-6 w-12" />
                  </div>
                ))}
              </div>
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : isError ? (
            <ErrorState
              title="AI analysis unavailable"
              message="Could not generate license optimization insights."
              onRetry={onRetry}
            />
          ) : !data ? (
            <EmptyState
              icon={<Sparkles size={40} strokeWidth={1.5} />}
              title="No insights yet"
              description="AI recommendations will appear once sufficient data is collected."
            />
          ) : (
            <div className="space-y-5">
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <p className="text-muted-foreground flex items-center gap-1 text-xs">
                    <AlertCircle size={12} />
                    Dormant
                  </p>
                  <p className="text-foreground text-xl font-semibold">
                    {data.dormantLicenses}
                  </p>
                  <p className="text-muted-foreground text-xs">licenses</p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground flex items-center gap-1 text-xs">
                    <TrendingUp size={12} />
                    Predicted
                  </p>
                  <p className="text-foreground text-xl font-semibold">
                    {data.predictedLicenses}
                  </p>
                  <p className="text-muted-foreground text-xs">
                    licenses needed
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground flex items-center gap-1 text-xs">
                    <DollarSign size={12} />
                    Savings
                  </p>
                  <p className="text-success text-xl font-semibold">
                    {formatCurrency(data.potentialSavings)}
                  </p>
                  <p className="text-muted-foreground text-xs">potential</p>
                </div>
              </div>

              <div
                className={cn(
                  "rounded-lg border p-3 text-sm",
                  data.riskLevel === "high"
                    ? "border-danger/20 bg-danger/5"
                    : data.riskLevel === "medium"
                      ? "border-warning/20 bg-warning/5"
                      : "border-success/20 bg-success/5",
                )}
              >
                <p
                  className={cn(
                    "text-xs font-medium",
                    data.riskLevel === "high"
                      ? "text-danger"
                      : data.riskLevel === "medium"
                        ? "text-warning"
                        : "text-success",
                  )}
                >
                  Top Recommendation
                </p>
                <p className="text-foreground mt-1 text-sm">
                  {data.topRecommendation}
                </p>
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Button variant="outline" size="sm" className="w-full gap-2" onClick={() => router.push("/ai-assistant")}>
            <Sparkles size={14} />
            Open AI Assistant
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
}
