"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AssetForm } from "@/features/assets/components/AssetForm";
import { useCreateAsset } from "@/features/assets/services/assets.service";
import type { CreateAssetPayload } from "@/features/assets/types/assets";

export default function NewAssetPage() {
  const router = useRouter();
  const { mutate: createAsset, isPending } = useCreateAsset();

  const handleSubmit = (data: Record<string, unknown>) => {
    createAsset(data as unknown as CreateAssetPayload, {
      onSuccess: () => {
        router.push("/assets");
      },
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/assets">
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <ChevronLeft size={16} />
          </Button>
        </Link>
        <div>
          <h1 className="text-foreground text-xl font-semibold tracking-tight">
            Register New Asset
          </h1>
          <p className="text-muted-foreground text-sm">
            Add a new asset to your IT inventory
          </p>
        </div>
      </div>

      <AssetForm mode="create" onSubmit={handleSubmit} isPending={isPending} />
    </div>
  );
}
