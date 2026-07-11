"use client";

/* eslint-disable @typescript-eslint/no-explicit-any */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/services/api";
import type { ApiResponse } from "@/types/api";
import type {
  Asset,
  AssetAssignment,
  AssetMaintenance,
  LifecycleEvent,
  CreateAssetPayload,
  UpdateAssetPayload,
  AssignAssetPayload,
} from "@/features/assets/types/assets";

interface ApiAsset {
  id: string;
  asset_code: string;
  serial_number: string | null;
  name: string;
  description: string | null;
  category_id: string;
  vendor_id: string | null;
  location_id: string | null;
  current_employee_id: string | null;
  status: string;
  condition: string;
  purchase_date: string | null;
  purchase_price: number | null;
  warranty_expiry: string | null;
  qr_value: string;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ApiAssignment {
  id: string;
  asset_id: string;
  employee_id: string;
  assigned_by: string | null;
  assigned_at: string;
  returned_at: string | null;
  expected_return_date: string | null;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

interface ApiHistory {
  id: string;
  asset_id: string;
  action: string;
  performed_by: string | null;
  performed_at: string;
  old_values: string | null;
  new_values: string | null;
  notes: string | null;
}

function mapAsset(a: ApiAsset): Asset {
  const now = new Date();
  const warrantyEnd = a.warranty_expiry ? new Date(a.warranty_expiry) : null;
  let warrantyStatus: Asset["warranty_status"] = "not_covered";
  if (warrantyEnd) {
    const daysUntilExpiry = Math.floor(
      (warrantyEnd.getTime() - now.getTime()) / (1000 * 60 * 60 * 24),
    );
    if (daysUntilExpiry < 0) warrantyStatus = "expired";
    else if (daysUntilExpiry <= 30) warrantyStatus = "expiring_soon";
    else warrantyStatus = "active";
  }
  return {
    id: a.id,
    asset_code: a.asset_code,
    name: a.name,
    category: a.category_id as Asset["category"],
    brand: "",
    model: a.name,
    serial_number: a.serial_number ?? "",
    purchase_date: a.purchase_date ?? "",
    purchase_price: a.purchase_price ?? 0,
    vendor: a.vendor_id ?? "Unknown",
    warranty_end: a.warranty_expiry ?? "",
    warranty_status: warrantyStatus,
    department: "",
    location: a.location_id ?? "",
    assigned_to: null,
    condition: a.condition as Asset["condition"],
    status: a.status as Asset["status"],
    description: a.description ?? "",
    notes: a.notes ?? "",
    created_at: a.created_at,
    updated_at: a.updated_at,
  };
}

function mapHistory(h: ApiHistory): LifecycleEvent {
  const eventTypeMap: Record<string, LifecycleEvent["event_type"]> = {
    created: "registered",
    assigned: "assigned",
    returned: "returned",
    transferred: "transferred",
    maintenance: "maintenance",
    retired: "retired",
    status_changed: "maintenance",
    condition_changed: "maintenance",
  };
  return {
    id: h.id,
    asset_id: h.asset_id,
    event_type: eventTypeMap[h.action] ?? "maintenance",
    title: h.action.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
    description: h.notes ?? "",
    user: h.performed_by ?? "system",
    timestamp: h.performed_at,
  };
}

export function useAssets(page = 1, perPage = 20) {
  return useQuery<Asset[]>({
    queryKey: ["assets", { page, perPage }],
    queryFn: async () => {
      const res = await api.get<ApiResponse<ApiAsset[]>>("/api/v1/assets", {
        params: {
          page,
          per_page: perPage,
          sort_by: "created_at",
          sort_order: "desc",
        },
      });
      const items = (res.data as any).data ?? res.data ?? [];
      return (Array.isArray(items) ? items : []).map(mapAsset);
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useAsset(id: string) {
  return useQuery<Asset | undefined>({
    queryKey: ["assets", id],
    queryFn: async () => {
      const res = await api.get<ApiResponse<ApiAsset>>(`/api/v1/assets/${id}`);
      const data = (res.data as any).data ?? res.data;
      if (!data || !data.id) return undefined;
      return mapAsset(data as ApiAsset);
    },
    staleTime: 5 * 60 * 1000,
    enabled: !!id,
  });
}

export function useAssetLifecycle(assetId: string) {
  return useQuery<LifecycleEvent[]>({
    queryKey: ["assets", assetId, "lifecycle"],
    queryFn: async () => {
      const res = await api.get<ApiResponse<ApiHistory[]>>(
        `/api/v1/assets/${assetId}/history`,
      );
      const items = (res.data as any).data ?? [];
      return (Array.isArray(items) ? items : []).map(mapHistory);
    },
    staleTime: 5 * 60 * 1000,
    enabled: !!assetId,
  });
}

export function useAssetMaintenance(assetId: string) {
  return useQuery<AssetMaintenance[]>({
    queryKey: ["assets", assetId, "maintenance"],
    queryFn: async () => {
      const res = await api.get(`/api/v1/assets/${assetId}/history`);
      const items = (res.data as any).data ?? [];
      return (Array.isArray(items) ? items : [])
        .filter((h: any) => h.action === "maintenance")
        .map((h: any) => ({
          id: h.id,
          asset_id: h.asset_id,
          type: h.notes ?? "Maintenance",
          description: h.notes ?? "",
          scheduled_date: h.performed_at?.split("T")[0] ?? "",
          completed_date: h.performed_at?.split("T")[0] ?? "",
          status: "completed" as const,
        }));
    },
    staleTime: 5 * 60 * 1000,
    enabled: !!assetId,
  });
}

export function useAssetAssignment(assetId: string) {
  return useQuery<AssetAssignment | null>({
    queryKey: ["assets", assetId, "assignment"],
    queryFn: async () => {
      const res = await api.get<ApiResponse<ApiAssignment[]>>(
        `/api/v1/assets/${assetId}/history`,
      );
      const items = (res.data as any).data ?? [];
      const assignments = (Array.isArray(items) ? items : []).filter(
        (h: any) => h.action === "assigned" || h.action === "transferred",
      );
      if (assignments.length === 0) return null;
      const latest = assignments[assignments.length - 1];
      return {
        id: latest.id,
        asset_id: latest.asset_id,
        employee: { id: "", name: "Unknown", email: "", department: "" },
        assigned_date: latest.performed_at?.split("T")[0] ?? "",
        notes: latest.notes ?? undefined,
        status: "active" as const,
      };
    },
    staleTime: 5 * 60 * 1000,
    enabled: !!assetId,
  });
}

export function useCreateAsset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CreateAssetPayload) => {
      const res = await api.post("/api/v1/assets", {
        asset_code: payload.asset_code,
        name: payload.name,
        serial_number: payload.serial_number,
        category_id: payload.category,
        description: payload.description,
        purchase_date: payload.purchase_date || null,
        purchase_price: payload.purchase_price || null,
        warranty_expiry: payload.warranty_end || null,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
    },
  });
}

export function useUpdateAsset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string;
      payload: UpdateAssetPayload;
    }) => {
      const res = await api.put(`/api/v1/assets/${id}`, {
        ...(payload.name && { name: payload.name }),
        ...(payload.serial_number && { serial_number: payload.serial_number }),
        ...(payload.category && { category_id: payload.category }),
        ...(payload.condition && { condition: payload.condition }),
        ...(payload.status && { status: payload.status }),
        ...(payload.description !== undefined && {
          description: payload.description,
        }),
        ...(payload.notes !== undefined && { notes: payload.notes }),
        ...(payload.purchase_date && { purchase_date: payload.purchase_date }),
        ...(payload.purchase_price !== undefined && {
          purchase_price: payload.purchase_price,
        }),
      });
      return res.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      queryClient.invalidateQueries({ queryKey: ["assets", id] });
    },
  });
}

export function useDeleteAsset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/v1/assets/${id}`);
      return { success: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
    },
  });
}

export function useAssignAsset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      assetId,
      payload,
    }: {
      assetId: string;
      payload: AssignAssetPayload;
    }) => {
      const res = await api.post(`/api/v1/assets/${assetId}/assign`, {
        employee_id: payload.employee_id,
        notes: payload.notes || null,
        expected_return_date: payload.expected_return || null,
      });
      return res.data;
    },
    onSuccess: (_, { assetId }) => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      queryClient.invalidateQueries({ queryKey: ["assets", assetId] });
      queryClient.invalidateQueries({
        queryKey: ["assets", assetId, "assignment"],
      });
      queryClient.invalidateQueries({
        queryKey: ["assets", assetId, "lifecycle"],
      });
    },
  });
}

export function useReturnAsset() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      assetId,
      notes,
    }: {
      assetId: string;
      notes?: string;
    }) => {
      const res = await api.post(`/api/v1/assets/${assetId}/return`, {
        notes: notes || null,
      });
      return res.data;
    },
    onSuccess: (_, { assetId }) => {
      queryClient.invalidateQueries({ queryKey: ["assets"] });
      queryClient.invalidateQueries({ queryKey: ["assets", assetId] });
      queryClient.invalidateQueries({
        queryKey: ["assets", assetId, "assignment"],
      });
      queryClient.invalidateQueries({
        queryKey: ["assets", assetId, "lifecycle"],
      });
    },
  });
}

export function useEmployees() {
  return useQuery({
    queryKey: ["employees"],
    queryFn: async () => {
      const res = await api.get<ApiResponse<any[]>>("/api/v1/employees");
      const items = (res.data as any).data ?? [];
      return (Array.isArray(items) ? items : []).map((e: any) => ({
        id: e.id,
        name: e.full_name ?? e.name ?? "Unknown",
        email: e.email ?? "",
        department: e.department_name ?? e.department ?? "",
        avatar_url: "",
      }));
    },
    staleTime: 10 * 60 * 1000,
  });
}
