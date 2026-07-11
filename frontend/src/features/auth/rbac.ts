/** Role-based access control configuration.
 *
 * Maps routes and actions to permitted roles.
 * Centralise every permission check here so the UI reflects the backend RBAC.
 */

import type { UserRole } from "@/types/auth";

export type Permission =
  | "page:dashboard"
  | "page:assets"
  | "page:employees"
  | "page:software"
  | "page:licenses"
  | "page:notifications"
  | "page:audit"
  | "page:ai-assistant"
  | "page:analytics"
  | "page:settings"
  | "action:create:asset"
  | "action:edit:asset"
  | "action:delete:asset"
  | "action:assign:asset"
  | "action:create:employee"
  | "action:edit:employee"
  | "action:delete:employee"
  | "action:create:software"
  | "action:edit:software"
  | "action:delete:software"
  | "action:manage:licenses"
  | "action:view:audit"
  | "action:view:analytics"
  | "action:manage:users"
  | "action:manage:roles"
  | "action:ai:chat"
  | "action:ai:admin";

/** Map every role to the set of permissions it grants. */
const rolePermissions: Record<UserRole, Set<Permission>> = {
  super_admin: new Set([
    "page:dashboard",
    "page:assets",
    "page:employees",
    "page:software",
    "page:licenses",
    "page:notifications",
    "page:audit",
    "page:ai-assistant",
    "page:analytics",
    "page:settings",
    "action:create:asset",
    "action:edit:asset",
    "action:delete:asset",
    "action:assign:asset",
    "action:create:employee",
    "action:edit:employee",
    "action:delete:employee",
    "action:create:software",
    "action:edit:software",
    "action:delete:software",
    "action:manage:licenses",
    "action:view:audit",
    "action:view:analytics",
    "action:manage:users",
    "action:manage:roles",
    "action:ai:chat",
    "action:ai:admin",
  ]),

  it_manager: new Set([
    "page:dashboard",
    "page:assets",
    "page:employees",
    "page:software",
    "page:licenses",
    "page:notifications",
    "page:audit",
    "page:ai-assistant",
    "page:analytics",
    "page:settings",
    "action:view:audit",
    "action:view:analytics",
    "action:ai:chat",
  ]),

  it_support: new Set([
    "page:dashboard",
    "page:assets",
    "page:employees",
    "page:software",
    "page:licenses",
    "page:notifications",
    "page:ai-assistant",
    "page:settings",
    "action:ai:chat",
  ]),
};

/** Route-to-permission mapping used by the route guard. */
export const routePermissions: Record<string, Permission> = {
  "/dashboard": "page:dashboard",
  "/assets": "page:assets",
  "/employees": "page:employees",
  "/software": "page:software",
  "/licenses": "page:licenses",
  "/notifications": "page:notifications",
  "/audit": "page:audit",
  "/ai-assistant": "page:ai-assistant",
  "/analytics": "page:analytics",
  "/settings": "page:settings",
};

/** Check whether a role holds a given permission. */
export function hasPermission(
  role: UserRole | null,
  permission: Permission,
): boolean {
  if (!role) return false;
  return rolePermissions[role]?.has(permission) ?? false;
}

/** Check whether a role can access a given route. */
export function canAccessRoute(
  role: UserRole | null,
  pathname: string,
): boolean {
  if (!role) return false;

  const exactMatch = routePermissions[pathname];
  if (exactMatch) {
    return hasPermission(role, exactMatch);
  }

  const prefix = Object.keys(routePermissions).find((route) =>
    pathname.startsWith(route + "/"),
  );
  if (prefix) {
    return hasPermission(role, routePermissions[prefix]);
  }

  return false;
}

/** Return the appropriate redirect path when access is denied. */
export function getFallbackRoute(role: UserRole | null): string {
  if (!role) return "/login";
  return "/dashboard";
}
