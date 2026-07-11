"""Create notification, notification_preferences, system_activities tables and enhance audit_logs.

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- notifications ---
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("employee_id", UUID(as_uuid=False), sa.ForeignKey("employees.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("category", sa.String(30), nullable=False, server_default=sa.text("'system'"), index=True),
        sa.Column("priority", sa.String(10), nullable=False, server_default=sa.text("'medium'"), index=True),
        sa.Column("status", sa.String(10), nullable=False, server_default=sa.text("'unread'"), index=True),
        sa.Column("recipient_role", sa.String(30), nullable=True, index=True),
        sa.Column("reference_id", sa.String(100), nullable=True),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("tenant_id", UUID(as_uuid=False), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("is_broadcast", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
    )

    # --- notification_preferences ---
    op.create_table(
        "notification_preferences",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("category", sa.String(30), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("push_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("slack_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("teams_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("min_priority", sa.String(10), nullable=False, server_default=sa.text("'medium'")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "category", name="uq_user_notification_category"),
    )

    # --- system_activities ---
    op.create_table(
        "system_activities",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("event_type", sa.String(50), nullable=False, index=True),
        sa.Column("severity", sa.String(10), nullable=False, server_default=sa.text("'info'"), index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("service_name", sa.String(100), nullable=True, index=True),
        sa.Column("component", sa.String(100), nullable=True),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("hostname", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
    )

    # --- enhance audit_logs ---
    op.add_column("audit_logs", sa.Column("user_role", sa.String(30), nullable=True, index=True))
    op.add_column("audit_logs", sa.Column("ip_address", sa.String(45), nullable=True))
    op.add_column("audit_logs", sa.Column("user_agent", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("audit_logs", "user_agent")
    op.drop_column("audit_logs", "ip_address")
    op.drop_column("audit_logs", "user_role")
    op.drop_table("system_activities")
    op.drop_table("notification_preferences")
    op.drop_table("notifications")
