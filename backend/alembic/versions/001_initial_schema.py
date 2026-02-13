"""Initial schema with all tables

Revision ID: 001
Revises:
Create Date: 2026-02-12 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create student_profiles table
    op.create_table(
        'student_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('validation_result', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('topic', sa.String(length=500), nullable=False),
        sa.Column('experience_level', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    # Indexes for student_profiles
    op.create_index('ix_student_profiles_created_at', 'student_profiles', ['created_at'], unique=False)
    op.create_index('ix_student_profiles_data', 'student_profiles', ['data'], unique=False, postgresql_using='gin')

    # Create qa_reports table
    op.create_table(
        'qa_reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('report_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('batch_size', sa.Integer(), nullable=False),
        sa.Column('completed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mean_cdv', sa.Float(), nullable=True),
        sa.Column('cdv_std', sa.Float(), nullable=True),
        sa.Column('recommendation', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['profile_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    # Indexes for qa_reports
    op.create_index('ix_qa_reports_profile_id', 'qa_reports', ['profile_id'], unique=False)
    op.create_index('ix_qa_reports_status', 'qa_reports', ['status'], unique=False)

    # Create personalized_tracks table
    op.create_table(
        'personalized_tracks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('qa_report_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('track_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('generation_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('algorithm_version', sa.String(length=50), nullable=False),
        sa.Column('validation_b8', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('generation_duration_sec', sa.Float(), nullable=True),
        sa.Column('batch_index', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['profile_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['qa_report_id'], ['qa_reports.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    # Indexes for personalized_tracks
    op.create_index('ix_personalized_tracks_profile_id', 'personalized_tracks', ['profile_id'], unique=False)
    op.create_index('ix_personalized_tracks_qa_report_id', 'personalized_tracks', ['qa_report_id'], unique=False)
    op.create_index('ix_personalized_tracks_status', 'personalized_tracks', ['status'], unique=False)
    op.create_index('ix_personalized_tracks_created_at', 'personalized_tracks', ['created_at'], unique=False)

    # Create generation_logs table
    op.create_table(
        'generation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('track_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_name', sa.String(length=50), nullable=False),
        sa.Column('step_output', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('llm_calls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('step_duration_sec', sa.Float(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['track_id'], ['personalized_tracks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    # Indexes for generation_logs
    op.create_index('ix_generation_logs_track_step', 'generation_logs', ['track_id', 'step_name'], unique=False)
    op.create_index('ix_generation_logs_step_output', 'generation_logs', ['step_output'], unique=False, postgresql_using='gin')


def downgrade() -> None:
    op.drop_table('generation_logs')
    op.drop_table('personalized_tracks')
    op.drop_table('qa_reports')
    op.drop_table('student_profiles')
