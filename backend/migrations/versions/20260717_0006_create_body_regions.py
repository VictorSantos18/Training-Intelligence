"""create body regions

Revision ID: 20260717_0006
Revises: 20260716_0005
Create Date: 2026-07-17 09:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260717_0006"
down_revision: str | None = "20260716_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

BODY_REGIONS = [
    ("neck", "Pescoço"),
    ("upper_back", "Costas superiores"),
    ("lower_back", "Lombar"),
    ("chest", "Peitoral"),
    ("abdomen", "Abdomen"),
    ("left_shoulder", "Ombro esquerdo"),
    ("right_shoulder", "Ombro direito"),
    ("left_elbow", "Cotovelo esquerdo"),
    ("right_elbow", "Cotovelo direito"),
    ("left_wrist", "Punho esquerdo"),
    ("right_wrist", "Punho direito"),
]


def upgrade() -> None:
    op.create_table(
        "body_regions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="body_regions_code_unique"),
    )

    body_regions_table = sa.table(
        "body_regions",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        body_regions_table,
        [{"code": code, "name": name, "is_active": True} for code, name in BODY_REGIONS],
    )

    op.add_column(
        "pain_records",
        sa.Column("body_region_id", postgresql.UUID(as_uuid=False), nullable=True),
    )

    op.execute(
        """
        INSERT INTO body_regions (id, code, name, is_active)
        SELECT gen_random_uuid(), body_region, initcap(replace(body_region, '_', ' ')), true
        FROM pain_records
        WHERE body_region IS NOT NULL
        ON CONFLICT (code) DO NOTHING
        """
    )
    op.execute(
        """
        UPDATE pain_records
        SET body_region_id = body_regions.id
        FROM body_regions
        WHERE pain_records.body_region = body_regions.code
        """
    )

    op.alter_column("pain_records", "body_region_id", nullable=False)
    op.create_foreign_key(
        "pain_records_body_region_id_fkey",
        "pain_records",
        "body_regions",
        ["body_region_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("idx_pain_records_body_region", "pain_records", ["body_region_id"])
    op.drop_column("pain_records", "body_region")


def downgrade() -> None:
    op.add_column(
        "pain_records",
        sa.Column("body_region", sa.String(length=80), nullable=True),
    )
    op.execute(
        """
        UPDATE pain_records
        SET body_region = body_regions.code
        FROM body_regions
        WHERE pain_records.body_region_id = body_regions.id
        """
    )
    op.alter_column("pain_records", "body_region", nullable=False)
    op.drop_index("idx_pain_records_body_region", table_name="pain_records")
    op.drop_constraint("pain_records_body_region_id_fkey", "pain_records", type_="foreignkey")
    op.drop_column("pain_records", "body_region_id")
    op.drop_table("body_regions")
