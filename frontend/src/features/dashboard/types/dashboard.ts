export interface DashboardKpi {
  label: string;
  value: string;
  trend?: {
    direction: "up" | "down" | "neutral";
    value: string;
  };
  icon: string;
}

export interface AssetStatusData {
  name: string;
  value: number;
  color: string;
}

export interface SoftwareUsageData {
  name: string;
  value: number;
  percentage: number;
}

export interface AiInsight {
  dormantLicenses: number;
  predictedLicenses: number;
  potentialSavings: number;
  topRecommendation: string;
  riskLevel: "low" | "medium" | "high";
}

export type ActivityType =
  | "asset_assigned"
  | "qr_scan"
  | "license_renewed"
  | "maintenance"
  | "employee_login";

export interface ActivityItem {
  id: string;
  type: ActivityType;
  title: string;
  description: string;
  timestamp: string;
  user?: string;
}

export interface DashboardNotification {
  id: string;
  title: string;
  message: string;
  priority: "low" | "medium" | "high" | "critical";
  category: string;
  timestamp: string;
  read: boolean;
}

export interface QuickAction {
  id: string;
  label: string;
  description: string;
  icon: string;
  href?: string;
}
