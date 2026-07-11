"use client";

import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import type {
  AssetStatus,
  AssetCondition,
  WarrantyStatus,
} from "@/features/assets/types/assets";

const statusVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      status: {
        available: "border-transparent bg-success/10 text-success",
        assigned: "border-transparent bg-primary/10 text-primary",
        maintenance: "border-transparent bg-warning/10 text-warning",
        lost: "border-transparent bg-danger/10 text-danger",
        retired: "border-transparent bg-muted text-muted-foreground",
      },
    },
    defaultVariants: {
      status: "available",
    },
  },
);

const conditionVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      condition: {
        new: "border-transparent bg-success/10 text-success",
        good: "border-transparent bg-primary/10 text-primary",
        fair: "border-transparent bg-warning/10 text-warning",
        poor: "border-transparent bg-danger/10 text-danger",
        damaged: "border-transparent bg-danger/10 text-danger",
      },
    },
    defaultVariants: {
      condition: "good",
    },
  },
);

const warrantyVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      warranty: {
        active: "border-transparent bg-success/10 text-success",
        expiring_soon: "border-transparent bg-warning/10 text-warning",
        expired: "border-transparent bg-danger/10 text-danger",
        not_covered: "border-transparent bg-muted text-muted-foreground",
      },
    },
    defaultVariants: {
      warranty: "not_covered",
    },
  },
);

const statusLabel: Record<AssetStatus, string> = {
  available: "Available",
  assigned: "Assigned",
  maintenance: "Maintenance",
  lost: "Lost",
  retired: "Retired",
};

const conditionLabel: Record<AssetCondition, string> = {
  new: "New",
  good: "Good",
  fair: "Fair",
  poor: "Poor",
  damaged: "Damaged",
};

const warrantyLabel: Record<WarrantyStatus, string> = {
  active: "Active",
  expiring_soon: "Expiring Soon",
  expired: "Expired",
  not_covered: "Not Covered",
};

interface AssetStatusBadgeProps extends VariantProps<typeof statusVariants> {
  status: AssetStatus;
  className?: string;
}

export function AssetStatusBadge({ status, className }: AssetStatusBadgeProps) {
  return (
    <span className={cn(statusVariants({ status }), className)}>
      {statusLabel[status]}
    </span>
  );
}

interface AssetConditionBadgeProps extends VariantProps<
  typeof conditionVariants
> {
  condition: AssetCondition;
  className?: string;
}

export function AssetConditionBadge({
  condition,
  className,
}: AssetConditionBadgeProps) {
  return (
    <span className={cn(conditionVariants({ condition }), className)}>
      {conditionLabel[condition]}
    </span>
  );
}

interface AssetWarrantyBadgeProps extends VariantProps<
  typeof warrantyVariants
> {
  warranty: WarrantyStatus;
  className?: string;
}

export function AssetWarrantyBadge({
  warranty,
  className,
}: AssetWarrantyBadgeProps) {
  return (
    <span className={cn(warrantyVariants({ warranty }), className)}>
      {warrantyLabel[warranty]}
    </span>
  );
}
