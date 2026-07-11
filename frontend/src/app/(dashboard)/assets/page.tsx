"use client";

import { useState, useMemo, useCallback } from "react";
import Link from "next/link";
import { Plus, LayoutGrid, List } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { SearchToolbar } from "@/features/assets/components/SearchToolbar";
import { FilterBar } from "@/features/assets/components/FilterBar";
import { AssetTable } from "@/features/assets/components/AssetTable";
import { AssetCard } from "@/features/assets/components/AssetCard";
import { AssetTableSkeleton } from "@/features/assets/components/AssetSkeleton";
import { useAssets } from "@/features/assets/services/assets.service";
import type {
  AssetColumn,
  AssetFilters,
  AssetSort,
  SortField,
} from "@/features/assets/types/assets";
import { cn } from "@/lib/utils";

const defaultColumns: AssetColumn[] = [
  { key: "asset_code", label: "Code", visible: true, sortable: true },
  { key: "name", label: "Asset Name", visible: true, sortable: true },
  { key: "category", label: "Category", visible: true, sortable: false },
  { key: "brand", label: "Brand", visible: true, sortable: false },
  { key: "model", label: "Model", visible: false, sortable: false },
  {
    key: "assigned_employee",
    label: "Assigned To",
    visible: true,
    sortable: false,
  },
  { key: "department", label: "Department", visible: true, sortable: true },
  { key: "location", label: "Location", visible: false, sortable: false },
  {
    key: "purchase_date",
    label: "Purchase Date",
    visible: true,
    sortable: true,
  },
  { key: "purchase_price", label: "Price", visible: false, sortable: false },
  { key: "vendor", label: "Vendor", visible: false, sortable: false },
  { key: "warranty_status", label: "Warranty", visible: true, sortable: false },
  { key: "condition", label: "Condition", visible: true, sortable: false },
  { key: "status", label: "Status", visible: true, sortable: true },
];

const defaultFilters: AssetFilters = {
  search: "",
  category: [],
  department: [],
  status: [],
  location: [],
  condition: [],
  purchaseYear: [],
};

export default function AssetsPage() {
  const { data: assets, isLoading, refetch } = useAssets();

  const [viewMode, setViewMode] = useState<"table" | "grid">("table");
  const [columns, setColumns] = useState<AssetColumn[]>(defaultColumns);
  const [sort, setSort] = useState<AssetSort>({
    field: "purchase_date",
    direction: "desc",
  });
  const [filters, setFilters] = useState<AssetFilters>(defaultFilters);
  const [filterOpen, setFilterOpen] = useState(false);

  const filterActive =
    filters.category.length > 0 ||
    filters.department.length > 0 ||
    filters.status.length > 0 ||
    filters.location.length > 0 ||
    filters.condition.length > 0 ||
    filters.purchaseYear.length > 0;

  const filtered = useMemo(() => {
    if (!assets) return [];
    let result = [...assets];

    if (filters.search) {
      const q = filters.search.toLowerCase();
      result = result.filter(
        (a) =>
          a.asset_code.toLowerCase().includes(q) ||
          a.name.toLowerCase().includes(q) ||
          a.serial_number.toLowerCase().includes(q) ||
          a.brand.toLowerCase().includes(q) ||
          a.model.toLowerCase().includes(q) ||
          a.department.toLowerCase().includes(q) ||
          a.location.toLowerCase().includes(q),
      );
    }

    if (filters.category.length > 0) {
      result = result.filter((a) => filters.category.includes(a.category));
    }
    if (filters.department.length > 0) {
      result = result.filter((a) => filters.department.includes(a.department));
    }
    if (filters.status.length > 0) {
      result = result.filter((a) => filters.status.includes(a.status));
    }
    if (filters.location.length > 0) {
      result = result.filter((a) => filters.location.includes(a.location));
    }
    if (filters.condition.length > 0) {
      result = result.filter((a) => filters.condition.includes(a.condition));
    }
    if (filters.purchaseYear.length > 0) {
      result = result.filter((a) =>
        filters.purchaseYear.includes(new Date(a.purchase_date).getFullYear()),
      );
    }

    return result;
  }, [assets, filters]);

  const handleColumnToggle = useCallback((key: string) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.key === key ? { ...col, visible: !col.visible } : col,
      ),
    );
  }, []);

  const handleFilterChange = useCallback((newFilters: AssetFilters) => {
    setFilters(newFilters);
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters(defaultFilters);
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Assets"
        description="Manage your IT asset inventory"
        actions={
          <div className="flex items-center gap-2">
            <div className="bg-muted border-border flex items-center rounded-lg border p-0.5">
              <button
                type="button"
                onClick={() => setViewMode("table")}
                className={cn(
                  "rounded-md p-1.5 transition-colors",
                  viewMode === "table"
                    ? "bg-card text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                <List size={14} />
              </button>
              <button
                type="button"
                onClick={() => setViewMode("grid")}
                className={cn(
                  "rounded-md p-1.5 transition-colors",
                  viewMode === "grid"
                    ? "bg-card text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                <LayoutGrid size={14} />
              </button>
            </div>
            <Button size="sm" asChild>
              <Link href="/assets/new">
                <Plus size={14} />
                Add Asset
              </Link>
            </Button>
          </div>
        }
      />

      <SearchToolbar
        search={filters.search}
        onSearchChange={(search) => setFilters((prev) => ({ ...prev, search }))}
        columns={columns}
        onColumnToggle={handleColumnToggle}
        sort={sort}
        onSortChange={setSort}
        onFilterToggle={() => setFilterOpen(!filterOpen)}
        filterActive={filterActive}
      />

      <FilterBar
        isOpen={filterOpen}
        filters={filters}
        onFilterChange={handleFilterChange}
        onClear={handleClearFilters}
        onClose={() => setFilterOpen(false)}
      />

      {isLoading ? (
        <AssetTableSkeleton />
      ) : viewMode === "table" ? (
        <AssetTable
          assets={filtered}
          columns={columns}
          sort={sort}
          onSortChange={setSort}
        />
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((asset, i) => (
            <AssetCard key={asset.id} asset={asset} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
