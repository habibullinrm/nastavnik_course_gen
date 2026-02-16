"""Add batch_id column to personalized_tracks

Revision ID: 003
Revises: 002
Create Date: 2026-02-16 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'personalized_tracks',
        sa.Column('batch_id', UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        'ix_personalized_tracks_batch_id',
        'personalized_tracks',
        ['batch_id'],
    )


def downgrade() -> None:
    op.drop_index('ix_personalized_tracks_batch_id', table_name='personalized_tracks')
    op.drop_column('personalized_tracks', 'batch_id')
