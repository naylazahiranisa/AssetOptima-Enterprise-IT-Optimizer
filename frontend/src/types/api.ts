/** API response contracts matching the backend envelope */

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
  error: string | null;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface ApiError {
  status: number;
  message: string;
  detail: string;
  timestamp: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  category: string;
  priority: "low" | "medium" | "high";
  status: "unread" | "read" | "archived";
  created_at: string;
}
