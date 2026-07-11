"use client";

import { use, useState } from "react";
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
import { Avatar } from "@/components/ui/avatar";
import { Alert } from "@/components/ui/alert";
import { ArrowLeft, Edit, Trash2, Building2, Users } from "lucide-react";
import { LicenseBadge } from "@/features/software/components/LicenseBadge";
import { UtilizationCard } from "@/features/software/components/UtilizationCard";
import { RenewalCard } from "@/features/software/components/RenewalCard";
import { AiReadinessPanel } from "@/features/software/components/AiReadinessPanel";
import { AssignLicenseModal } from "@/features/software/components/AssignLicenseModal";
import { SoftwareDetailSkeleton } from "@/features/software/components/SoftwareSkeleton";
import {
  useSoftwareById,
  useSoftwareAssignments,
  useDeleteSoftware,
} from "@/features/software/services/software.service";
import { formatCurrency, formatDate, getInitials } from "@/lib/utils";

interface SoftwareDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function SoftwareDetailPage({
  params,
}: SoftwareDetailPageProps) {
  const { id } = use(params);
  const router = useRouter();
  const { data: software, isLoading } = useSoftwareById(id);
  const { data: assignments, isLoading: assignmentsLoading } =
    useSoftwareAssignments(id);
  const deleteSoftware = useDeleteSoftware();
  const [assignOpen, setAssignOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this software?")) return;
    setDeleting(true);
    try {
      await deleteSoftware.mutateAsync(id);
      router.push("/software");
    } catch {
      setDeleting(false);
    }
  };

  if (isLoading) return <SoftwareDetailSkeleton />;
  if (!software) {
    return (
      <Alert variant="error" title="Not Found" message="Software not found." />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={software.software_name}
        description={`${software.vendor} — ${software.department}`}
        actions={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/software")}
            >
              <ArrowLeft size={14} />
              Back
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAssignOpen(true)}
            >
              <Users size={14} />
              Assign License
            </Button>
            <Link href={`/software/${id}/edit`}>
              <Button variant="outline" size="sm">
                <Edit size={14} />
                Edit
              </Button>
            </Link>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDelete}
              disabled={deleting}
            >
              <Trash2 size={14} />
              {deleting ? "Deleting..." : "Delete"}
            </Button>
          </>
        }
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Software Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Vendor
                  </p>
                  <p className="text-foreground flex items-center gap-1.5 text-sm font-medium">
                    <Building2 size={14} className="text-muted-foreground" />
                    {software.vendor}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Category
                  </p>
                  <p className="text-foreground text-sm capitalize">
                    {software.category}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    License Type
                  </p>
                  <p className="text-foreground text-sm capitalize">
                    {software.license_type}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Department
                  </p>
                  <p className="text-foreground text-sm">
                    {software.department}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Status
                  </p>
                  <LicenseBadge status={software.status} />
                </div>
                <div className="space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Created
                  </p>
                  <p className="text-foreground text-sm">
                    {formatDate(software.created_at)}
                  </p>
                </div>
              </div>
              {software.description && (
                <>
                  <Separator className="my-4" />
                  <div className="space-y-1">
                    <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                      Description
                    </p>
                    <p className="text-foreground text-sm">
                      {software.description}
                    </p>
                  </div>
                </>
              )}
              {software.notes && (
                <div className="mt-4 space-y-1">
                  <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
                    Notes
                  </p>
                  <p className="text-muted-foreground text-sm">
                    {software.notes}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Assigned Employees</CardTitle>
              <CardDescription>
                {assignments?.length ?? 0} of {software.total_licenses} licenses
                assigned
              </CardDescription>
            </CardHeader>
            <CardContent>
              {assignmentsLoading ? (
                <div className="space-y-3">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="bg-muted h-9 w-9 animate-pulse rounded-full" />
                      <div className="flex-1 space-y-1">
                        <div className="bg-muted h-4 w-32 animate-pulse rounded" />
                        <div className="bg-muted h-3 w-48 animate-pulse rounded" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : assignments && assignments.length > 0 ? (
                <div className="space-y-3">
                  {assignments.map((a) => (
                    <div key={a.id} className="flex items-center gap-3">
                      <Avatar
                        fallback={getInitials(a.employee_name)}
                        size="sm"
                      />
                      <div className="min-w-0 flex-1">
                        <p className="text-foreground text-sm font-medium">
                          {a.employee_name}
                        </p>
                        <p className="text-muted-foreground truncate text-xs">
                          {a.employee_email}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-muted-foreground text-xs">
                          {a.assigned_date}
                        </p>
                        {a.license_key && (
                          <p className="text-muted-foreground font-mono text-[10px]">
                            {a.license_key}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-8">
                  <Users
                    size={32}
                    className="text-muted-foreground/40 mb-3"
                    strokeWidth={1.5}
                  />
                  <p className="text-foreground text-sm font-medium">
                    No assignments yet
                  </p>
                  <p className="text-muted-foreground mt-1 text-xs">
                    Assign licenses to employees to track usage
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-3"
                    onClick={() => setAssignOpen(true)}
                  >
                    <Users size={14} />
                    Assign License
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          <AiReadinessPanel />
        </div>

        <div className="space-y-6">
          <UtilizationCard
            purchased={software.total_licenses}
            assigned={software.used_licenses}
            available={software.available_licenses}
            inactive={software.inactive_licenses}
          />

          <RenewalCard
            renewalDate={software.renewal_date}
            monthlyCost={software.monthly_cost}
            annualCost={software.annual_cost}
            status={software.status}
          />

          <Card>
            <CardHeader>
              <CardTitle>Cost Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">
                  Monthly Cost
                </span>
                <span className="text-foreground font-semibold">
                  {formatCurrency(software.monthly_cost)}
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">
                  Annual Cost
                </span>
                <span className="text-foreground font-semibold">
                  {formatCurrency(software.annual_cost)}
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">
                  Cost per License (Monthly)
                </span>
                <span className="text-foreground text-sm font-medium">
                  {software.total_licenses > 0
                    ? formatCurrency(
                        software.monthly_cost / software.total_licenses,
                      )
                    : "—"}
                </span>
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground text-sm">
                  Cost per License (Annual)
                </span>
                <span className="text-foreground text-sm font-medium">
                  {software.total_licenses > 0
                    ? formatCurrency(
                        software.annual_cost / software.total_licenses,
                      )
                    : "—"}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Vendor Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="bg-primary/10 text-primary flex h-10 w-10 items-center justify-center rounded-lg">
                  <Building2 size={18} />
                </div>
                <div>
                  <p className="text-foreground text-sm font-medium">
                    {software.vendor}
                  </p>
                  <p className="text-muted-foreground text-xs capitalize">
                    {software.category}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <AssignLicenseModal
        open={assignOpen}
        onOpenChange={setAssignOpen}
        softwareId={id}
        softwareName={software.software_name}
      />
    </div>
  );
}
