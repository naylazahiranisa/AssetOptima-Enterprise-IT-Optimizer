export type LicenseStatus =
  "active" | "expired" | "expiring_soon" | "unused" | "suspended";

export type SoftwareCategory =
  | "productivity"
  | "design"
  | "development"
  | "security"
  | "communication"
  | "analytics"
  | "infrastructure"
  | "finance"
  | "hr"
  | "other";

export type LicenseType =
  "perpetual" | "subscription" | "concurrent" | "floating" | "volume";

export interface SoftwareLicense {
  id: string;
  software_name: string;
  vendor: string;
  category: SoftwareCategory;
  license_type: LicenseType;
  total_licenses: number;
  used_licenses: number;
  available_licenses: number;
  inactive_licenses: number;
  monthly_cost: number;
  annual_cost: number;
  renewal_date: string;
  department: string;
  status: LicenseStatus;
  description: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface LicenseAssignment {
  id: string;
  software_id: string;
  employee_name: string;
  employee_email: string;
  employee_department: string;
  assigned_date: string;
  license_key?: string;
  notes?: string;
  status: "active" | "revoked";
}

export interface SoftwareFilters {
  search: string;
  vendor: string[];
  category: SoftwareCategory[];
  department: string[];
  status: LicenseStatus[];
  renewalMonth: string[];
}

export type SortField =
  | "software_name"
  | "vendor"
  | "category"
  | "license_type"
  | "total_licenses"
  | "used_licenses"
  | "available_licenses"
  | "monthly_cost"
  | "annual_cost"
  | "renewal_date"
  | "department"
  | "status";

export type SortDirection = "asc" | "desc";

export interface SoftwareSort {
  field: SortField;
  direction: SortDirection;
}

export interface SoftwareColumn {
  key: string;
  label: string;
  visible: boolean;
  sortable: boolean;
}

export interface CreateSoftwarePayload {
  software_name: string;
  vendor: string;
  category: SoftwareCategory;
  license_type: LicenseType;
  total_licenses: number;
  monthly_cost: number;
  annual_cost: number;
  renewal_date: string;
  department: string;
  description?: string;
}

export interface UpdateSoftwarePayload extends Partial<CreateSoftwarePayload> {
  used_licenses?: number;
  available_licenses?: number;
  inactive_licenses?: number;
  status?: LicenseStatus;
  notes?: string;
}

export interface AssignLicensePayload {
  employee_name: string;
  employee_email: string;
  employee_department: string;
  assigned_date: string;
  license_key?: string;
  notes?: string;
}
