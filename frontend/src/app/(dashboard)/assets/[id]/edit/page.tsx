"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AssetForm } from "@/features/assets/components/AssetForm";
import { AssetFormSkeleton } from "@/features/assets/components/AssetSkeleton";
import {
  useAsset,
  useUpdateAsset,
} from "@/features/assets/services/assets.service";
export default function EditAssetPage() {
  const params = useParams();
  const router = useRouter();
  const assetId = params.id as string;

  const { data: asset, isLoading } = useAsset(assetId);
  const { mutate: updateAsset, isPending } = useUpdateAsset();

  const handleSubmit = (data: Record<string, unknown>) => {
    if (!asset) return;
    updateAsset(
      { id: assetId, payload: data },
      {
        onSuccess: () => {
          router.push(`/assets/${assetId}`);
        },
      },
    );
  };

  if (isLoading) return <AssetFormSkeleton />;

  if (!asset) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <p className="text-foreground text-sm font-medium">Asset not found</p>
        <p className="text-muted-foreground mt-1 text-sm">
          The asset you&apos;re looking for doesn&apos;t exist.
        </p>
        <Link href="/assets">
          <Button variant="outline" size="sm" className="mt-4">
            Back to Assets
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href={`/assets/${assetId}`}>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <ChevronLeft size={16} />
          </Button>
        </Link>
        <div>
          <h1 className="text-foreground text-xl font-semibold tracking-tight">
            Edit Asset
          </h1>
          <p className="text-muted-foreground text-sm">
            Update information for {asset.name}
          </p>
        </div>
      </div>

      <AssetForm
        mode="edit"
        defaultValues={{
          name: asset.name,
          category: asset.category,
          brand: asset.brand,
          model: asset.model,
          serial_number: asset.serial_number,
          purchase_date: asset.purchase_date,
          purchase_price: asset.purchase_price,
          vendor: asset.vendor,
          warranty_end: asset.warranty_end,
          department: asset.department,
          location: asset.location,
          description: asset.description,
          condition: asset.condition,
          status: asset.status,
          notes: asset.notes,
        }}
        onSubmit={handleSubmit}
        isPending={isPending}
      />
    </div>
  );
}
