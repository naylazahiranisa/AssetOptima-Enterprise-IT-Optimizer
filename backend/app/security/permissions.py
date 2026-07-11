"""Role definitions, permission matrix, and role-based utilities.

Every user is assigned exactly one role.  Each role maps to a
set of fine-grained permissions that future business modules
can check via the ``require_permissions`` dependency.
"""

from enum import Enum


class Role(str, Enum):
    """Authorised user roles within AssetOptima."""

    SUPER_ADMIN = "super_admin"
    IT_MANAGER = "it_manager"
    IT_SUPPORT = "it_support"


class Permission(str, Enum):
    """Fine-grained action permissions."""

    # Super Admin — absolute
    FULL_ACCESS = "full_access"

    # IT Manager
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_REPORTS = "view_reports"
    VIEW_ANALYTICS = "view_analytics"
    VIEW_AI_ASSISTANT = "view_ai_assistant"
    READ_ASSETS = "read_assets"
    READ_EMPLOYEES = "read_employees"
    READ_LICENSES = "read_licenses"

    # IT Support
    MANAGE_INVENTORY = "manage_inventory"
    USE_QR_SCANNER = "use_qr_scanner"
    ASSIGN_ASSET = "assign_asset"
    RETURN_ASSET = "return_asset"


ROLE_PERMISSIONS: dict[Role, list[Permission]] = {
    Role.SUPER_ADMIN: list(Permission),
    Role.IT_MANAGER: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_REPORTS,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_AI_ASSISTANT,
        Permission.READ_ASSETS,
        Permission.READ_EMPLOYEES,
        Permission.READ_LICENSES,
    ],
    Role.IT_SUPPORT: [
        Permission.MANAGE_INVENTORY,
        Permission.USE_QR_SCANNER,
        Permission.ASSIGN_ASSET,
        Permission.RETURN_ASSET,
    ],
}

ROLE_DISPLAY_NAMES: dict[Role, str] = {
    Role.SUPER_ADMIN: "Super Admin",
    Role.IT_MANAGER: "IT Manager",
    Role.IT_SUPPORT: "IT Support",
}


def role_has_permission(role: Role, permission: Permission) -> bool:
    """Check whether a given role is granted a specific permission."""
    return permission in ROLE_PERMISSIONS[role]
