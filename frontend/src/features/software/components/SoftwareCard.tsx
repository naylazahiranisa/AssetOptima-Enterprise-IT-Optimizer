"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Building2, Calendar, DollarSign, Users } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LicenseBadge } from "@/features/software/components/LicenseBadge";
import { formatCurrency } from "@/lib/utils";
import type { SoftwareLicense } from "@/features/software/types/software";

interface SoftwareCardProps {
  software: SoftwareLicense;
  index?: number;
}

export function SoftwareCard({ software, index = 0 }: SoftwareCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.03 }}
    >
      <Link href={`/software/${software.id}`} className="block">
        <Card className="hover:shadow-card transition-all duration-200 hover:-translate-y-0.5">
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <p className="text-foreground truncate text-sm font-semibold">
                    {software.software_name}
                  </p>
                  {software.status === "expiring_soon" && (
                    <Badge
                      variant="warning"
                      className="shrink-0 px-1.5 text-[10px]"
                    >
                      Renewal
                    </Badge>
                  )}
                </div>
                <p className="text-muted-foreground mt-0.5 text-xs">
                  {software.vendor}
                </p>
              </div>
              <LicenseBadge status={software.status} />
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2">
              <div className="flex items-center gap-1.5 text-xs">
                <Building2 size={12} className="text-muted-foreground" />
                <span className="text-foreground capitalize">
                  {software.category}
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-xs">
                <Users size={12} className="text-muted-foreground" />
                <span className="text-foreground">
                  {software.used_licenses}/{software.total_licenses} seats
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-xs">
                <DollarSign size={12} className="text-muted-foreground" />
                <span className="text-foreground">
                  {formatCurrency(software.monthly_cost)}/mo
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-xs">
                <Calendar size={12} className="text-muted-foreground" />
                <span className="text-foreground">{software.renewal_date}</span>
              </div>
            </div>

            <div className="mt-3 flex items-center gap-1.5">
              <span className="text-muted-foreground text-[10px] uppercase">
                {software.department}
              </span>
              <span className="text-muted-foreground">·</span>
              <span className="text-muted-foreground text-[10px] capitalize">
                {software.license_type}
              </span>
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}
