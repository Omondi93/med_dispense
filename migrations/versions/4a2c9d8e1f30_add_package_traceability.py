"""add package traceability and repackaging audit tables

Revision ID: 4a2c9d8e1f30
Revises: c8fc5f759eb2
Create Date: 2026-10-06
"""
from alembic import op
import sqlalchemy as sa

revision = "4a2c9d8e1f30"
down_revision = "c8fc5f759eb2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "medicine_packages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("serial_number", sa.String(length=64), nullable=False),
        sa.Column("batch_id", sa.Integer(), sa.ForeignKey("batches.id"), nullable=False),
        sa.Column("parent_package_id", sa.Integer(), sa.ForeignKey("medicine_packages.id"), nullable=True),
        sa.Column("qr_code_id", sa.Integer(), sa.ForeignKey("qrcodes.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("manufacturers.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("serial_number", name="uq_medicine_packages_serial_number"),
        sa.UniqueConstraint("qr_code_id", name="uq_medicine_packages_qr_code_id"),
        sa.CheckConstraint("quantity > 0", name="ck_medicine_packages_quantity_positive"),
    )
    op.create_index("ix_medicine_packages_serial_number", "medicine_packages", ["serial_number"])
    op.create_index("ix_medicine_packages_batch_id", "medicine_packages", ["batch_id"])
    op.create_index("ix_medicine_packages_parent_package_id", "medicine_packages", ["parent_package_id"])
    op.create_index("ix_medicine_packages_status", "medicine_packages", ["status"])
    op.create_index("ix_medicine_packages_created_by", "medicine_packages", ["created_by"])

    op.create_table(
        "repackaging_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_package_id", sa.Integer(), sa.ForeignKey("medicine_packages.id"), nullable=False),
        sa.Column("manufacturer_id", sa.Integer(), sa.ForeignKey("manufacturers.id"), nullable=False),
        sa.Column("source_quantity", sa.Integer(), nullable=False),
        sa.Column("child_count", sa.Integer(), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("source_quantity > 0", name="ck_repackaging_events_source_quantity_positive"),
        sa.CheckConstraint("child_count >= 2", name="ck_repackaging_events_child_count_minimum"),
    )
    op.create_index("ix_repackaging_events_source_package_id", "repackaging_events", ["source_package_id"])
    op.create_index("ix_repackaging_events_manufacturer_id", "repackaging_events", ["manufacturer_id"])


def downgrade():
    op.drop_index("ix_repackaging_events_manufacturer_id", table_name="repackaging_events")
    op.drop_index("ix_repackaging_events_source_package_id", table_name="repackaging_events")
    op.drop_table("repackaging_events")
    op.drop_index("ix_medicine_packages_created_by", table_name="medicine_packages")
    op.drop_index("ix_medicine_packages_status", table_name="medicine_packages")
    op.drop_index("ix_medicine_packages_parent_package_id", table_name="medicine_packages")
    op.drop_index("ix_medicine_packages_batch_id", table_name="medicine_packages")
    op.drop_index("ix_medicine_packages_serial_number", table_name="medicine_packages")
    op.drop_table("medicine_packages")
