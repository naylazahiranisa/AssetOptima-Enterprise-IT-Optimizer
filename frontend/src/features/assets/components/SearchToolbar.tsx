"use client";

import {
  Search,
  SlidersHorizontal,
  ArrowUpDown,
  Columns3,
  Check,
  X,
} from "lucide-react";
import { motion } from "framer-motion";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type {
  AssetColumn,
  AssetSort,
  SortField,
  SortDirection,
} from "@/features/assets/types/assets";

interface SearchToolbarProps {
  search: string;
  onSearchChange: (value: string) => void;
  columns: AssetColumn[];
  onColumnToggle: (key: string) => void;
  sort: AssetSort;
  onSortChange: (sort: AssetSort) => void;
  onFilterToggle: () => void;
  filterActive: boolean;
}

const sortOptions: { field: SortField; label: string }[] = [
  { field: "asset_code", label: "Asset Code" },
  { field: "name", label: "Name" },
  { field: "department", label: "Department" },
  { field: "purchase_date", label: "Purchase Date" },
  { field: "status", label: "Status" },
];

export function SearchToolbar({
  search,
  onSearchChange,
  columns,
  onColumnToggle,
  sort,
  onSortChange,
  onFilterToggle,
  filterActive,
}: SearchToolbarProps) {
  const [showColumns, setShowColumns] = useState(false);
  const [showSort, setShowSort] = useState(false);

  const visibleCount = columns.filter((c) => c.visible).length;

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="flex flex-wrap items-center gap-2"
    >
      <div className="relative min-w-[200px] flex-1">
        <Search
          size={14}
          className="text-muted-foreground pointer-events-none absolute top-1/2 left-3 -translate-y-1/2"
        />
        <input
          type="text"
          placeholder="Search assets by name, code, serial number..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border pr-8 pl-9 text-sm transition-colors outline-none focus:ring-1"
        />
        {search && (
          <button
            type="button"
            onClick={() => onSearchChange("")}
            className="text-muted-foreground hover:text-foreground absolute top-1/2 right-2.5 -translate-y-1/2"
          >
            <X size={14} />
          </button>
        )}
      </div>

      <Button
        variant={filterActive ? "default" : "outline"}
        size="sm"
        onClick={onFilterToggle}
        className="h-9"
      >
        <SlidersHorizontal size={14} />
        Filters
        {filterActive && (
          <span className="bg-primary-foreground text-primary ml-1 flex h-4 w-4 items-center justify-center rounded-full text-[10px] font-bold">
            {columns.filter((c) => c.visible).length === 0 ? 0 : 1}
          </span>
        )}
      </Button>

      <div className="relative">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowSort(!showSort)}
          className="h-9"
        >
          <ArrowUpDown size={14} />
          {sortOptions.find((o) => o.field === sort.field)?.label ?? "Sort"}
        </Button>
        {showSort && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setShowSort(false)}
            />
            <div className="bg-card border-border shadow-elevated absolute right-0 z-50 mt-1 w-44 rounded-lg border py-1">
              {sortOptions.map((option) => {
                const isActive = sort.field === option.field;
                return (
                  <div key={option.field} className="px-1">
                    <button
                      type="button"
                      onClick={() => {
                        if (isActive) {
                          onSortChange({
                            field: option.field,
                            direction:
                              sort.direction === "asc" ? "desc" : "asc",
                          });
                        } else {
                          onSortChange({
                            field: option.field,
                            direction: "asc",
                          });
                        }
                        setShowSort(false);
                      }}
                      className={cn(
                        "flex w-full items-center justify-between rounded-md px-3 py-1.5 text-left text-sm transition-colors",
                        isActive
                          ? "bg-primary/10 text-primary"
                          : "text-foreground hover:bg-muted",
                      )}
                    >
                      {option.label}
                      {isActive && (
                        <span className="text-xs">
                          {sort.direction === "asc" ? "↑" : "↓"}
                        </span>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      <div className="relative">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowColumns(!showColumns)}
          className="h-9"
        >
          <Columns3 size={14} />
          Columns
          <span className="text-muted-foreground ml-1 text-xs">
            {visibleCount}
          </span>
        </Button>
        {showColumns && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setShowColumns(false)}
            />
            <div className="bg-card border-border shadow-elevated absolute right-0 z-50 mt-1 w-48 rounded-lg border py-1">
              {columns.map((col) => (
                <button
                  key={col.key}
                  type="button"
                  onClick={() => onColumnToggle(col.key)}
                  className="hover:bg-muted flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm"
                >
                  <div
                    className={cn(
                      "border-border flex h-4 w-4 items-center justify-center rounded border transition-colors",
                      col.visible && "bg-primary border-primary",
                    )}
                  >
                    {col.visible && (
                      <Check size={10} className="text-primary-foreground" />
                    )}
                  </div>
                  <span className="text-foreground">{col.label}</span>
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </motion.div>
  );
}
