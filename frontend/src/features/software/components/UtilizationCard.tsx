"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface UtilizationCardProps {
  purchased: number;
  assigned: number;
  available: number;
  inactive: number;
}

export function UtilizationCard({
  purchased,
  assigned,
  available,
  inactive,
}: UtilizationCardProps) {
  const utilizationPct =
    purchased > 0 ? Math.round((assigned / purchased) * 100) : 0;
  const availablePct =
    purchased > 0 ? Math.round((available / purchased) * 100) : 0;
  const inactivePct =
    purchased > 0 ? Math.round((inactive / purchased) * 100) : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>License Utilization</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-foreground font-medium">
              {utilizationPct}% utilized
            </span>
            <span className="text-muted-foreground text-xs">
              {assigned} / {purchased}
            </span>
          </div>
          <div className="bg-muted h-2.5 w-full overflow-hidden rounded-full">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${utilizationPct}%` }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className={cn(
                "h-full rounded-full",
                utilizationPct > 80
                  ? "bg-success"
                  : utilizationPct > 50
                    ? "bg-warning"
                    : "bg-danger",
              )}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-muted-foreground text-xs">Purchased</p>
            <p className="text-foreground mt-0.5 text-lg font-semibold">
              {purchased}
            </p>
          </div>
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-muted-foreground text-xs">Assigned</p>
            <p className="text-foreground mt-0.5 text-lg font-semibold">
              {assigned}
            </p>
          </div>
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-muted-foreground text-xs">Available</p>
            <p className="text-foreground mt-0.5 text-lg font-semibold">
              {available}
            </p>
          </div>
          <div className="bg-muted/50 rounded-lg p-3">
            <p className="text-muted-foreground text-xs">Inactive</p>
            <p
              className={cn(
                "mt-0.5 text-lg font-semibold",
                inactive > 0 ? "text-warning" : "text-foreground",
              )}
            >
              {inactive}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
