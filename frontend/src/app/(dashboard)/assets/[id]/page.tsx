"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ChevronLeft, Edit, UserPlus, Trash2 } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { AssetDetailCard } from "@/features/assets/components/AssetDetailCard";
import { AssetTimeline } from "@/features/assets/components/AssetTimeline";
import { QRPreview } from "@/features/assets/components/QRPreview";
import { AssignmentModal } from "@/features/assets/components/AssignmentModal";
import { AssetDetailSkeleton } from "@/features/assets/components/AssetSkeleton";
import {
  useAsset,
  useAssetLifecycle,
  useAssetMaintenance,
  useAssetAssignment,
  useAssignAsset,
  useDeleteAsset,
} from "@/features/assets/services/assets.service";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { Wrench } from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import type { AssetMaintenance } from "@/features/assets/types/assets";

export default function AssetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const assetId = params.id as string;

  const { data: asset, isLoading: assetLoading } = useAsset(assetId);
  const { data: lifecycle, isLoading: lifecycleLoading } =
    useAssetLifecycle(assetId);
  const { data: maintenances, isLoading: maintenanceLoading } =
    useAssetMaintenance(assetId);
  const { data: assignment } = useAssetAssignment(assetId);
  const { mutate: assignAsset, isPending: assignPending } = useAssignAsset();
  const { mutate: deleteAsset, isPending: deletePending } = useDeleteAsset();

  const [assignOpen, setAssignOpen] = useState(false);

  const handleAssign = (payload: {
    employee_id: string;
    assigned_date: string;
    expected_return?: string;
    notes?: string;
  }) => {
    assignAsset(
      { assetId, payload },
      { onSuccess: () => setAssignOpen(false) },
    );
  };

  const handleDelete = () => {
    if (!confirm("Are you sure you want to delete this asset?")) return;
    deleteAsset(assetId, {
      onSuccess: () => router.push("/assets"),
    });
  };

  if (assetLoading) return <AssetDetailSkeleton />;

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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/assets">
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <ChevronLeft size={16} />
            </Button>
          </Link>
          <div>
            <h1 className="text-foreground text-xl font-semibold tracking-tight">
              {asset.name}
            </h1>
            <p className="text-muted-foreground text-sm">{asset.asset_code}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="default"
            size="sm"
            onClick={() => setAssignOpen(true)}
            disabled={
              asset.status === "assigned" ||
              asset.status === "lost" ||
              asset.status === "retired"
            }
          >
            <UserPlus size={14} />
            Assign
          </Button>
          <Link href={`/assets/${asset.id}/edit`}>
            <Button variant="outline" size="sm">
              <Edit size={14} />
              Edit
            </Button>
          </Link>
          <Button
            variant="outline"
            size="sm"
            className="text-danger hover:text-danger"
            onClick={handleDelete}
            disabled={deletePending}
          >
            <Trash2 size={14} />
            Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <AssetDetailCard asset={asset} />

          <AssetTimeline events={lifecycle} isLoading={lifecycleLoading} />

          <Card>
            <CardHeader>
              <CardTitle>Maintenance History</CardTitle>
              <CardDescription>
                Scheduled and completed maintenance
              </CardDescription>
            </CardHeader>
            <CardContent>
              {maintenanceLoading ? (
                <div className="space-y-3">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex gap-3">
                      <Skeleton className="h-8 w-8 rounded-full" />
                      <div className="flex-1 space-y-2">
                        <Skeleton className="h-4 w-40" />
                        <Skeleton className="h-3 w-56" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : !maintenances || maintenances.length === 0 ? (
                <EmptyState
                  icon={<Wrench size={40} strokeWidth={1.5} />}
                  title="No maintenance records"
                  description="Maintenance history will appear here."
                />
              ) : (
                <div className="divide-border divide-y">
                  {maintenances.map((m: AssetMaintenance) => (
                    <div
                      key={m.id}
                      className="flex items-start justify-between gap-4 py-3 first:pt-0 last:pb-0"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="text-foreground text-sm font-medium">
                          {m.type}
                        </p>
                        <p className="text-muted-foreground mt-0.5 text-xs">
                          {m.description}
                        </p>
                        <div className="text-muted-foreground/60 mt-1 flex items-center gap-3 text-xs">
                          <span>Scheduled: {m.scheduled_date}</span>
                          {m.completed_date && (
                            <>
                              <span>·</span>
                              <span>Completed: {m.completed_date}</span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="shrink-0 text-right">
                        <span
                          className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${
                            m.status === "completed"
                              ? "bg-success/10 text-success"
                              : m.status === "in_progress"
                                ? "bg-warning/10 text-warning"
                                : m.status === "scheduled"
                                  ? "bg-primary/10 text-primary"
                                  : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {m.status.replace("_", " ")}
                        </span>
                        {m.cost && (
                          <p className="text-muted-foreground mt-1 text-xs">
                            {formatCurrency(m.cost)}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <QRPreview assetCode={asset.asset_code} assetName={asset.name} />

          {assignment && (
            <Card>
              <CardHeader>
                <CardTitle>Current Assignment</CardTitle>
                <CardDescription>Assigned employee details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-muted-foreground text-xs">Employee</p>
                  <p className="text-foreground text-sm font-medium">
                    {assignment.employee.name}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs">Department</p>
                  <p className="text-foreground text-sm">
                    {assignment.employee.department}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground text-xs">Assigned Date</p>
                  <p className="text-foreground text-sm">
                    {assignment.assigned_date}
                  </p>
                </div>
                {assignment.expected_return && (
                  <div>
                    <p className="text-muted-foreground text-xs">
                      Expected Return
                    </p>
                    <p className="text-foreground text-sm">
                      {assignment.expected_return}
                    </p>
                  </div>
                )}
                {assignment.notes && (
                  <div>
                    <p className="text-muted-foreground text-xs">Notes</p>
                    <p className="text-foreground text-sm">
                      {assignment.notes}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <AssignmentModal
        isOpen={assignOpen}
        onClose={() => setAssignOpen(false)}
        onAssign={handleAssign}
        isPending={assignPending}
        assetName={asset.name}
      />
    </div>
  );
}
