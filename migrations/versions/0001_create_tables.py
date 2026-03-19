"""Создание всех таблиц.

Revision ID: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activities",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "parent_id",
            sa.BigInteger(),
            sa.ForeignKey("activities.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.CheckConstraint("level >= 1 AND level <= 3", name="ck_activity_level"),
    )
    op.create_index("ix_activities_parent_id", "activities", ["parent_id"])

    op.create_table(
        "buildings",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
    )
    op.create_index("ix_buildings_latitude", "buildings", ["latitude"])
    op.create_index("ix_buildings_longitude", "buildings", ["longitude"])

    op.create_table(
        "organizations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "building_id",
            sa.BigInteger(),
            sa.ForeignKey("buildings.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    op.create_index("ix_organizations_name", "organizations", ["name"])
    op.create_index("ix_organizations_building_id", "organizations", ["building_id"])

    op.create_table(
        "organization_phones",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "organization_id",
            sa.BigInteger(),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("phone", sa.String(50), nullable=False),
    )
    op.create_index(
        "ix_organization_phones_organization_id",
        "organization_phones",
        ["organization_id"],
    )

    op.create_table(
        "organization_activities",
        sa.Column(
            "organization_id",
            sa.BigInteger(),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "activity_id",
            sa.BigInteger(),
            sa.ForeignKey("activities.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("organization_activities")
    op.drop_table("organization_phones")
    op.drop_table("organizations")
    op.drop_table("buildings")
    op.drop_table("activities")
