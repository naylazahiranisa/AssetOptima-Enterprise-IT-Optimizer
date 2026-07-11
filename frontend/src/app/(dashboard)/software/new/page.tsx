"use client";

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
import { useCreateSoftware } from "@/features/software/services/software.service";

const softwareSchema = z.object({
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
  monthly_cost: z.coerce.number().min(0, "Cost cannot be negative"),
  annual_cost: z.coerce.number().min(0, "Cost cannot be negative"),
  renewal_date: z.string().min(1, "Renewal date is required"),
  department: z.string().min(1, "Department is required"),
  description: z.string().optional(),
});

type SoftwareFormData = z.infer<typeof softwareSchema>;

export default function NewSoftwarePage() {
  const router = useRouter();
  const createSoftware = useCreateSoftware();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SoftwareFormData>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(softwareSchema) as any,
    defaultValues: {
      category: "other",
      license_type: "subscription",
      total_licenses: 1,
      monthly_cost: 0,
      annual_cost: 0,
      department: "IT",
    },
  });

  const onSubmit = async (data: SoftwareFormData) => {
    try {
      await createSoftware.mutateAsync(data);
      router.push("/software");
    } catch {
      // handled by react-query
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Register Software"
        description="Add a new software title to your catalog"
        actions={
          <Button variant="outline" size="sm" onClick={() => router.back()}>
            <ArrowLeft size={14} />
            Back
          </Button>
        }
      />

      <Card>
        <CardHeader>
          <CardTitle>Software Information</CardTitle>
          <CardDescription>
            Enter the details of the software license
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
                  placeholder="e.g. Microsoft 365 Business Premium"
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
                  placeholder="e.g. Microsoft"
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
                  placeholder="150"
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
                  Department
                </label>
                <input
                  {...register("department")}
                  placeholder="e.g. Engineering"
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
                  Monthly Cost ($)
                </label>
                <input
                  type="number"
                  {...register("monthly_cost")}
                  placeholder="0"
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
                  placeholder="0"
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
                  Description (optional)
                </label>
                <input
                  {...register("description")}
                  placeholder="Brief description of the software"
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Saving..." : "Register Software"}
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
