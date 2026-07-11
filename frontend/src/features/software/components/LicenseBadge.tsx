"use client";

import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import type { LicenseStatus } from "@/features/software/types/software";

const licenseVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      status: {
        active: "border-transparent bg-success/10 text-success",
        expired: "border-transparent bg-danger/10 text-danger",
        expiring_soon: "border-transparent bg-warning/10 text-warning",
        unused: "border-transparent bg-muted text-muted-foreground",
        suspended:
          "border-transparent bg-muted text-muted-foreground line-through",
      },
    },
    defaultVariants: {
      status: "unused",
    },
  },
);

const licenseLabel: Record<LicenseStatus, string> = {
  active: "Active",
  expired: "Expired",
  expiring_soon: "Expiring Soon",
  unused: "Unused",
  suspended: "Suspended",
};

interface LicenseBadgeProps extends VariantProps<typeof licenseVariants> {
  status: LicenseStatus;
  className?: string;
}

export function LicenseBadge({ status, className }: LicenseBadgeProps) {
  return (
    <span className={cn(licenseVariants({ status }), className)}>
      {licenseLabel[status]}
    </span>
  );
}
