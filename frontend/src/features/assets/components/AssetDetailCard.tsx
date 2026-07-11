"use client";

import {
  Calendar,
  DollarSign,
  Building2,
  MapPin,
  Barcode,
  FileText,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  AssetStatusBadge,
  AssetConditionBadge,
  AssetWarrantyBadge,
} from "@/features/assets/components/AssetBadge";
import { formatCurrency, formatDate } from "@/lib/utils";
import type { Asset } from "@/features/assets/types/assets";

interface AssetDetailCardProps {
  asset: Asset;
}

interface DetailRowProps {
  icon?: React.ReactNode;
  label: string;
  value: string | React.ReactNode;
}

function DetailRow({ icon, label, value }: DetailRowProps) {
  return (
    <div className="flex items-start gap-3">
      {icon && (
        <div className="text-muted-foreground mt-0.5 shrink-0">{icon}</div>
      )}
      <div className="min-w-0 flex-1">
        <p className="text-muted-foreground text-xs">{label}</p>
        <div className="text-foreground mt-0.5 text-sm font-medium">
          {value}
        </div>
      </div>
    </div>
  );
}

export function AssetDetailCard({ asset }: AssetDetailCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{asset.name}</CardTitle>
            <p className="text-muted-foreground mt-0.5 text-sm">
              {asset.asset_code}
            </p>
          </div>
          <AssetStatusBadge status={asset.status} />
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-x-6 gap-y-5">
          <DetailRow
            icon={<Building2 size={14} />}
            label="Category"
            value={<span className="capitalize">{asset.category}</span>}
          />
          <DetailRow label="Brand" value={asset.brand} />
          <DetailRow label="Model" value={asset.model} />
          <DetailRow
            icon={<Barcode size={14} />}
            label="Serial Number"
            value={
              <span className="font-mono text-xs">{asset.serial_number}</span>
            }
          />
          <DetailRow
            icon={<Building2 size={14} />}
            label="Department"
            value={asset.department}
          />
          <DetailRow
            icon={<MapPin size={14} />}
            label="Location"
            value={asset.location}
          />
          <DetailRow
            icon={<DollarSign size={14} />}
            label="Purchase Price"
            value={formatCurrency(asset.purchase_price)}
          />
          <DetailRow label="Vendor" value={asset.vendor} />
          <DetailRow
            icon={<Calendar size={14} />}
            label="Purchase Date"
            value={asset.purchase_date}
          />
          <DetailRow
            icon={<Calendar size={14} />}
            label="Warranty End"
            value={asset.warranty_end}
          />
          <DetailRow
            label="Warranty Status"
            value={<AssetWarrantyBadge warranty={asset.warranty_status} />}
          />
          <DetailRow
            label="Condition"
            value={<AssetConditionBadge condition={asset.condition} />}
          />
        </div>

        <Separator />

        <div>
          <p className="text-muted-foreground mb-2 flex items-center gap-1.5 text-xs font-medium tracking-wider uppercase">
            <FileText size={12} />
            Description
          </p>
          <p className="text-foreground text-sm">
            {asset.description || "No description provided."}
          </p>
        </div>

        {asset.notes && (
          <>
            <Separator />
            <div>
              <p className="text-muted-foreground mb-2 text-xs font-medium tracking-wider uppercase">
                Notes
              </p>
              <p className="text-foreground text-sm">{asset.notes}</p>
            </div>
          </>
        )}

        <Separator />

        <div className="text-muted-foreground grid grid-cols-2 gap-4 text-xs">
          <div>
            <p>Created</p>
            <p className="text-foreground font-medium">
              {formatDate(asset.created_at)}
            </p>
          </div>
          <div>
            <p>Last Updated</p>
            <p className="text-foreground font-medium">
              {formatDate(asset.updated_at)}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
