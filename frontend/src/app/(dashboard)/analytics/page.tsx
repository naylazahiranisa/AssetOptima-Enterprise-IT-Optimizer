"use client";

import { useQuery } from "@tanstack/react-query";
import { PageHeader } from "@/components/ui/page-header";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { BarChart3, TrendingUp, Users, DollarSign, ShieldAlert } from "lucide-react";
import api from "@/services/api";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#64748b", "#8b5cf6"];

async function fetchAnalytics() {
  const res = await api.get("/api/v1/ai/analytics");
  return res.data?.data ?? {};
}

export default function AnalyticsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics"],
    queryFn: fetchAnalytics,
    staleTime: 5 * 60 * 1000,
  });

  const expensiveSw = data?.most_expensive_software ?? [];
  const util = data?.license_utilization ?? {};
  const unusedAssets = data?.unused_assets_count ?? 0;
  const totalSw = data?.total_software ?? 0;

  const insights = [
    {
      label: "Most Expensive SW",
      value: expensiveSw.length > 0 ? expensiveSw[0]?.name ?? "—" : "—",
      subtitle: expensiveSw.length > 0 ? `$${expensiveSw[0]?.monthly_cost?.toLocaleString() ?? 0}/mo` : "No data",
      icon: DollarSign,
    },
    {
      label: "License Utilization",
      value: `${util?.utilization_rate ?? 0}%`,
      subtitle: `${util?.used ?? 0}/${util?.total ?? 0} seats used`,
      icon: TrendingUp,
    },
    {
      label: "Unused Assets",
      value: unusedAssets.toString(),
      subtitle: "available for reassignment",
      icon: BarChart3,
    },
    {
      label: "Risk Level",
      value: (data?.risk_level ?? "low").toUpperCase(),
      subtitle: "overall risk assessment",
      icon: ShieldAlert,
    },
  ];

  return (
    <div className="space-y-8">
      <PageHeader
        title="Analytics"
        description="Data-driven insights and trends"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {insights.map((insight) => {
          const Icon = insight.icon;
          return (
            <Card key={insight.label}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-muted-foreground text-sm font-medium">
                  {insight.label}
                </CardTitle>
                <Icon size={16} className="text-muted-foreground/60" />
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <Skeleton className="h-7 w-20" />
                ) : (
                  <>
                    <div className="text-foreground text-2xl font-semibold">
                      {insight.value}
                    </div>
                    <p className="text-muted-foreground mt-0.5 text-xs">
                      {insight.subtitle}
                    </p>
                  </>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Most Expensive Software</CardTitle>
            <CardDescription>Monthly cost by software</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : expensiveSw.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={expensiveSw.slice(0, 8)}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="monthly_cost" fill="#2563eb" radius={[4, 4, 0, 0]} name="Monthly Cost" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center py-16">
                <p className="text-muted-foreground text-sm">No software cost data available</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>License Utilization</CardTitle>
            <CardDescription>Total vs used seats</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : (util?.total ?? 0) > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: "Used", value: util.used ?? 0 },
                      { name: "Available", value: (util.total ?? 0) - (util.used ?? 0) },
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    <Cell fill="#16a34a" />
                    <Cell fill="#f59e0b" />
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center py-16">
                <p className="text-muted-foreground text-sm">No license data available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
