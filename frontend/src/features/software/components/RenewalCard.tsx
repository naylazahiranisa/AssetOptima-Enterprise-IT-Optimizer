"use client";

import { useState } from "react";
import { Calendar, AlertTriangle, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";
import type { LicenseStatus } from "@/features/software/types/software";

interface RenewalCardProps {
  renewalDate: string;
  monthlyCost: number;
  annualCost: number;
  status: LicenseStatus;
}

export function RenewalCard({
  renewalDate,
  monthlyCost,
  annualCost,
  status,
}: RenewalCardProps) {
  const [now] = useState(() => Date.now());
  const daysUntilRenewal = Math.ceil(
    (new Date(renewalDate).getTime() - now) / (1000 * 60 * 60 * 24),
  );

  const isExpired = status === "expired";
  const isExpiringSoon =
    status === "expiring_soon" ||
    (daysUntilRenewal > 0 && daysUntilRenewal <= 60);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Renewal Info</CardTitle>
          {isExpired ? (
            <Badge variant="danger">Expired</Badge>
          ) : isExpiringSoon ? (
            <Badge variant="warning">Expiring Soon</Badge>
          ) : (
            <Badge variant="success">Active</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              "flex h-9 w-9 items-center justify-center rounded-lg",
              isExpired
                ? "bg-danger/10 text-danger"
                : isExpiringSoon
                  ? "bg-warning/10 text-warning"
                  : "bg-success/10 text-success",
            )}
          >
            {isExpired || isExpiringSoon ? (
              <AlertTriangle size={16} />
            ) : (
              <CheckCircle2 size={16} />
            )}
          </div>
          <div>
            <p className="text-foreground text-sm font-medium">
              {isExpired
                ? "Renewal overdue"
                : isExpiringSoon
                  ? `${daysUntilRenewal} days until renewal`
                  : `${daysUntilRenewal} days until renewal`}
            </p>
            <p className="text-muted-foreground flex items-center gap-1 text-xs">
              <Calendar size={10} />
              {renewalDate}
            </p>
          </div>
        </div>

        <Separator />

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground text-sm">Monthly Cost</span>
            <span className="text-foreground font-semibold">
              {formatCurrency(monthlyCost)}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground text-sm">Annual Cost</span>
            <span className="text-foreground font-semibold">
              {formatCurrency(annualCost)}
            </span>
          </div>
          {monthlyCost > 0 && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground text-sm">
                Per Month / License
              </span>
              <span className="text-foreground text-sm font-medium">
                {formatCurrency(monthlyCost / Math.max(1, 1))}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function cn(...inputs: (string | false | undefined | null)[]): string {
  return inputs.filter(Boolean).join(" ");
}
