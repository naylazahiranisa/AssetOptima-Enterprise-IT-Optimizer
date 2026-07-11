"use client";

import { use, useEffect } from "react";
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
import { ArrowLeft } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { SoftwareFormSkeleton } from "@/features/software/components/SoftwareSkeleton";
import {
  useSoftwareById,
  useUpdateSoftware,
} from "@/features/software/services/software.service";

const editSoftwareSchema = z.object({
  software_name: z.string().min(1, "Software name is required"),
  vendor: z.string().min(1, "Vendor is required"),
  category: z.enum([
    "productivity",
    "design",
    "development",
    "security",
    "communication",
    "analytics",
    "infrastructure",
    "finance",
    "hr",
    "other",
  ]),
  license_type: z.enum([
    "perpetual",
    "subscription",
    "concurrent",
    "floating",
    "volume",
  ]),
  total_licenses: z.coerce.number().min(1, "At least 1 license required"),
  used_licenses: z.coerce.number().min(0, "Cannot be negative"),
  available_licenses: z.coerce.number().min(0, "Cannot be negative"),
  inactive_licenses: z.coerce.number().min(0, "Cannot be negative"),
  monthly_cost: z.coerce.number().min(0, "Cost cannot be negative"),
  annual_cost: z.coerce.number().min(0, "Cost cannot be negative"),
  renewal_date: z.string().min(1, "Renewal date is required"),
  department: z.string().min(1, "Department is required"),
  status: z.enum(["active", "expired", "expiring_soon", "unused", "suspended"]),
  notes: z.string().optional(),
  description: z.string().optional(),
});

type EditSoftwareFormData = z.infer<typeof editSoftwareSchema>;

interface EditSoftwarePageProps {
  params: Promise<{ id: string }>;
}

export default function EditSoftwarePage({ params }: EditSoftwarePageProps) {
  const { id } = use(params);
  const router = useRouter();
  const { data: software, isLoading } = useSoftwareById(id);
  const updateSoftware = useUpdateSoftware();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<EditSoftwareFormData>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(editSoftwareSchema) as any,
  });

  useEffect(() => {
    if (software) {
      reset({
        software_name: software.software_name,
        vendor: software.vendor,
        category: software.category,
        license_type: software.license_type,
        total_licenses: software.total_licenses,
        used_licenses: software.used_licenses,
        available_licenses: software.available_licenses,
        inactive_licenses: software.inactive_licenses,
        monthly_cost: software.monthly_cost,
        annual_cost: software.annual_cost,
        renewal_date: software.renewal_date,
        department: software.department,
        status: software.status,
        notes: software.notes || "",
        description: software.description || "",
      });
    }
  }, [software, reset]);

  const onSubmit = async (data: EditSoftwareFormData) => {
    try {
      await updateSoftware.mutateAsync({ id, payload: data });
      router.push(`/software/${id}`);
    } catch {
      // handled by react-query
    }
  };

  if (isLoading) return <SoftwareFormSkeleton />;
  if (!software) {
    return (
      <div className="flex items-center justify-center py-16">
        <p className="text-muted-foreground text-sm">Software not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Edit: ${software.software_name}`}
        description="Update software information and license details"
        actions={
          <Button variant="outline" size="sm" onClick={() => router.back()}>
            <ArrowLeft size={14} />
            Back
          </Button>
        }
      />

      <Card>
        <CardHeader>
          <CardTitle>Software Details</CardTitle>
          <CardDescription>
            Modify the fields below and save your changes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            <div className="grid gap-6 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Software Name
                </label>
                <input
                  {...register("software_name")}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.software_name && (
                  <p className="text-danger text-xs">
                    {errors.software_name.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Vendor
                </label>
                <input
                  {...register("vendor")}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.vendor && (
                  <p className="text-danger text-xs">{errors.vendor.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Category
                </label>
                <select
                  {...register("category")}
                  className="border-border bg-card text-foreground focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                >
                  <option value="productivity">Productivity</option>
                  <option value="design">Design</option>
                  <option value="development">Development</option>
                  <option value="security">Security</option>
                  <option value="communication">Communication</option>
                  <option value="analytics">Analytics</option>
                  <option value="infrastructure">Infrastructure</option>
                  <option value="finance">Finance</option>
                  <option value="hr">HR</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  License Type
                </label>
                <select
                  {...register("license_type")}
                  className="border-border bg-card text-foreground focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                >
                  <option value="subscription">Subscription</option>
                  <option value="perpetual">Perpetual</option>
                  <option value="concurrent">Concurrent</option>
                  <option value="floating">Floating</option>
                  <option value="volume">Volume</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Total Licenses
                </label>
                <input
                  type="number"
                  {...register("total_licenses")}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.total_licenses && (
                  <p className="text-danger text-xs">
                    {errors.total_licenses.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Used Licenses
                </label>
                <input
                  type="number"
                  {...register("used_licenses")}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.used_licenses && (
                  <p className="text-danger text-xs">
                    {errors.used_licenses.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Available Licenses
                </label>
                <input
                  type="number"
                  {...register("available_licenses")}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.available_licenses && (
                  <p className="text-danger text-xs">
                    {errors.available_licenses.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Inactive Licenses
                </label>
                <input
                  type="number"
                  {...register("inactive_licenses")}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.inactive_licenses && (
                  <p className="text-danger text-xs">
                    {errors.inactive_licenses.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Monthly Cost ($)
                </label>
                <input
                  type="number"
                  {...register("monthly_cost")}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.monthly_cost && (
                  <p className="text-danger text-xs">
                    {errors.monthly_cost.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Annual Cost ($)
                </label>
                <input
                  type="number"
                  {...register("annual_cost")}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.annual_cost && (
                  <p className="text-danger text-xs">
                    {errors.annual_cost.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Renewal Date
                </label>
                <input
                  type="date"
                  {...register("renewal_date")}
                  className="border-border bg-card text-foreground focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.renewal_date && (
                  <p className="text-danger text-xs">
                    {errors.renewal_date.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Department
                </label>
                <input
                  {...register("department")}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
                {errors.department && (
                  <p className="text-danger text-xs">
                    {errors.department.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Status
                </label>
                <select
                  {...register("status")}
                  className="border-border bg-card text-foreground focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                >
                  <option value="active">Active</option>
                  <option value="expiring_soon">Expiring Soon</option>
                  <option value="expired">Expired</option>
                  <option value="unused">Unused</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>

              <div className="space-y-2 md:col-span-2">
                <label className="text-foreground text-sm font-medium">
                  Notes
                </label>
                <textarea
                  {...register("notes")}
                  rows={3}
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 w-full rounded-lg border px-3 py-2 text-sm transition-colors outline-none focus:ring-1"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Saving..." : "Save Changes"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
