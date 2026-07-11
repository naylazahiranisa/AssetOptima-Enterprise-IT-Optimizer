"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import type {
  AssetStatus,
  AssetCondition,
  AssetCategory,
  AssetFilters,
} from "@/features/assets/types/assets";

const categories: AssetCategory[] = [
  "laptop",
  "desktop",
  "monitor",
  "tablet",
  "phone",
  "printer",
  "network",
  "peripheral",
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

const statuses: AssetStatus[] = [
  "available",
  "assigned",
  "maintenance",
  "lost",
  "retired",
];

const conditions: AssetCondition[] = ["new", "good", "fair", "poor", "damaged"];

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

const purchaseYears = ["2022", "2023", "2024"];

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

interface FilterBarProps {
  isOpen: boolean;
  filters: AssetFilters;
  onFilterChange: (filters: AssetFilters) => void;
  onClear: () => void;
  onClose: () => void;
}

export function FilterBar({
  isOpen,
  filters,
  onFilterChange,
  onClear,
  onClose,
}: FilterBarProps) {
  const updateFilter = <K extends keyof AssetFilters>(
    key: K,
    value: AssetFilters[K],
  ) => {
    onFilterChange({ ...filters, [key]: value });
  };

  const activeCount =
    filters.category.length +
    filters.department.length +
    filters.status.length +
    filters.location.length +
    filters.condition.length +
    filters.purchaseYear.length;

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
                  label="Category"
                  options={categories}
                  selected={filters.category as string[]}
                  onChange={(v) =>
                    updateFilter("category", v as AssetCategory[])
                  }
                />
                <FilterGroup
                  label="Department"
                  options={departments}
                  selected={filters.department}
                  onChange={(v) => updateFilter("department", v)}
                />
                <FilterGroup
                  label="Status"
                  options={statuses}
                  selected={filters.status as string[]}
                  onChange={(v) => updateFilter("status", v as AssetStatus[])}
                />
                <FilterGroup
                  label="Condition"
                  options={conditions}
                  selected={filters.condition as string[]}
                  onChange={(v) =>
                    updateFilter("condition", v as AssetCondition[])
                  }
                />
                <FilterGroup
                  label="Location"
                  options={locations}
                  selected={filters.location}
                  onChange={(v) => updateFilter("location", v)}
                />
                <FilterGroup
                  label="Purchase Year"
                  options={purchaseYears}
                  selected={filters.purchaseYear.map(String)}
                  onChange={(v) => updateFilter("purchaseYear", v.map(Number))}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
