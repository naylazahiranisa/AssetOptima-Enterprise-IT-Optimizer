"use client";

import { useAuth } from "@/hooks/useAuth";
import { DashboardHeader } from "@/features/dashboard/components/DashboardHeader";
import { StatCard } from "@/features/dashboard/components/StatCard";
import { AssetStatusChart } from "@/features/dashboard/components/AssetStatusChart";
import { SoftwareUsageChart } from "@/features/dashboard/components/SoftwareUsageChart";
import { AiInsightCard } from "@/features/dashboard/components/AiInsightCard";
import { ActivityTimeline } from "@/features/dashboard/components/ActivityTimeline";
import { NotificationPanel } from "@/features/dashboard/components/NotificationPanel";
import { QuickActions } from "@/features/dashboard/components/QuickActions";
import {
  useDashboardKpis,
  useAssetStatus,
  useSoftwareUsage,
  useAiInsight,
  useActivityFeed,
  useDashboardNotifications,
  useQuickActions,
} from "@/features/dashboard/api/useDashboard";

export default function DashboardPage() {
  const { user } = useAuth();

  const {
    data: kpis,
    isLoading: kpisLoading,
    refetch: refetchKpis,
  } = useDashboardKpis();

  const {
    data: assetStatus,
    isLoading: assetStatusLoading,
    isError: assetStatusError,
    refetch: refetchAssetStatus,
  } = useAssetStatus();

  const {
    data: softwareUsage,
    isLoading: softwareUsageLoading,
    isError: softwareUsageError,
    refetch: refetchSoftwareUsage,
  } = useSoftwareUsage();

  const {
    data: aiInsight,
    isLoading: aiInsightLoading,
    isError: aiInsightError,
    refetch: refetchAiInsight,
  } = useAiInsight();

  const {
    data: activities,
    isLoading: activitiesLoading,
    isError: activitiesError,
    refetch: refetchActivities,
  } = useActivityFeed();

  const {
    data: notifications,
    isLoading: notificationsLoading,
    isError: notificationsError,
    refetch: refetchNotifications,
  } = useDashboardNotifications();

  const { data: quickActions, isLoading: quickActionsLoading } =
    useQuickActions();

  const handleRefresh = () => {
    refetchKpis();
    refetchAssetStatus();
    refetchSoftwareUsage();
    refetchAiInsight();
    refetchActivities();
    refetchNotifications();
  };

  const currentUserName = user?.full_name?.split(" ")[0];

  return (
    <div className="space-y-8">
      <DashboardHeader userName={currentUserName} onRefresh={handleRefresh} />

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {kpis?.map((kpi, i) => (
          <StatCard
            key={kpi.label}
            data={kpi}
            isLoading={kpisLoading}
            index={i}
          />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <AssetStatusChart
          data={assetStatus}
          isLoading={assetStatusLoading}
          isError={assetStatusError}
          onRetry={refetchAssetStatus}
        />
        <SoftwareUsageChart
          data={softwareUsage}
          isLoading={softwareUsageLoading}
          isError={softwareUsageError}
          onRetry={refetchSoftwareUsage}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <AiInsightCard
            data={aiInsight}
            isLoading={aiInsightLoading}
            isError={aiInsightError}
            onRetry={refetchAiInsight}
          />
        </div>
        <div className="lg:col-span-1">
          <ActivityTimeline
            data={activities}
            isLoading={activitiesLoading}
            isError={activitiesError}
            onRetry={refetchActivities}
          />
        </div>
        <div className="lg:col-span-1">
          <NotificationPanel
            data={notifications}
            isLoading={notificationsLoading}
            isError={notificationsError}
            onRetry={refetchNotifications}
          />
        </div>
      </div>

      <QuickActions data={quickActions} isLoading={quickActionsLoading} />
    </div>
  );
}
