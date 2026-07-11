"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type {
  AssetCategory,
  AssetCondition,
  AssetStatus,
} from "@/features/assets/types/assets";

const formSchema = z.object({
  asset_code: z.string().optional(),
  name: z.string().min(1, "Asset name is required"),
  category: z.string().min(1, "Category is required"),
  brand: z.string().min(1, "Brand is required"),
  model: z.string().min(1, "Model is required"),
  serial_number: z.string().min(1, "Serial number is required"),
  purchase_date: z.string().min(1, "Purchase date is required"),
  purchase_price: z.coerce.number().min(0, "Price must be positive"),
  vendor: z.string().min(1, "Vendor is required"),
  warranty_end: z.string().min(1, "Warranty end date is required"),
  department: z.string().min(1, "Department is required"),
  location: z.string().min(1, "Location is required"),
  description: z.string().optional(),
  condition: z.string().optional(),
  status: z.string().optional(),
  notes: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

interface AssetFormProps {
  mode: "create" | "edit";
  defaultValues?: Partial<FormData>;
  onSubmit: (data: Record<string, unknown>) => void;
  isPending?: boolean;
}

const categories: { value: AssetCategory; label: string }[] = [
  { value: "laptop", label: "Laptop" },
  { value: "desktop", label: "Desktop" },
  { value: "monitor", label: "Monitor" },
  { value: "tablet", label: "Tablet" },
  { value: "phone", label: "Phone" },
  { value: "printer", label: "Printer" },
  { value: "network", label: "Network" },
  { value: "peripheral", label: "Peripheral" },
  { value: "other", label: "Other" },
];

const departments = [
  "Engineering",
  "Design",
  "Marketing",
  "Finance",
  "IT",
  "HR",
  "Operations",
];

const conditions: { value: AssetCondition; label: string }[] = [
  { value: "new", label: "New" },
  { value: "good", label: "Good" },
  { value: "fair", label: "Fair" },
  { value: "poor", label: "Poor" },
  { value: "damaged", label: "Damaged" },
];

const statuses: { value: AssetStatus; label: string }[] = [
  { value: "available", label: "Available" },
  { value: "assigned", label: "Assigned" },
  { value: "maintenance", label: "Maintenance" },
  { value: "lost", label: "Lost" },
  { value: "retired", label: "Retired" },
];

const locations = [
  "Floor 1 - Lobby",
  "Floor 2 - Studio",
  "Floor 3 - East Wing",
  "Floor 3 - IT Dept",
  "Floor 4 - North",
  "Floor 4 - Finance",
  "Lab A",
  "Server Room B",
];

function getError(field: unknown): string | undefined {
  if (field && typeof field === "object" && "message" in field) {
    const msg = (field as { message: unknown }).message;
    return typeof msg === "string" ? msg : undefined;
  }
  return undefined;
}

interface FieldProps {
  label: string;
  error?: string | undefined;
  children: React.ReactNode;
}

function Field({ label, error, children }: FieldProps) {
  return (
    <div className="space-y-1.5">
      <label className="text-foreground text-sm font-medium">{label}</label>
      {children}
      {error && <p className="text-danger text-xs">{error}</p>}
    </div>
  );
}

export function AssetForm({
  mode,
  defaultValues,
  onSubmit,
  isPending,
}: AssetFormProps) {
  const isCreate = mode === "create";

  const {
    register,
    handleSubmit,
    formState: { errors },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } = useForm<any>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      ...defaultValues,
      ...(isCreate ? { asset_code: "" } : {}),
    },
  });

  const inputClass = cn(
    "border-border bg-card text-foreground placeholder:text-muted-foreground/60 h-9 w-full rounded-lg border px-3 text-sm outline-none",
    "transition-colors focus:border-primary/50 focus:ring-1 focus:ring-primary/20",
  );

  const selectClass = inputClass;
  const textareaClass = cn(inputClass, "h-20 resize-none py-2");

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <form
        onSubmit={handleSubmit((data) => {
          const cleaned = Object.fromEntries(
            Object.entries(data).filter(([, v]) => v !== undefined && v !== ""),
          );
          onSubmit(cleaned as Record<string, unknown>);
        })}
      >
        <Card>
          <CardHeader>
            <CardTitle>
              {isCreate ? "Register New Asset" : "Edit Asset"}
            </CardTitle>
            <CardDescription>
              {isCreate
                ? "Add a new asset to your inventory"
                : "Update asset information"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-5 md:grid-cols-2">
              {isCreate && (
                <Field label="Asset Code" error={getError(errors.asset_code)}>
                  <input
                    {...register("asset_code", { required: isCreate })}
                    placeholder="AST-2024-001"
                    className={inputClass}
                  />
                </Field>
              )}

              <Field label="Asset Name" error={getError(errors.name)}>
                <input
                  {...register("name")}
                  placeholder='MacBook Pro 14" M4'
                  className={inputClass}
                />
              </Field>

              <Field label="Category" error={getError(errors.category)}>
                <select {...register("category")} className={selectClass}>
                  <option value="">Select category...</option>
                  {categories.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Brand" error={getError(errors.brand)}>
                <input
                  {...register("brand")}
                  placeholder="Apple"
                  className={inputClass}
                />
              </Field>

              <Field label="Model" error={getError(errors.model)}>
                <input
                  {...register("model")}
                  placeholder='MacBook Pro 14" M4'
                  className={inputClass}
                />
              </Field>

              <Field
                label="Serial Number"
                error={getError(errors.serial_number)}
              >
                <input
                  {...register("serial_number")}
                  placeholder="SN-MBP-001-2024"
                  className={inputClass}
                />
              </Field>

              <Field
                label="Purchase Date"
                error={getError(errors.purchase_date)}
              >
                <input
                  type="date"
                  {...register("purchase_date")}
                  className={inputClass}
                />
              </Field>

              <Field
                label="Purchase Price ($)"
                error={getError(errors.purchase_price)}
              >
                <input
                  type="number"
                  step="0.01"
                  {...register("purchase_price")}
                  placeholder="2499"
                  className={inputClass}
                />
              </Field>

              <Field label="Vendor" error={getError(errors.vendor)}>
                <input
                  {...register("vendor")}
                  placeholder="Apple Inc."
                  className={inputClass}
                />
              </Field>

              <Field label="Warranty End" error={getError(errors.warranty_end)}>
                <input
                  type="date"
                  {...register("warranty_end")}
                  className={inputClass}
                />
              </Field>

              <Field label="Department" error={getError(errors.department)}>
                <select {...register("department")} className={selectClass}>
                  <option value="">Select department...</option>
                  {departments.map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Location" error={getError(errors.location)}>
                <select {...register("location")} className={selectClass}>
                  <option value="">Select location...</option>
                  {locations.map((l) => (
                    <option key={l} value={l}>
                      {l}
                    </option>
                  ))}
                </select>
              </Field>
            </div>

            {!isCreate && (
              <div className="grid gap-5 md:grid-cols-2">
                <Field label="Condition">
                  <select
                    {...register("condition")}
                    className={selectClass}
                    defaultValue={defaultValues?.condition ?? "good"}
                  >
                    {conditions.map((c) => (
                      <option key={c.value} value={c.value}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </Field>

                <Field label="Status">
                  <select
                    {...register("status")}
                    className={selectClass}
                    defaultValue={defaultValues?.status ?? "available"}
                  >
                    {statuses.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>
            )}

            <Field label="Description">
              <textarea
                {...register("description")}
                placeholder="Describe the asset, its purpose, and any relevant details..."
                className={textareaClass}
              />
            </Field>

            {!isCreate && (
              <Field label="Notes">
                <textarea
                  {...register("notes")}
                  placeholder="Internal notes about this asset..."
                  className={textareaClass}
                />
              </Field>
            )}
          </CardContent>
          <CardFooter className="flex items-center justify-between">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => window.history.back()}
            >
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={isPending}>
              {isPending
                ? isCreate
                  ? "Registering..."
                  : "Saving..."
                : isCreate
                  ? "Register Asset"
                  : "Save Changes"}
            </Button>
          </CardFooter>
        </Card>
      </form>
    </motion.div>
  );
}
