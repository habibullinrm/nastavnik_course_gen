"""Widen step_name column from String(10) to String(50)

Revision ID: 002
Revises: 001
Create Date: 2026-02-16 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'generation_logs',
        'step_name',
        existing_type=sa.String(10),
        type_=sa.String(50),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'generation_logs',
        'step_name',
        existing_type=sa.String(50),
        type_=sa.String(10),
        existing_nullable=False,
    )
