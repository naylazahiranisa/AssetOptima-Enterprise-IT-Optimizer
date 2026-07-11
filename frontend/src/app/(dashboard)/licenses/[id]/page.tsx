"use client";

import { use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Alert } from "@/components/ui/alert";
import { ArrowLeft, ArrowUpRight, Building2 } from "lucide-react";
import { LicenseBadge } from "@/features/software/components/LicenseBadge";
import { UtilizationCard } from "@/features/software/components/UtilizationCard";
import { RenewalCard } from "@/features/software/components/RenewalCard";
import { SoftwareDetailSkeleton } from "@/features/software/components/SoftwareSkeleton";
import { useLicenseById } from "@/features/software/services/software.service";
import { formatCurrency, formatDate } from "@/lib/utils";

interface LicenseDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function LicenseDetailPage({ params }: LicenseDetailPageProps) {
  const { id } = use(params);
  const router = useRouter();
  const { data: license, isLoading } = useLicenseById(id);

  if (isLoading) return <SoftwareDetailSkeleton />;
  if (!license) {
    return (
      <Alert variant="error" title="Not Found" message="License not found." />
    );
  }

  const utilizationPct =
    license.total_licenses > 0
      ? Math.round((license.used_licenses / license.total_licenses) * 100)
      : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title={license.software_name}
        description={`License Details — ${license.vendor}`}
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/licenses")}
            >
              <ArrowLeft size={14} />
              Back
            </Button>
            <Link href={`/software/${license.id}`}>
              <Button variant="outline" size="sm">
                <ArrowUpRight size={14} />
                View Software
              </Button>
            </Link>
          </>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>License Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Software
                  </p>
                  <p className="text-foreground text-sm font-medium">
                    {license.software_name}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Vendor
                  </p>
                  <p className="text-foreground flex items-center gap-1.5 text-sm">
                    <Building2 size={14} className="text-muted-foreground" />
                    {license.vendor}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    License Type
                  </p>
                  <p className="text-foreground text-sm capitalize">
                    {license.license_type}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Status
                  </p>
                  <LicenseBadge status={license.status} />
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Category
                  </p>
                  <p className="text-foreground text-sm capitalize">
                    {license.category}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Department
                  </p>
                  <p className="text-foreground text-sm">
                    {license.department}
                  </p>
                </div>
              </div>
              {license.description && (
                <>
                  <Separator className="my-4" />
                  <div className="space-y-1">
                    <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                      Description
                    </p>
                    <p className="text-foreground text-sm">
                      {license.description}
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>License Summary</CardTitle>
              <CardDescription>
                {utilizationPct}% utilization across {license.department}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 sm:grid-cols-4">
                <div className="bg-muted/50 rounded-lg p-4 text-center">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Purchased
                  </p>
                  <p className="text-foreground mt-1 text-2xl font-bold">
                    {license.total_licenses}
                  </p>
                </div>
                <div className="bg-muted/50 rounded-lg p-4 text-center">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Assigned
                  </p>
                  <p className="text-foreground mt-1 text-2xl font-bold">
                    {license.used_licenses}
                  </p>
                </div>
                <div className="bg-muted/50 rounded-lg p-4 text-center">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Available
                  </p>
                  <p className="text-foreground mt-1 text-2xl font-bold">
                    {license.available_licenses}
                  </p>
                </div>
                <div className="bg-muted/50 rounded-lg p-4 text-center">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Inactive
                  </p>
                  <p className="text-foreground mt-1 text-2xl font-bold">
                    {license.inactive_licenses}
                  </p>
                </div>
              </div>

              <div className="mt-6 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-foreground font-medium">
                    Utilization Rate
                  </span>
                  <span
                    className={
                      utilizationPct > 80
                        ? "text-success"
                        : utilizationPct > 50
                          ? "text-warning"
                          : "text-danger"
                    }
                  >
                    {utilizationPct}%
                  </span>
                </div>
                <div className="bg-muted h-2.5 w-full overflow-hidden rounded-full">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      utilizationPct > 80
                        ? "bg-success"
                        : utilizationPct > 50
                          ? "bg-warning"
                          : "bg-danger"
                    }`}
                    style={{ width: `${utilizationPct}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <UtilizationCard
            purchased={license.total_licenses}
            assigned={license.used_licenses}
            available={license.available_licenses}
            inactive={license.inactive_licenses}
          />

          <RenewalCard
            renewalDate={license.renewal_date}
            monthlyCost={license.monthly_cost}
            annualCost={license.annual_cost}
            status={license.status}
          />

          <Card>
            <CardHeader>
              <CardTitle>Quick Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Created</span>
                <span className="text-foreground">
                  {formatDate(license.created_at)}
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Last Updated</span>
                <span className="text-foreground">
                  {formatDate(license.updated_at)}
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">
                  Cost per License (Mo.)
                </span>
                <span className="text-foreground font-medium">
                  {license.total_licenses > 0
                    ? formatCurrency(
                        license.monthly_cost / license.total_licenses,
                      )
                    : "—"}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
