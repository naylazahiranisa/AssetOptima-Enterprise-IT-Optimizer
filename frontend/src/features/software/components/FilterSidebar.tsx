"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import type {
  SoftwareCategory,
  LicenseStatus,
  SoftwareFilters,
} from "@/features/software/types/software";

const vendors = [
  "Microsoft",
  "Adobe",
  "JetBrains",
  "Salesforce",
  "CrowdStrike",
  "GitHub",
  "Atlassian",
  "Zoom",
  "McAfee",
];

const categories: SoftwareCategory[] = [
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
];

const departments = [
  "All Departments",
  "Engineering",
  "Design",
  "Marketing",
  "Finance",
  "IT",
  "Sales",
  "Analytics",
  "HR",
  "Operations",
];

const statuses: LicenseStatus[] = [
  "active",
  "expired",
  "expiring_soon",
  "unused",
  "suspended",
];

const renewalMonths = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

interface FilterGroupProps {
  label: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

function FilterGroup({ label, options, selected, onChange }: FilterGroupProps) {
  return (
    <div className="space-y-2">
      <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
        {label}
      </p>
      <div className="flex flex-wrap gap-1.5">
        {options.map((option) => {
          const isActive = selected.includes(option);
          return (
            <button
              key={option}
              type="button"
              onClick={() =>
                onChange(
                  isActive
                    ? selected.filter((s) => s !== option)
                    : [...selected, option],
                )
              }
              className={cn(
                "rounded-md border px-2.5 py-1 text-xs font-medium transition-all",
                isActive
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:border-primary/30 hover:text-foreground",
              )}
            >
              {option
                .replace(/_/g, " ")
                .replace(/\b\w/g, (l) => l.toUpperCase())}
            </button>
          );
        })}
      </div>
    </div>
  );
}

interface FilterSidebarProps {
  isOpen: boolean;
  filters: SoftwareFilters;
  onFilterChange: (filters: SoftwareFilters) => void;
  onClear: () => void;
  onClose: () => void;
}

export function FilterSidebar({
  isOpen,
  filters,
  onFilterChange,
  onClear,
  onClose,
}: FilterSidebarProps) {
  const updateFilter = <K extends keyof SoftwareFilters>(
    key: K,
    value: SoftwareFilters[K],
  ) => {
    onFilterChange({ ...filters, [key]: value });
  };

  const activeCount =
    filters.vendor.length +
    filters.category.length +
    filters.department.length +
    filters.status.length +
    filters.renewalMonth.length;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden"
        >
          <Card>
            <CardContent className="p-5">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium">Filters</p>
                  {activeCount > 0 && (
                    <Badge variant="primary" className="h-5 px-1.5 text-xs">
                      {activeCount}
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  {activeCount > 0 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={onClear}
                      className="h-7 text-xs"
                    >
                      <X size={12} />
                      Clear all
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onClose}
                    className="h-7 text-xs"
                  >
                    <X size={12} />
                    Close
                  </Button>
                </div>
              </div>

              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                <FilterGroup
                  label="Vendor"
                  options={vendors}
                  selected={filters.vendor}
                  onChange={(v) => updateFilter("vendor", v)}
                />
                <FilterGroup
                  label="Category"
                  options={categories}
                  selected={filters.category as string[]}
                  onChange={(v) =>
                    updateFilter("category", v as SoftwareCategory[])
                  }
                />
                <FilterGroup
                  label="Department"
                  options={departments}
                  selected={filters.department}
                  onChange={(v) => updateFilter("department", v)}
                />
                <FilterGroup
                  label="License Status"
                  options={statuses}
                  selected={filters.status as string[]}
                  onChange={(v) => updateFilter("status", v as LicenseStatus[])}
                />
                <FilterGroup
                  label="Renewal Month"
                  options={renewalMonths}
                  selected={filters.renewalMonth}
                  onChange={(v) => updateFilter("renewalMonth", v)}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
