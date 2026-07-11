"use client";

import { useState, useMemo, useCallback } from "react";
import { useRouter } from "next/navigation";
import { PageHeader } from "@/components/ui/page-header";
import { Button } from "@/components/ui/button";
import { Plus, Download } from "lucide-react";
import { SearchToolbar } from "@/features/software/components/SearchToolbar";
import { FilterSidebar } from "@/features/software/components/FilterSidebar";
import { SoftwareTable } from "@/features/software/components/SoftwareTable";
import { SoftwareTableSkeleton } from "@/features/software/components/SoftwareSkeleton";
import { useSoftware } from "@/features/software/services/software.service";
import type {
  SoftwareFilters,
  SoftwareColumn,
  SoftwareSort,
} from "@/features/software/types/software";

const defaultColumns: SoftwareColumn[] = [
  {
    key: "software_name",
    label: "Software Name",
    visible: true,
    sortable: true,
  },
  { key: "vendor", label: "Vendor", visible: true, sortable: true },
  { key: "category", label: "Category", visible: true, sortable: true },
  {
    key: "license_type",
    label: "License Type",
    visible: true,
    sortable: false,
  },
  { key: "total_licenses", label: "Purchased", visible: true, sortable: true },
  { key: "used_licenses", label: "Used", visible: true, sortable: true },
  {
    key: "available_licenses",
    label: "Available",
    visible: true,
    sortable: true,
  },
  { key: "monthly_cost", label: "Monthly Cost", visible: true, sortable: true },
  { key: "renewal_date", label: "Renewal Date", visible: true, sortable: true },
  { key: "department", label: "Department", visible: true, sortable: true },
  { key: "status", label: "Status", visible: true, sortable: true },
];

const initialFilters: SoftwareFilters = {
  search: "",
  vendor: [],
  category: [],
  department: [],
  status: [],
  renewalMonth: [],
};

export default function SoftwarePage() {
  const router = useRouter();
  const { data: software, isLoading } = useSoftware();

  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState<SoftwareFilters>(initialFilters);
  const [sort, setSort] = useState<SoftwareSort>({
    field: "software_name",
    direction: "asc",
  });
  const [columns, setColumns] = useState<SoftwareColumn[]>(defaultColumns);
  const [filterOpen, setFilterOpen] = useState(false);

  const filtered = useMemo(() => {
    if (!software) return [];
    let result = [...software];

    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (s) =>
          s.software_name.toLowerCase().includes(q) ||
          s.vendor.toLowerCase().includes(q) ||
          s.department.toLowerCase().includes(q),
      );
    }

    if (filters.vendor.length > 0) {
      result = result.filter((s) => filters.vendor.includes(s.vendor));
    }
    if (filters.category.length > 0) {
      result = result.filter((s) => filters.category.includes(s.category));
    }
    if (filters.department.length > 0) {
      result = result.filter((s) => filters.department.includes(s.department));
    }
    if (filters.status.length > 0) {
      result = result.filter((s) => filters.status.includes(s.status));
    }
    if (filters.renewalMonth.length > 0) {
      result = result.filter((s) => {
        const month = new Date(s.renewal_date).toLocaleString("en-US", {
          month: "short",
        });
        return filters.renewalMonth.includes(month);
      });
    }

    return result;
  }, [software, search, filters]);

  const handleColumnToggle = useCallback((key: string) => {
    setColumns((prev) =>
      prev.map((c) => (c.key === key ? { ...c, visible: !c.visible } : c)),
    );
  }, []);

  const filterActive =
    filters.vendor.length > 0 ||
    filters.category.length > 0 ||
    filters.department.length > 0 ||
    filters.status.length > 0 ||
    filters.renewalMonth.length > 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Software"
        description="Manage software titles, licenses, and renewals"
        actions={
          <>
            <Button variant="outline" size="sm" disabled>
              <Download size={14} />
              Export CSV
            </Button>
            <Button size="sm" onClick={() => router.push("/software/new")}>
              <Plus size={14} />
              Add Software
            </Button>
          </>
        }
      />

      <SearchToolbar
        search={search}
        onSearchChange={setSearch}
        columns={columns}
        onColumnToggle={handleColumnToggle}
        sort={sort}
        onSortChange={setSort}
        onFilterToggle={() => setFilterOpen(!filterOpen)}
        filterActive={filterActive}
      />

      <FilterSidebar
        isOpen={filterOpen}
        filters={filters}
        onFilterChange={setFilters}
        onClear={() => setFilters(initialFilters)}
        onClose={() => setFilterOpen(false)}
      />

      {isLoading ? (
        <SoftwareTableSkeleton />
      ) : (
        <SoftwareTable
          software={filtered}
          columns={columns}
          sort={sort}
          onSortChange={setSort}
        />
      )}
    </div>
  );
}
