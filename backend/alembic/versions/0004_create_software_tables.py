"""Create software-management tables (software_categories, software, licenses, employee_software, software_usage_logs).

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- software_categories ---
    op.create_table(
        "software_categories",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(200), unique=True, nullable=False, index=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- software ---
    op.create_table(
        "software",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column(
            "vendor_id", UUID(as_uuid=False),
            sa.ForeignKey("vendors.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "category_id", UUID(as_uuid=False),
            sa.ForeignKey("software_categories.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("current_version", sa.String(50), nullable=True),
        sa.Column("license_type", sa.String(20), nullable=False, server_default=sa.text("'subscription'")),
        sa.Column("monthly_cost", sa.Float(), nullable=True),
        sa.Column("annual_cost", sa.Float(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'"), index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- licenses ---
    op.create_table(
        "licenses",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("license_key", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column(
            "software_id", UUID(as_uuid=False),
            sa.ForeignKey("software.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column("purchase_date", sa.DateTime(), nullable=True),
        sa.Column("renewal_date", sa.DateTime(), nullable=True),
        sa.Column("expiry_date", sa.DateTime(), nullable=True, index=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'"), index=True),
        sa.Column("max_seats", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("allocated_seats", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("monthly_cost", sa.Float(), nullable=True),
        sa.Column("annual_cost", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- employee_software ---
    op.create_table(
        "employee_software",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "employee_id", UUID(as_uuid=False),
            sa.ForeignKey("employees.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "software_id", UUID(as_uuid=False),
            sa.ForeignKey("software.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "license_id", UUID(as_uuid=False),
            sa.ForeignKey("licenses.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "assigned_by", UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("assigned_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'active'")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- software_usage_logs ---
    op.create_table(
        "software_usage_logs",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "employee_id", UUID(as_uuid=False),
            sa.ForeignKey("employees.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "software_id", UUID(as_uuid=False),
            sa.ForeignKey("software.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column("login_time", sa.DateTime(), nullable=False, index=True),
        sa.Column("logout_time", sa.DateTime(), nullable=True),
        sa.Column("session_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("os", sa.String(100), nullable=True),
        sa.Column("device_name", sa.String(255), nullable=True),
        sa.Column(
            "department_id", UUID(as_uuid=False),
            sa.ForeignKey("departments.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("software_usage_logs")
    op.drop_table("employee_software")
    op.drop_table("licenses")
    op.drop_table("software")
    op.drop_table("software_categories")
