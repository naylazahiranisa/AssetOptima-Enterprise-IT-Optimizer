"use client";

import { cn } from "@/lib/utils";

interface ConfidenceBadgeProps {
  score: number;
  className?: string;
}

/** Displays AI confidence score with color-coded badge */
export function ConfidenceBadge({ score, className }: ConfidenceBadgeProps) {
  const pct = Math.round(score * 100);
  const label = pct >= 90 ? "High" : pct >= 70 ? "Medium" : "Low";
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] font-medium",
        pct >= 90 && "bg-success/10 text-success",
        pct >= 70 && pct < 90 && "bg-warning/10 text-warning",
        pct < 70 && "bg-danger/10 text-danger",
        className,
      )}
    >
      <span>{label}</span>
      <span className="opacity-70">{pct}%</span>
    </div>
  );
}
