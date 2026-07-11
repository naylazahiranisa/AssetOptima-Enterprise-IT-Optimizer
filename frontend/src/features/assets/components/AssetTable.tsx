"use client";

import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  Eye,
  Edit,
  QrCode,
  MoreHorizontal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  AssetStatusBadge,
  AssetConditionBadge,
  AssetWarrantyBadge,
} from "@/features/assets/components/AssetBadge";
import { cn, formatDate, formatCurrency } from "@/lib/utils";
import type {
  Asset,
  AssetColumn,
  AssetSort,
  SortField,
  SortDirection,
} from "@/features/assets/types/assets";

interface AssetTableProps {
  assets: Asset[];
  isLoading?: boolean;
  columns: AssetColumn[];
  sort: AssetSort;
  onSortChange: (sort: AssetSort) => void;
}

const ITEMS_PER_PAGE = 10;

export function AssetTable({
  assets,
  columns,
  sort,
  onSortChange,
}: AssetTableProps) {
  const [page, setPage] = useState(0);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  const sorted = useMemo(() => {
    const sorted = [...assets].sort((a, b) => {
      const field = sort.field;
      const aVal = String(a[field as keyof Asset] ?? "");
      const bVal = String(b[field as keyof Asset] ?? "");
      const cmp = aVal.localeCompare(bVal);
      return sort.direction === "asc" ? cmp : -cmp;
    });
    return sorted;
  }, [assets, sort]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / ITEMS_PER_PAGE));
  const paginated = sorted.slice(
    page * ITEMS_PER_PAGE,
    (page + 1) * ITEMS_PER_PAGE,
  );

  const handleSort = (field: SortField) => {
    if (sort.field === field) {
      onSortChange({
        field,
        direction: sort.direction === "asc" ? "desc" : "asc",
      });
    } else {
      onSortChange({ field, direction: "asc" });
    }
  };

  if (assets.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-16">
          <p className="text-foreground text-sm font-medium">No assets found</p>
          <p className="text-muted-foreground mt-1 text-sm">
            Try adjusting your search or filters
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div>
      <div className="border-border bg-card shadow-card overflow-hidden rounded-xl border">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-border border-b">
                {columns
                  .filter((c) => c.visible)
                  .map((col) => (
                    <th
                      key={col.key}
                      className={cn(
                        "bg-muted/50 text-muted-foreground sticky top-0 px-4 py-3 text-left text-xs font-medium tracking-wider whitespace-nowrap uppercase",
                        col.sortable &&
                          "hover:text-foreground cursor-pointer select-none",
                      )}
                      onClick={() =>
                        col.sortable && handleSort(col.key as SortField)
                      }
                    >
                      <div className="flex items-center gap-1.5">
                        {col.label}
                        {col.sortable && (
                          <ArrowUpDown
                            size={12}
                            className={cn(
                              "shrink-0",
                              sort.field === col.key && "text-primary",
                            )}
                          />
                        )}
                      </div>
                    </th>
                  ))}
                <th className="bg-muted/50 sticky top-0 w-12 px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {paginated.map((asset, i) => (
                <motion.tr
                  key={asset.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.15, delay: i * 0.02 }}
                  className="border-border hover:bg-muted/30 group border-b transition-colors last:border-b-0"
                >
                  {columns
                    .filter((c) => c.visible)
                    .map((col) => (
                      <td key={col.key} className="px-4 py-3 text-sm">
                        <TableCell asset={asset} column={col.key} />
                      </td>
                    ))}
                  <td className="px-4 py-3">
                    <div className="relative flex items-center justify-end gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                      <Link href={`/assets/${asset.id}`}>
                        <Button variant="ghost" size="icon" className="h-7 w-7">
                          <Eye size={14} />
                        </Button>
                      </Link>
                      <Link href={`/assets/${asset.id}/edit`}>
                        <Button variant="ghost" size="icon" className="h-7 w-7">
                          <Edit size={14} />
                        </Button>
                      </Link>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={() =>
                          setOpenMenuId(
                            openMenuId === asset.id ? null : asset.id,
                          )
                        }
                      >
                        <MoreHorizontal size={14} />
                      </Button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <p className="text-muted-foreground text-sm">
          Showing {page * ITEMS_PER_PAGE + 1}–
          {Math.min((page + 1) * ITEMS_PER_PAGE, sorted.length)} of{" "}
          {sorted.length} assets
        </p>
        <div className="flex items-center gap-1">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            disabled={page === 0}
            onClick={() => setPage(page - 1)}
          >
            <ChevronLeft size={14} />
          </Button>
          {Array.from({ length: totalPages }).map((_, i) => (
            <Button
              key={i}
              variant={page === i ? "default" : "outline"}
              size="icon"
              className="h-8 w-8 text-xs"
              onClick={() => setPage(i)}
            >
              {i + 1}
            </Button>
          ))}
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            disabled={page >= totalPages - 1}
            onClick={() => setPage(page + 1)}
          >
            <ChevronRight size={14} />
          </Button>
        </div>
      </div>
    </div>
  );
}

function TableCell({ asset, column }: { asset: Asset; column: string }) {
  switch (column) {
    case "asset_code":
      return (
        <Link
          href={`/assets/${asset.id}`}
          className="text-primary font-medium hover:underline"
        >
          {asset.asset_code}
        </Link>
      );
    case "name":
      return (
        <Link
          href={`/assets/${asset.id}`}
          className="text-foreground hover:text-primary font-medium transition-colors"
        >
          {asset.name}
        </Link>
      );
    case "category":
      return (
        <span className="text-foreground capitalize">{asset.category}</span>
      );
    case "brand":
      return <span className="text-foreground">{asset.brand}</span>;
    case "model":
      return (
        <span className="text-muted-foreground text-xs">{asset.model}</span>
      );
    case "assigned_employee":
      return asset.assigned_to ? (
        <span className="text-foreground">{asset.assigned_to.name}</span>
      ) : (
        <span className="text-muted-foreground italic">—</span>
      );
    case "department":
      return <span className="text-foreground">{asset.department}</span>;
    case "location":
      return (
        <span className="text-muted-foreground text-xs">{asset.location}</span>
      );
    case "purchase_date":
      return (
        <span className="text-muted-foreground">{asset.purchase_date}</span>
      );
    case "warranty_status":
      return <AssetWarrantyBadge warranty={asset.warranty_status} />;
    case "condition":
      return <AssetConditionBadge condition={asset.condition} />;
    case "status":
      return <AssetStatusBadge status={asset.status} />;
    case "purchase_price":
      return (
        <span className="text-foreground font-medium">
          {formatCurrency(asset.purchase_price)}
        </span>
      );
    case "vendor":
      return <span className="text-foreground">{asset.vendor}</span>;
    default:
      return <span className="text-foreground">—</span>;
  }
}
