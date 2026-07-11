export type AssetStatus =
  "available" | "assigned" | "maintenance" | "lost" | "retired";

export type AssetCondition = "new" | "good" | "fair" | "poor" | "damaged";

export type AssetCategory =
  | "laptop"
  | "desktop"
  | "monitor"
  | "tablet"
  | "phone"
  | "printer"
  | "network"
  | "peripheral"
  | "other";

export type WarrantyStatus =
  "active" | "expiring_soon" | "expired" | "not_covered";

export type LifecycleEventType =
  | "registered"
  | "assigned"
  | "returned"
  | "transferred"
  | "maintenance"
  | "retired";

export interface EmployeeRef {
  id: string;
  name: string;
  email: string;
  department: string;
  avatar_url?: string;
}

export interface Asset {
  id: string;
  asset_code: string;
  name: string;
  category: AssetCategory;
  brand: string;
  model: string;
  serial_number: string;
  purchase_date: string;
  purchase_price: number;
  vendor: string;
  warranty_end: string;
  warranty_status: WarrantyStatus;
  department: string;
  location: string;
  assigned_to: EmployeeRef | null;
  condition: AssetCondition;
  status: AssetStatus;
  description: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface LifecycleEvent {
  id: string;
  asset_id: string;
  event_type: LifecycleEventType;
  title: string;
  description: string;
  user: string;
  timestamp: string;
}

export interface AssetMaintenance {
  id: string;
  asset_id: string;
  type: string;
  description: string;
  scheduled_date: string;
  completed_date?: string;
  cost?: number;
  vendor?: string;
  status: "scheduled" | "in_progress" | "completed" | "cancelled";
}

export interface AssetAssignment {
  id: string;
  asset_id: string;
  employee: EmployeeRef;
  assigned_date: string;
  expected_return?: string;
  returned_date?: string;
  notes?: string;
  status: "active" | "returned";
}

export interface AssetFilters {
  search: string;
  category: AssetCategory[];
  department: string[];
  status: AssetStatus[];
  location: string[];
  condition: AssetCondition[];
  purchaseYear: number[];
}

export type SortField =
  "asset_code" | "name" | "department" | "purchase_date" | "status";

export type SortDirection = "asc" | "desc";

export interface AssetSort {
  field: SortField;
  direction: SortDirection;
}

export interface AssetColumn {
  key: string;
  label: string;
  visible: boolean;
  sortable: boolean;
}

export interface CreateAssetPayload {
  asset_code: string;
  name: string;
  category: AssetCategory;
  brand: string;
  model: string;
  serial_number: string;
  purchase_date: string;
  purchase_price: number;
  vendor: string;
  warranty_end: string;
  department: string;
  location: string;
  description: string;
}

export interface UpdateAssetPayload extends Partial<CreateAssetPayload> {
  condition?: AssetCondition;
  status?: AssetStatus;
  notes?: string;
}

export interface AssignAssetPayload {
  employee_id: string;
  assigned_date: string;
  expected_return?: string;
  notes?: string;
}
