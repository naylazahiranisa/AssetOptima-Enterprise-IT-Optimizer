"""Create asset-management tables (asset_categories, assets, asset_assignments, asset_histories, notifications).

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- asset_categories ---
    op.create_table(
        "asset_categories",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- assets ---
    op.create_table(
        "assets",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("asset_code", sa.String(100), unique=True, nullable=False, index=True),
        sa.Column("serial_number", sa.String(200), unique=True, nullable=True, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "category_id", UUID(as_uuid=False),
            sa.ForeignKey("asset_categories.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "vendor_id", UUID(as_uuid=False),
            sa.ForeignKey("vendors.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "location_id", UUID(as_uuid=False),
            sa.ForeignKey("locations.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "current_employee_id", UUID(as_uuid=False),
            sa.ForeignKey("employees.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'available'"), index=True),
        sa.Column("condition", sa.String(20), nullable=False, server_default=sa.text("'good'")),
        sa.Column("purchase_date", sa.DateTime(), nullable=True),
        sa.Column("purchase_price", sa.Float(), nullable=True),
        sa.Column("warranty_expiry", sa.DateTime(), nullable=True),
        sa.Column("qr_value", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- asset_assignments ---
    op.create_table(
        "asset_assignments",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "asset_id", UUID(as_uuid=False),
            sa.ForeignKey("assets.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "employee_id", UUID(as_uuid=False),
            sa.ForeignKey("employees.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "assigned_by", UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("assigned_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("returned_at", sa.DateTime(), nullable=True),
        sa.Column("expected_return_date", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'assigned'")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- asset_histories ---
    op.create_table(
        "asset_histories",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "asset_id", UUID(as_uuid=False),
            sa.ForeignKey("assets.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column("action", sa.String(30), nullable=False, index=True),
        sa.Column(
            "performed_by", UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("performed_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
        sa.Column("old_values", sa.Text(), nullable=True),
        sa.Column("new_values", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # --- notifications ---
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column(
            "user_id", UUID(as_uuid=False),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "employee_id", UUID(as_uuid=False),
            sa.ForeignKey("employees.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("type", sa.String(30), nullable=False, index=True),
        sa.Column("reference_id", sa.String(100), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("asset_histories")
    op.drop_table("asset_assignments")
    op.drop_table("assets")
    op.drop_table("asset_categories")
