"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { LicenseBadge } from "@/features/software/components/LicenseBadge";
import { formatCurrency } from "@/lib/utils";
import type { SoftwareLicense } from "@/features/software/types/software";

interface LicenseCardProps {
  software: SoftwareLicense;
  index?: number;
}

export function LicenseCard({ software, index = 0 }: LicenseCardProps) {
  const utilizationPct =
    software.total_licenses > 0
      ? Math.round((software.used_licenses / software.total_licenses) * 100)
      : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.03 }}
    >
      <Link href={`/licenses/${software.id}`} className="block">
        <Card className="hover:shadow-card transition-all duration-200 hover:-translate-y-0.5">
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-foreground truncate text-sm font-semibold">
                  {software.software_name}
                </p>
                <p className="text-muted-foreground mt-0.5 text-xs">
                  {software.vendor}
                </p>
              </div>
              <LicenseBadge status={software.status} />
            </div>

            <div className="mt-4 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Utilization</span>
                <span className="text-foreground font-medium">
                  {utilizationPct}%
                </span>
              </div>
              <div className="bg-muted h-1.5 w-full overflow-hidden rounded-full">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${utilizationPct}%` }}
                  transition={{ duration: 0.6, delay: index * 0.03 }}
                  className={`h-full rounded-full ${
                    utilizationPct > 80
                      ? "bg-success"
                      : utilizationPct > 50
                        ? "bg-warning"
                        : "bg-danger"
                  }`}
                />
              </div>
            </div>

            <div className="border-border mt-3 grid grid-cols-3 gap-2 border-t pt-3">
              <div>
                <p className="text-muted-foreground text-[10px] tracking-wider uppercase">
                  Seats
                </p>
                <p className="text-foreground text-xs font-medium">
                  {software.used_licenses}/{software.total_licenses}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground text-[10px] tracking-wider uppercase">
                  Cost/mo
                </p>
                <p className="text-foreground text-xs font-medium">
                  {formatCurrency(software.monthly_cost)}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground text-[10px] tracking-wider uppercase">
                  Renewal
                </p>
                <p className="text-foreground text-xs font-medium">
                  {software.renewal_date}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}
