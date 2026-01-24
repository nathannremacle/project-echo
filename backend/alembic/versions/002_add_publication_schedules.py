"""Add publication_schedules table

Revision ID: 002_add_publication_schedules
Revises: 001_initial
Create Date: 2026-01-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_publication_schedules'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create publication_schedules table
    op.create_table(
        'publication_schedules',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('channel_id', sa.String(36), nullable=False),
        sa.Column('video_id', sa.String(36), nullable=True),
        sa.Column('schedule_type', sa.String(50), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('delay_seconds', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('coordination_group_id', sa.String(36), nullable=True),
        sa.Column('wave_id', sa.String(36), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('is_paused', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('execution_result', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='SET NULL'),
        sa.CheckConstraint(
            "schedule_type IN ('simultaneous', 'staggered', 'independent')",
            name='check_schedule_type'
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'scheduled', 'executing', 'completed', 'failed', 'cancelled')",
            name='check_schedule_status'
        ),
        sa.CheckConstraint('delay_seconds >= 0', name='check_delay_positive'),
    )
    
    # Create indexes for common queries
    op.create_index('ix_publication_schedules_channel_id', 'publication_schedules', ['channel_id'])
    op.create_index('ix_publication_schedules_video_id', 'publication_schedules', ['video_id'])
    op.create_index('ix_publication_schedules_scheduled_at', 'publication_schedules', ['scheduled_at'])
    op.create_index('ix_publication_schedules_status', 'publication_schedules', ['status'])
    op.create_index('ix_publication_schedules_coordination_group_id', 'publication_schedules', ['coordination_group_id'])
    op.create_index('ix_publication_schedules_wave_id', 'publication_schedules', ['wave_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_publication_schedules_wave_id', table_name='publication_schedules')
    op.drop_index('ix_publication_schedules_coordination_group_id', table_name='publication_schedules')
    op.drop_index('ix_publication_schedules_status', table_name='publication_schedules')
    op.drop_index('ix_publication_schedules_scheduled_at', table_name='publication_schedules')
    op.drop_index('ix_publication_schedules_video_id', table_name='publication_schedules')
    op.drop_index('ix_publication_schedules_channel_id', table_name='publication_schedules')
    
    # Drop table
    op.drop_table('publication_schedules')
