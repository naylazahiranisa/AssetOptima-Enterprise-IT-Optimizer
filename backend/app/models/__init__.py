# Models module: SQLAlchemy ORM models
# Import all models here so Alembic can discover them

from app.models.user import User  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.company import Company  # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.employee import Employee  # noqa: F401
from app.models.role_model import RoleModel  # noqa: F401
from app.models.location import Location  # noqa: F401
from app.models.vendor import Vendor  # noqa: F401
from app.models.asset_category import AssetCategory  # noqa: F401
from app.models.asset import Asset  # noqa: F401
from app.models.asset_assignment import AssetAssignment  # noqa: F401
from app.models.asset_history import AssetHistory  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.software_category import SoftwareCategory  # noqa: F401
from app.models.software import Software  # noqa: F401
from app.models.license_model import License  # noqa: F401
from app.models.employee_software import EmployeeSoftware  # noqa: F401
from app.models.software_usage_log import SoftwareUsageLog  # noqa: F401
from app.models.notification import Notification, NotificationPreference  # noqa: F401
from app.models.system_activity import SystemActivity  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.document_chunk import DocumentChunk  # noqa: F401
