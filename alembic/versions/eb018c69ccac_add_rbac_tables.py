"""add rbac tables

Revision ID: eb018c69ccac
Revises: f9ce68098a37
Create Date: 2026-08-03 10:42:50.176736

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "eb018c69ccac"
down_revision: Union[str, Sequence[str], None] = "f9ce68098a37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create permissions table

    op.create_table(
        "permissions",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    )

    op.create_index(
        op.f("ix_permissions_id"),
        "permissions",
        ["id"],
        unique=False
    )

    # Create roles table

    op.create_table(
        "roles",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String(length=50),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name")
    )

    op.create_index(
        op.f("ix_roles_id"),
        "roles",
        ["id"],
        unique=False
    )

    # Create role_permissions table

    op.create_table(
        "role_permissions",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            "role_id",
            sa.BigInteger(),
            nullable=False
        ),
        sa.Column(
            "permission_id",
            sa.BigInteger(),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        op.f("ix_role_permissions_id"),
        "role_permissions",
        ["id"],
        unique=False
    )

    # Add role_id column to users

    op.add_column(
        "users",
        sa.Column(
            "role_id",
            sa.BigInteger(),
            nullable=False
        )
    )

    # Create foreign key

    op.create_foreign_key(
        "fk_users_role_id",
        "users",
        "roles",
        ["role_id"],
        ["id"]
    )

    # Remove old role column

    op.drop_column(
        "users",
        "role"
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False
        )
    )

    op.drop_constraint(
        "fk_users_role_id",
        "users",
        type_="foreignkey"
    )

    op.drop_column(
        "users",
        "role_id"
    )

    op.drop_index(
        op.f("ix_role_permissions_id"),
        table_name="role_permissions"
    )

    op.drop_table("role_permissions")

    op.drop_index(
        op.f("ix_roles_id"),
        table_name="roles"
    )

    op.drop_table("roles")

    op.drop_index(
        op.f("ix_permissions_id"),
        table_name="permissions"
    )

    op.drop_table("permissions")