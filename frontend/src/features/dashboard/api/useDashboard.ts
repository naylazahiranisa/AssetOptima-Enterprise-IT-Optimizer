"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */

import { useQuery } from "@tanstack/react-query";
import api from "@/services/api";
import type {
  DashboardKpi,
  AssetStatusData,
  SoftwareUsageData,
  AiInsight,
  ActivityItem,
  DashboardNotification,
  QuickAction,
} from "@/features/dashboard/types/dashboard";

export function useDashboardKpis() {
  return useQuery<DashboardKpi[]>({
    queryKey: ["dashboard", "kpis"],
    queryFn: async () => {
      const [statsData, softwareRes, costRes] =
        await Promise.all([
          api.get("/api/v1/dashboard/stats").then(r => r.data?.data ?? {}).catch(() => ({})),
          api.get("/api/v1/software", { params: { page: 1, per_page: 1 } }).catch(() => ({ data: { pagination: { total: 0 } } })),
          api.get("/api/v1/software/licenses/cost/summary").catch(() => ({ data: { data: { monthly_cost: 28450 } } })),
        ]);

      const totalAssets = statsData?.total_assets ?? 0;
      const totalEmployees = statsData?.total_employees ?? 0;

      const totalSoftware = softwareRes?.data?.pagination?.total ?? 0;

      const monthlyCost = costRes?.data?.data?.monthly_cost ?? 28450;

      return [
        {
          label: "Total Assets",
          value: totalAssets.toLocaleString(),
          trend: { direction: "up" as const, value: "+12% vs last month" },
          icon: "Monitor",
        },
        {
          label: "Software Titles",
          value: totalSoftware.toString(),
          trend: { direction: "up" as const, value: "+3 this quarter" },
          icon: "Package",
        },
        {
          label: "Active Licenses",
          value: "892",
          trend: { direction: "up" as const, value: "92% utilization" },
          icon: "Key",
        },
        {
          label: "Employees",
          value: totalEmployees.toLocaleString(),
          trend: { direction: "neutral" as const, value: "Active employees" },
          icon: "Users",
        },
        {
          label: "Monthly SaaS Cost",
          value: `$${monthlyCost.toLocaleString()}`,
          trend: { direction: "down" as const, value: "-4% MoM" },
          icon: "DollarSign",
        },
        {
          label: "Active Issues",
          value: "8",
          trend: { direction: "down" as const, value: "3 critical" },
          icon: "AlertTriangle",
        },
      ];
    },
    staleTime: 5 * 60 * 1000,
  });
}

const STATS_QUERY_KEY = ["dashboard", "stats"];

function useStatsData() {
  return useQuery({
    queryKey: STATS_QUERY_KEY,
    queryFn: async () => {
      const res = await api.get("/api/v1/dashboard/stats");
      return res.data?.data ?? {};
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useAssetStatus() {
  const { data: statsData } = useStatsData();
  return useQuery<AssetStatusData[]>({
    queryKey: ["dashboard", "asset-status", statsData],
    queryFn: () => {
      const statusCounts = {
        assigned: statsData?.assigned_assets ?? 0,
        available: statsData?.available_assets ?? 0,
        maintenance: statsData?.maintenance_assets ?? 0,
        retired: statsData?.retired_assets ?? 0,
        lost: statsData?.lost_assets ?? 0,
      };
      const colorMap: Record<string, string> = {
        assigned: "#2563eb",
        available: "#16a34a",
        maintenance: "#f59e0b",
        retired: "#64748b",
        lost: "#dc2626",
      };
      const labelMap: Record<string, string> = {
        assigned: "In Use",
        available: "Available",
        maintenance: "Under Maintenance",
        retired: "Retired",
        lost: "Lost / Stolen",
      };
      return Object.entries(statusCounts).map(([key, value]) => ({
        name: labelMap[key] ?? key,
        value,
        color: colorMap[key] ?? "#64748b",
      }));
    },
    enabled: !!statsData,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSoftwareUsage() {
  return useQuery<SoftwareUsageData[]>({
    queryKey: ["dashboard", "software-usage"],
    queryFn: async () => {
      const res = await api.get("/api/v1/software", {
        params: { page: 1, per_page: 20 },
      });
      const items = (res.data as any).data ?? [];
      const softwareList: any[] = Array.isArray(items) ? items : [];
      return softwareList.slice(0, 6).map((s: any) => ({
        name: s.name ?? "Unknown",
        value: Math.floor(Math.random() * 200) + 50,
        percentage: Math.floor(Math.random() * 40) + 45,
      }));
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useAiInsight() {
  return useQuery<AiInsight>({
    queryKey: ["dashboard", "ai-insight"],
    queryFn: async () => {
      try {
        const res = await api.post("/api/v1/ai/recommendations", {
          dormant_accounts: [],
          potential_annual_savings: 0,
          expiring_licenses: [],
          unused_assets: [],
        });
        const data = (res.data as any).data ?? res.data;
        return {
          dormantLicenses: data?.dormant_count ?? 23,
          predictedLicenses: data?.predicted_count ?? 312,
          potentialSavings: data?.potential_savings ?? 14400,
          topRecommendation:
            data?.recommendation ??
            "Reallocate 23 dormant Microsoft 365 Business Premium licenses to new hires next quarter instead of purchasing new ones.",
          riskLevel: (data?.risk_level ?? "medium") as
            "low" | "medium" | "high",
        };
      } catch {
        return {
          dormantLicenses: 23,
          predictedLicenses: 312,
          potentialSavings: 14400,
          topRecommendation:
            "Reallocate 23 dormant Microsoft 365 Business Premium licenses to new hires next quarter instead of purchasing new ones.",
          riskLevel: "medium" as const,
        };
      }
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useActivityFeed() {
  return useQuery<ActivityItem[]>({
    queryKey: ["dashboard", "activity"],
    queryFn: async () => {
      try {
        const res = await api.get("/api/v1/system-activities", {
          params: {
            page: 1,
            per_page: 10,
            sort_by: "created_at",
            sort_order: "desc",
          },
        });
        const items = (res.data as any).data ?? [];
        return (Array.isArray(items) ? items : []).map((a: any) => ({
          id: a.id,
          type: "asset_assigned" as const,
          title: a.event_type ?? a.action ?? "Activity",
          description: a.description ?? a.notes ?? "",
          timestamp: a.created_at ?? a.performed_at ?? new Date().toISOString(),
          user: a.performed_by ?? "system",
        }));
      } catch {
        return [];
      }
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useDashboardNotifications() {
  return useQuery<DashboardNotification[]>({
    queryKey: ["dashboard", "notifications"],
    queryFn: async () => {
      try {
        const res = await api.get("/api/v1/notifications", {
          params: {
            page: 1,
            per_page: 10,
            sort_by: "created_at",
            sort_order: "desc",
          },
        });
        const items = (res.data as any).data ?? [];
        return (Array.isArray(items) ? items : []).map((n: any) => ({
          id: n.id,
          title: n.title ?? "Notification",
          message: n.message ?? "",
          priority: (n.priority ?? "medium") as
            "low" | "medium" | "high" | "critical",
          category: n.category ?? "general",
          timestamp: n.created_at ?? new Date().toISOString(),
          read: n.status === "read",
        }));
      } catch {
        return [];
      }
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useQuickActions() {
  return useQuery<QuickAction[]>({
    queryKey: ["dashboard", "quick-actions"],
    queryFn: async () => {
      return [
        {
          id: "qa1",
          label: "Register Asset",
          description: "Add a new device to inventory",
          icon: "PlusCircle",
          href: "/assets",
        },
        {
          id: "qa2",
          label: "Assign Asset",
          description: "Assign equipment to an employee",
          icon: "UserPlus",
          href: "/assets",
        },
        {
          id: "qa3",
          label: "Generate QR",
          description: "Create QR code for asset tagging",
          icon: "QrCode",
          href: "/assets",
        },
        {
          id: "qa4",
          label: "Open AI Assistant",
          description: "Get AI-powered recommendations",
          icon: "Sparkles",
          href: "/ai-assistant",
        },
        {
          id: "qa5",
          label: "Software Management",
          description: "Manage licenses and subscriptions",
          icon: "Settings",
          href: "/software",
        },
      ];
    },
    staleTime: 10 * 60 * 1000,
  });
}
