"""create initial schema

Revision ID: 7f377a76f1c6
Revises:
Create Date: 2026-07-05 00:22:18.910510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f377a76f1c6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    ]


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        *_timestamp_columns(),
    )

    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=True),
        *_timestamp_columns(),
    )

    op.create_table(
        "plannings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "employee_id",
            sa.Integer(),
            sa.ForeignKey("employees.id"),
            nullable=False,
        ),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=False),
        *_timestamp_columns(),
    )

    op.create_table(
        "devis",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False
        ),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        *_timestamp_columns(),
    )

    op.create_table(
        "factures",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("devis_id", sa.Integer(), sa.ForeignKey("devis.id"), nullable=True),
        sa.Column(
            "client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False
        ),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=True),
        *_timestamp_columns(),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("factures")
    op.drop_table("devis")
    op.drop_table("plannings")
    op.drop_table("employees")
    op.drop_table("clients")
