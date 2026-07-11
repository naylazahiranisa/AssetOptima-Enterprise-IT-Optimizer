"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import { Eye, Edit, Monitor } from "lucide-react";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  AssetStatusBadge,
  AssetConditionBadge,
} from "@/features/assets/components/AssetBadge";
import { formatCurrency } from "@/lib/utils";
import type { Asset } from "@/features/assets/types/assets";

interface AssetCardProps {
  asset: Asset;
  index?: number;
}

export function AssetCard({ asset, index = 0 }: AssetCardProps) {
  const router = useRouter();

  const handleCardClick = () => {
    router.push(`/assets/${asset.id}`);
  };

  const handleButtonClick = (e: React.MouseEvent, href: string) => {
    e.stopPropagation();
    router.push(href);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.03 }}
    >
      <div
        onClick={handleCardClick}
        className="group block cursor-pointer"
        role="link"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") handleCardClick();
        }}
      >
        <Card className="hover:shadow-elevated transition-all duration-200">
          <CardContent className="p-5">
            <div className="flex items-start justify-between">
              <div className="bg-primary/10 text-primary rounded-lg p-2.5">
                <Monitor size={16} />
              </div>
              <AssetStatusBadge status={asset.status} />
            </div>

            <div className="mt-4 space-y-1">
              <p className="text-foreground group-hover:text-primary text-sm font-semibold transition-colors">
                {asset.name}
              </p>
              <p className="text-muted-foreground text-xs">
                {asset.asset_code}
              </p>
            </div>

            <div className="text-muted-foreground mt-3 flex items-center gap-2 text-xs">
              <span>{asset.brand}</span>
              <span>·</span>
              <span>{asset.model}</span>
            </div>

            <div className="border-border/50 mt-3 flex items-center justify-between border-t pt-3 text-xs">
              <div className="space-y-0.5">
                <p className="text-muted-foreground">Assigned to</p>
                <p className="text-foreground font-medium">
                  {asset.assigned_to?.name ?? "—"}
                </p>
              </div>
              <div className="space-y-0.5 text-right">
                <p className="text-muted-foreground">Value</p>
                <p className="text-foreground font-medium">
                  {formatCurrency(asset.purchase_price)}
                </p>
              </div>
            </div>
          </CardContent>

          <CardFooter className="border-border/50 flex gap-2 border-t px-5 py-3">
            <div className="flex-1">
              <Button
                variant="outline"
                size="sm"
                className="w-full gap-1.5 text-xs"
                onClick={(e) => handleButtonClick(e, `/assets/${asset.id}`)}
              >
                <Eye size={12} />
                View
              </Button>
            </div>
            <div className="flex-1">
              <Button
                variant="outline"
                size="sm"
                className="w-full gap-1.5 text-xs"
                onClick={(e) =>
                  handleButtonClick(e, `/assets/${asset.id}/edit`)
                }
              >
                <Edit size={12} />
                Edit
              </Button>
            </div>
          </CardFooter>
        </Card>
      </div>
    </motion.div>
  );
}
