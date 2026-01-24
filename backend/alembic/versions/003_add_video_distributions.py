"""Add video_distributions table

Revision ID: 003_add_video_distributions
Revises: 002_add_publication_schedules
Create Date: 2026-01-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_video_distributions'
down_revision = '002_add_publication_schedules'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create video_distributions table
    op.create_table(
        'video_distributions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('video_id', sa.String(36), nullable=False),
        sa.Column('channel_id', sa.String(36), nullable=False),
        sa.Column('distribution_method', sa.String(50), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.Column('assignment_reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='assigned'),
        sa.Column('schedule_id', sa.String(36), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('youtube_video_id', sa.String(50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.String(10), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.String(10), nullable=False, server_default='3'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['schedule_id'], ['publication_schedules.id'], ondelete='SET NULL'),
        sa.CheckConstraint(
            "distribution_method IN ('auto_filter', 'auto_schedule', 'manual')",
            name='check_distribution_method'
        ),
        sa.CheckConstraint(
            "status IN ('assigned', 'scheduled', 'published', 'failed', 'cancelled')",
            name='check_distribution_status'
        ),
    )
    
    # Create indexes for common queries
    op.create_index('ix_video_distributions_video_id', 'video_distributions', ['video_id'])
    op.create_index('ix_video_distributions_channel_id', 'video_distributions', ['channel_id'])
    op.create_index('ix_video_distributions_status', 'video_distributions', ['status'])
    op.create_index('ix_video_distributions_method', 'video_distributions', ['distribution_method'])
    op.create_index('ix_video_distributions_assigned_at', 'video_distributions', ['assigned_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_video_distributions_assigned_at', table_name='video_distributions')
    op.drop_index('ix_video_distributions_method', table_name='video_distributions')
    op.drop_index('ix_video_distributions_status', table_name='video_distributions')
    op.drop_index('ix_video_distributions_channel_id', table_name='video_distributions')
    op.drop_index('ix_video_distributions_video_id', table_name='video_distributions')
    
    # Drop table
    op.drop_table('video_distributions')
