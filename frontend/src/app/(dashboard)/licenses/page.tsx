"use client";

import { useMemo } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Key,
  AlertTriangle,
  CheckCircle2,
  Clock,
  XCircle,
  TrendingUp,
} from "lucide-react";
import { LicenseCard } from "@/features/software/components/LicenseCard";
import { LicensesOverviewSkeleton } from "@/features/software/components/SoftwareSkeleton";
import { useLicenses } from "@/features/software/services/software.service";
import { formatCurrency } from "@/lib/utils";

export default function LicensesPage() {
  const { data: licenses, isLoading } = useLicenses();

  const stats = useMemo(() => {
    if (!licenses) return null;
    const active = licenses.filter((l) => l.status === "active");
    const expired = licenses.filter((l) => l.status === "expired");
    const expiringSoon = licenses.filter((l) => l.status === "expiring_soon");
    const unused = licenses.filter((l) => l.status === "unused");
    const totalMonthly = licenses.reduce((sum, l) => sum + l.monthly_cost, 0);
    const totalAnnual = licenses.reduce((sum, l) => sum + l.annual_cost, 0);
    const totalSeats = licenses.reduce((sum, l) => sum + l.total_licenses, 0);
    const usedSeats = licenses.reduce((sum, l) => sum + l.used_licenses, 0);
    const utilPct =
      totalSeats > 0 ? Math.round((usedSeats / totalSeats) * 100) : 0;
    return {
      active,
      expired,
      expiringSoon,
      unused,
      totalMonthly,
      totalAnnual,
      totalSeats,
      usedSeats,
      utilPct,
    };
  }, [licenses]);

  if (isLoading) return <LicensesOverviewSkeleton />;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Licenses"
        description="Overview of all software licenses and utilization"
        actions={
          <Badge variant="primary" className="gap-1.5">
            <Key size={12} />
            {licenses?.length ?? 0} Licenses
          </Badge>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
              Active
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-foreground text-2xl font-bold">
              {stats?.active.length ?? 0}
            </p>
            <div className="mt-1 flex items-center gap-1 text-xs">
              <CheckCircle2 size={10} className="text-success" />
              <span className="text-muted-foreground">Active licenses</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
              Expiring Soon
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-foreground text-2xl font-bold">
              {stats?.expiringSoon.length ?? 0}
            </p>
            <div className="mt-1 flex items-center gap-1 text-xs">
              <Clock size={10} className="text-warning" />
              <span className="text-muted-foreground">Need attention</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
              Expired
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-foreground text-2xl font-bold">
              {stats?.expired.length ?? 0}
            </p>
            <div className="mt-1 flex items-center gap-1 text-xs">
              <XCircle size={10} className="text-danger" />
              <span className="text-muted-foreground">Overdue renewals</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
              Unused
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-foreground text-2xl font-bold">
              {stats?.unused.length ?? 0}
            </p>
            <div className="mt-1 flex items-center gap-1 text-xs">
              <AlertTriangle size={10} className="text-warning" />
              <span className="text-muted-foreground">Wasted spend</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
              Utilization
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <p className="text-foreground text-2xl font-bold">
              {stats?.utilPct ?? 0}%
            </p>
            <div className="mt-1 flex items-center gap-1 text-xs">
              <TrendingUp size={10} className="text-primary" />
              <span className="text-muted-foreground">
                {stats?.usedSeats ?? 0}/{stats?.totalSeats ?? 0} seats
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>All Licenses</CardTitle>
          </CardHeader>
          <CardContent>
            {licenses && licenses.length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {licenses.map((sw, i) => (
                  <LicenseCard key={sw.id} software={sw} index={i} />
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12">
                <Key
                  size={32}
                  className="text-muted-foreground/40 mb-3"
                  strokeWidth={1.5}
                />
                <p className="text-foreground text-sm font-medium">
                  No licenses found
                </p>
                <p className="text-muted-foreground mt-1 text-xs">
                  Licenses will appear once software is registered
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Cost Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">
                  Monthly Total
                </span>
                <span className="text-foreground text-lg font-bold">
                  {formatCurrency(stats?.totalMonthly ?? 0)}
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">
                  Annual Total
                </span>
                <span className="text-foreground text-lg font-bold">
                  {formatCurrency(stats?.totalAnnual ?? 0)}
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">
                  Avg Cost / License
                </span>
                <span className="text-foreground font-semibold">
                  {stats && stats.totalSeats > 0
                    ? formatCurrency(stats.totalMonthly / stats.totalSeats)
                    : "—"}
                  <span className="text-muted-foreground text-xs font-normal">
                    /mo
                  </span>
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Upcoming Renewals</CardTitle>
            </CardHeader>
            <CardContent>
              {licenses ? (
                <div className="space-y-3">
                  {licenses
                    .filter(
                      (l) =>
                        l.status === "active" || l.status === "expiring_soon",
                    )
                    .sort(
                      (a, b) =>
                        new Date(a.renewal_date).getTime() -
                        new Date(b.renewal_date).getTime(),
                    )
                    .slice(0, 5)
                    .map((l) => (
                      <div
                        key={l.id}
                        className="flex items-center justify-between"
                      >
                        <div className="min-w-0 flex-1">
                          <p className="text-foreground truncate text-sm font-medium">
                            {l.software_name}
                          </p>
                          <p className="text-muted-foreground text-xs">
                            {l.renewal_date}
                          </p>
                        </div>
                        <Badge
                          variant={
                            l.status === "expiring_soon" ? "warning" : "success"
                          }
                          className="ml-2 shrink-0 text-[10px]"
                        >
                          {l.status === "expiring_soon" ? "Soon" : "Active"}
                        </Badge>
                      </div>
                    ))}
                  {licenses.filter(
                    (l) =>
                      l.status === "active" || l.status === "expiring_soon",
                  ).length === 0 && (
                    <p className="text-muted-foreground py-4 text-center text-sm">
                      No upcoming renewals
                    </p>
                  )}
                </div>
              ) : (
                <div className="bg-muted h-20 animate-pulse rounded-lg" />
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
