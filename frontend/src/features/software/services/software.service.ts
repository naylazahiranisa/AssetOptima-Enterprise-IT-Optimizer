"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/services/api";
import type { ApiResponse } from "@/types/api";
import type {
  SoftwareLicense,
  LicenseAssignment,
  CreateSoftwarePayload,
  UpdateSoftwarePayload,
  AssignLicensePayload,
} from "@/features/software/types/software";

interface ApiSoftware {
  id: string;
  name: string;
  vendor_id: string | null;
  category_id: string | null;
  current_version: string | null;
  license_type: string;
  monthly_cost: number | null;
  annual_cost: number | null;
  status: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ApiLicense {
  id: string;
  software_id: string;
  license_key: string | null;
  max_seats: number;
  allocated_seats: number;
  monthly_cost: number | null;
  annual_cost: number | null;
  status: string;
  purchase_date: string | null;
  renewal_date: string | null;
  expiry_date: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ApiAssignment {
  id: string;
  software_id: string;
  employee_id: string;
  license_id: string | null;
  assigned_by: string | null;
  assigned_at: string;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

const categoryMap: Record<string, string> = {
  productivity: "productivity",
  design: "design",
  development: "development",
  security: "security",
  communication: "communication",
  analytics: "analytics",
  infrastructure: "infrastructure",
  finance: "finance",
  hr: "hr",
};

function mapSoftware(s: ApiSoftware, licenses?: ApiLicense[]): SoftwareLicense {
  const totalLicenses =
    licenses?.reduce((sum, l) => sum + (l.max_seats || 0), 0) ?? 0;
  const usedLicenses =
    licenses?.reduce((sum, l) => sum + (l.allocated_seats || 0), 0) ?? 0;
  const availableLicenses =
    licenses?.reduce((sum, l) => sum + (l.max_seats - l.allocated_seats || 0), 0) ?? 0;
  const monthlyCost = s.monthly_cost ?? 0;
  const annualCost = s.annual_cost ?? 0;

  const now = new Date();
  let expiryDate: string | null = null;
  if (licenses && licenses.length > 0) {
    const validExpiry = licenses
      .map((l) => l.expiry_date)
      .find((d) => d !== null);
    expiryDate = validExpiry ?? null;
  }

  let status: SoftwareLicense["status"] = "active";
  if (s.status === "inactive" || !s.is_active) status = "suspended";
  else if (expiryDate && new Date(expiryDate) < now) status = "expired";
  else if (expiryDate) {
    const daysUntilExpiry = Math.floor(
      (new Date(expiryDate).getTime() - now.getTime()) / (1000 * 60 * 60 * 24),
    );
    if (daysUntilExpiry <= 30) status = "expiring_soon";
  }

  return {
    id: s.id,
    software_name: s.name,
    vendor: s.vendor_id ?? "Unknown",
    category: (categoryMap[s.category_id ?? ""] ??
      "other") as SoftwareLicense["category"],
    license_type:
      (s.license_type as SoftwareLicense["license_type"]) ?? "subscription",
    total_licenses: totalLicenses,
    used_licenses: usedLicenses,
    available_licenses: availableLicenses,
    inactive_licenses: totalLicenses - usedLicenses - availableLicenses,
    monthly_cost: monthlyCost,
    annual_cost: annualCost,
    renewal_date: expiryDate ?? "",
    department: "",
    status,
    description: s.description ?? "",
    notes: "",
    created_at: s.created_at,
    updated_at: s.updated_at,
  };
}

export function useSoftware(page = 1, perPage = 20) {
  return useQuery<SoftwareLicense[]>({
    queryKey: ["software", { page, perPage }],
    queryFn: async () => {
      const res = await api.get<ApiResponse<ApiSoftware[]>>(
        "/api/v1/software",
        {
          params: {
            page,
            per_page: perPage,
            sort_by: "created_at",
            sort_order: "desc",
          },
        },
      );
      const items = (res.data as any).data ?? [];
      if (!Array.isArray(items)) return [];
      const softwareList = items as ApiSoftware[];
      return Promise.all(
        softwareList.map(async (s) => {
          try {
            const licRes = await api.get<ApiResponse<ApiLicense[]>>(
              `/api/v1/software/licenses`,
              {
                params: { software_id: s.id },
              },
            );
            const licItems = ((licRes.data as any).data ?? []) as ApiLicense[];
            return mapSoftware(s, licItems);
          } catch {
            return mapSoftware(s);
          }
        }),
      );
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useSoftwareById(id: string) {
  return useQuery<SoftwareLicense | undefined>({
    queryKey: ["software", id],
    queryFn: async () => {
      const res = await api.get<ApiResponse<ApiSoftware>>(
        `/api/v1/software/${id}`,
      );
      const item = (res.data as any).data ?? res.data;
      if (!item || !item.id) return undefined;
      let licenses: ApiLicense[] = [];
      try {
        const licRes = await api.get<ApiResponse<ApiLicense[]>>(
          `/api/v1/software/licenses`,
          {
            params: { software_id: id },
          },
        );
        licenses = ((licRes.data as any).data ?? []) as ApiLicense[];
      } catch {
        /* no licenses */
      }
      return mapSoftware(item as ApiSoftware, licenses);
    },
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
  });
}

export function useSoftwareAssignments(softwareId: string) {
  return useQuery<LicenseAssignment[]>({
    queryKey: ["software", softwareId, "assignments"],
    queryFn: async () => {
      const res = await api.get<ApiResponse<ApiAssignment[]>>(
        `/api/v1/software/assignments`,
        {
          params: { software_id: softwareId },
        },
      );
      const items = (res.data as any).data ?? [];
      return (Array.isArray(items) ? items : []).map((a: ApiAssignment) => ({
        id: a.id,
        software_id: a.software_id,
        employee_name: a.employee_id ?? "Unknown",
        employee_email: "",
        employee_department: "",
        assigned_date: a.assigned_at?.split("T")[0] ?? "",
        notes: a.notes ?? undefined,
        status:
          a.status === "active" ? ("active" as const) : ("revoked" as const),
      }));
    },
    staleTime: 5 * 60 * 1000,
    enabled: !!softwareId,
  });
}

export function useLicenses(page = 1, perPage = 20) {
  return useQuery<SoftwareLicense[]>({
    queryKey: ["licenses", { page, perPage }],
    queryFn: async () => {
      const res = await api.get<ApiResponse<ApiLicense[]>>(
        "/api/v1/software/licenses",
        {
          params: {
            page,
            per_page: perPage,
            sort_by: "created_at",
            sort_order: "desc",
          },
        },
      );
      const items = (res.data as any).data ?? [];
      if (!Array.isArray(items)) return [];
      return items.map((l: ApiLicense) => {
        const now = new Date();
        let status: SoftwareLicense["status"] = "active";
        if (l.status === "expired") status = "expired";
        else if (l.expiry_date && new Date(l.expiry_date) < now) status = "expired";
        else if (l.expiry_date) {
          const days = Math.floor((new Date(l.expiry_date).getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
          if (days <= 30) status = "expiring_soon";
        }
        if (l.allocated_seats === 0 && l.max_seats > 0) status = "unused";

        return {
          id: l.id,
          software_name: l.software_id ?? "Unknown",
          vendor: "",
          category: "other" as const,
          license_type: "subscription" as const,
          total_licenses: l.max_seats || 0,
          used_licenses: l.allocated_seats || 0,
          available_licenses: (l.max_seats - l.allocated_seats) || 0,
          inactive_licenses: 0,
          monthly_cost: l.monthly_cost ?? 0,
          annual_cost: l.annual_cost ?? 0,
          renewal_date: l.renewal_date ?? l.expiry_date ?? "",
          department: "",
          status,
          description: l.notes ?? "",
          notes: l.notes ?? "",
          created_at: l.created_at,
          updated_at: l.updated_at,
        };
      });
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useLicenseById(id: string) {
  return useQuery<SoftwareLicense | undefined>({
    queryKey: ["licenses", id],
    queryFn: async () => {
      const res = await api.get<ApiResponse<ApiLicense>>(
        `/api/v1/software/licenses/${id}`,
      );
      const item = (res.data as any).data ?? res.data;
      if (!item || !item.id) return undefined;
      const l = item as ApiLicense;
      const now = new Date();
      let status: SoftwareLicense["status"] = "active";
      if (l.status === "expired") status = "expired";
      else if (l.expiry_date && new Date(l.expiry_date) < now) status = "expired";
      else if (l.expiry_date) {
        const days = Math.floor((new Date(l.expiry_date).getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
        if (days <= 30) status = "expiring_soon";
      }
      if (l.allocated_seats === 0 && l.max_seats > 0) status = "unused";

      return {
        id: l.id,
        software_name: l.software_id ?? "Unknown",
        vendor: "",
        category: "other" as const,
        license_type: "subscription" as const,
        total_licenses: l.max_seats || 0,
        used_licenses: l.allocated_seats || 0,
        available_licenses: (l.max_seats - l.allocated_seats) || 0,
        inactive_licenses: 0,
        monthly_cost: l.monthly_cost ?? 0,
        annual_cost: l.annual_cost ?? 0,
        renewal_date: l.renewal_date ?? l.expiry_date ?? "",
        department: "",
        status,
        description: l.notes ?? "",
        notes: l.notes ?? "",
        created_at: l.created_at,
        updated_at: l.updated_at,
      };
    },
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
  });
}

export function useCreateSoftware() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateSoftwarePayload) => {
      const res = await api.post("/api/v1/software", {
        name: payload.software_name,
        license_type: payload.license_type,
        monthly_cost: payload.monthly_cost || null,
        annual_cost: payload.annual_cost || null,
        description: payload.description || null,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["software"] });
    },
  });
}

export function useUpdateSoftware() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string;
      payload: UpdateSoftwarePayload;
    }) => {
      const res = await api.put(`/api/v1/software/${id}`, {
        ...(payload.software_name && { name: payload.software_name }),
        ...(payload.license_type && { license_type: payload.license_type }),
        ...(payload.monthly_cost !== undefined && {
          monthly_cost: payload.monthly_cost,
        }),
        ...(payload.annual_cost !== undefined && {
          annual_cost: payload.annual_cost,
        }),
        ...(payload.description !== undefined && {
          description: payload.description,
        }),
        ...(payload.status && { status: payload.status }),
      });
      return res.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["software"] });
      queryClient.invalidateQueries({ queryKey: ["software", id] });
    },
  });
}

export function useDeleteSoftware() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/software/${id}`);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["software"] });
    },
  });
}

export function useAssignLicense() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      softwareId,
      payload,
    }: {
      softwareId: string;
      payload: AssignLicensePayload;
    }) => {
      const res = await api.post("/api/v1/software/assignments/assign", {
        software_id: softwareId,
        employee_id: "",
        notes: payload.notes || null,
      });
      return res.data;
    },
    onSuccess: (_, { softwareId }) => {
      queryClient.invalidateQueries({ queryKey: ["software"] });
      queryClient.invalidateQueries({ queryKey: ["software", softwareId] });
      queryClient.invalidateQueries({
        queryKey: ["software", softwareId, "assignments"],
      });
    },
  });
}
