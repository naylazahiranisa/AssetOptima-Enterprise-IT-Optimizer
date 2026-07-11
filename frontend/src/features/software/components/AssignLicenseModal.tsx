"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import { X, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAssignLicense } from "@/features/software/services/software.service";

const assignSchema = z.object({
  employee_name: z.string().min(1, "Employee name is required"),
  employee_email: z.string().email("Valid email is required"),
  employee_department: z.string().min(1, "Department is required"),
  assigned_date: z.string().min(1, "Date is required"),
  license_key: z.string().optional(),
  notes: z.string().optional(),
});

type AssignFormData = z.infer<typeof assignSchema>;

interface AssignLicenseModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  softwareId: string;
  softwareName: string;
}

export function AssignLicenseModal({
  open,
  onOpenChange,
  softwareId,
  softwareName,
}: AssignLicenseModalProps) {
  const assignLicense = useAssignLicense();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AssignFormData>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(assignSchema) as any,
    defaultValues: {
      assigned_date: new Date().toISOString().split("T")[0],
    },
  });

  const onSubmit = async (data: AssignFormData) => {
    try {
      await assignLicense.mutateAsync({ softwareId, payload: data });
      reset();
      onOpenChange(false);
    } catch {
      // handled by react-query
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="bg-foreground/20 absolute inset-0 backdrop-blur-sm"
            onClick={() => onOpenChange(false)}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.15 }}
            className="bg-card border-border shadow-elevated relative z-10 mx-4 w-full max-w-md rounded-xl border"
          >
            <div className="border-border flex items-center justify-between border-b px-6 py-4">
              <div className="flex items-center gap-2">
                <Users size={16} className="text-primary" />
                <h2 className="text-foreground text-base font-semibold">
                  Assign License
                </h2>
              </div>
              <button
                onClick={() => onOpenChange(false)}
                className="text-muted-foreground hover:text-foreground rounded-md p-1"
              >
                <X size={16} />
              </button>
            </div>

            <div className="px-6 py-2">
              <p className="text-muted-foreground text-sm">
                Assigning license for{" "}
                <span className="text-foreground font-medium">
                  {softwareName}
                </span>
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="px-6 pt-2 pb-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-foreground text-sm font-medium">
                    Employee Name
                  </label>
                  <input
                    {...register("employee_name")}
                    placeholder="e.g. John Doe"
                    className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                  />
                  {errors.employee_name && (
                    <p className="text-danger text-xs">
                      {errors.employee_name.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-foreground text-sm font-medium">
                    Employee Email
                  </label>
                  <input
                    type="email"
                    {...register("employee_email")}
                    placeholder="john@company.com"
                    className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                  />
                  {errors.employee_email && (
                    <p className="text-danger text-xs">
                      {errors.employee_email.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-foreground text-sm font-medium">
                    Department
                  </label>
                  <input
                    {...register("employee_department")}
                    placeholder="e.g. Engineering"
                    className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                  />
                  {errors.employee_department && (
                    <p className="text-danger text-xs">
                      {errors.employee_department.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-foreground text-sm font-medium">
                    Assign Date
                  </label>
                  <input
                    type="date"
                    {...register("assigned_date")}
                    className="border-border bg-card text-foreground focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                  />
                  {errors.assigned_date && (
                    <p className="text-danger text-xs">
                      {errors.assigned_date.message}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-foreground text-sm font-medium">
                    License Key{" "}
                    <span className="text-muted-foreground">(optional)</span>
                  </label>
                  <input
                    {...register("license_key")}
                    placeholder="e.g. ABC-123-XYZ"
                    className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-foreground text-sm font-medium">
                    Notes{" "}
                    <span className="text-muted-foreground">(optional)</span>
                  </label>
                  <textarea
                    {...register("notes")}
                    rows={2}
                    placeholder="Any additional notes"
                    className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 w-full rounded-lg border px-3 py-2 text-sm transition-colors outline-none focus:ring-1"
                  />
                </div>
              </div>

              <div className="mt-6 flex items-center justify-end gap-3">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => onOpenChange(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" size="sm" disabled={isSubmitting}>
                  {isSubmitting ? "Assigning..." : "Assign License"}
                </Button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
