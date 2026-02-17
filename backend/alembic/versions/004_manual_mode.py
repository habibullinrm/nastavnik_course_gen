"""Ручной режим отладки: manual_sessions, prompt_versions, manual_step_runs, processor_configs

Revision ID: 004
Revises: 003
Create Date: 2026-02-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # prompt_versions — версии промптов для каждого шага
    op.create_table(
        'prompt_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('step_name', sa.String(length=50), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('prompt_text', sa.Text(), nullable=False),
        sa.Column('change_description', sa.Text(), nullable=True),
        sa.Column('is_baseline', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('step_name', 'version', name='uq_prompt_versions_step_version'),
    )
    op.create_index('ix_prompt_versions_step_name', 'prompt_versions', ['step_name'])

    # manual_sessions — сессии отладки
    op.create_table(
        'manual_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['profile_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_manual_sessions_profile_id', 'manual_sessions', ['profile_id'])
    op.create_index('ix_manual_sessions_status', 'manual_sessions', ['status'])

    # manual_step_runs — запуски шагов (полные снимки)
    op.create_table(
        'manual_step_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_name', sa.String(length=50), nullable=False),
        sa.Column('run_number', sa.Integer(), nullable=False),
        sa.Column('prompt_version_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rendered_prompt', sa.Text(), nullable=True),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('profile_variables', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('llm_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('raw_response', sa.Text(), nullable=True),
        sa.Column('parsed_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('parse_error', sa.Text(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('duration_ms', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
        sa.Column('preprocessor_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('postprocessor_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('auto_evaluation', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('llm_judge_evaluation', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['manual_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prompt_version_id'], ['prompt_versions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_manual_step_runs_session_id', 'manual_step_runs', ['session_id'])
    op.create_index('ix_manual_step_runs_session_step', 'manual_step_runs', ['session_id', 'step_name'])

    # processor_configs — привязка процессоров к шагам
    op.create_table(
        'processor_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('step_name', sa.String(length=50), nullable=False),
        sa.Column('processor_type', sa.String(length=20), nullable=False),
        sa.Column('processor_name', sa.String(length=255), nullable=False),
        sa.Column('execution_order', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('config_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['manual_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_processor_configs_session_step', 'processor_configs', ['session_id', 'step_name'])


def downgrade() -> None:
    op.drop_table('processor_configs')
    op.drop_table('manual_step_runs')
    op.drop_table('manual_sessions')
    op.drop_table('prompt_versions')
