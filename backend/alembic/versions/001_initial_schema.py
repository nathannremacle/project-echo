"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-23

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create transformation_presets table first (referenced by channels)
    op.create_table(
        'transformation_presets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parameters', sa.Text(), nullable=False),  # JSON
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create music table (referenced by videos)
    op.create_table(
        'music',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('artist', sa.String(255), nullable=True),
        sa.Column('spotify_track_id', sa.String(100), nullable=True, unique=True),
        sa.Column('spotify_track_url', sa.String(500), nullable=True),
        sa.Column('file_path', sa.String(1000), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),  # JSON
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create channels table
    op.create_table(
        'channels',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('youtube_channel_id', sa.String(255), nullable=False, unique=True),
        sa.Column('youtube_channel_url', sa.String(500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('api_credentials_encrypted', sa.Text(), nullable=False),
        sa.Column('posting_schedule', sa.Text(), nullable=False),  # JSON
        sa.Column('content_filters', sa.Text(), nullable=False),  # JSON
        sa.Column('metadata_template', sa.Text(), nullable=False),  # JSON
        sa.Column('effect_preset_id', sa.String(36), nullable=True),
        sa.Column('github_repo_url', sa.String(500), nullable=True),
        sa.Column('github_secret_key_encrypted', sa.Text(), nullable=True),
        sa.Column('phase2_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_publication_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['effect_preset_id'], ['transformation_presets.id'], ondelete='SET NULL'),
    )

    # Create indexes for channels
    op.create_index('idx_channels_is_active', 'channels', ['is_active'])
    op.create_index('idx_channels_youtube_channel_id', 'channels', ['youtube_channel_id'])
    op.create_index('idx_channels_effect_preset_id', 'channels', ['effect_preset_id'])
    op.create_index('idx_channels_created_at', 'channels', ['created_at'])

    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('channel_id', sa.String(36), nullable=False),
        sa.Column('source_url', sa.String(1000), nullable=False),
        sa.Column('source_title', sa.String(500), nullable=False),
        sa.Column('source_creator', sa.String(255), nullable=True),
        sa.Column('source_platform', sa.String(100), nullable=False),
        sa.Column('scraped_at', sa.DateTime(), nullable=False),
        sa.Column('download_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('download_url', sa.String(1000), nullable=True),
        sa.Column('download_size', sa.Integer(), nullable=True),
        sa.Column('download_duration', sa.Integer(), nullable=True),
        sa.Column('download_resolution', sa.String(50), nullable=True),
        sa.Column('transformation_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('transformation_preset_id', sa.String(36), nullable=True),
        sa.Column('transformation_params', sa.Text(), nullable=True),  # JSON
        sa.Column('transformed_url', sa.String(1000), nullable=True),
        sa.Column('transformed_size', sa.Integer(), nullable=True),
        sa.Column('processing_started_at', sa.DateTime(), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(), nullable=True),
        sa.Column('processing_duration', sa.Integer(), nullable=True),
        sa.Column('publication_status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('scheduled_publication_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('youtube_video_id', sa.String(50), nullable=True),
        sa.Column('youtube_video_url', sa.String(500), nullable=True),
        sa.Column('final_title', sa.String(500), nullable=True),
        sa.Column('final_description', sa.Text(), nullable=True),
        sa.Column('final_tags', sa.Text(), nullable=True),  # JSON array
        sa.Column('music_replaced', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('music_track_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['transformation_preset_id'], ['transformation_presets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['music_track_id'], ['music.id'], ondelete='SET NULL'),
        sa.CheckConstraint(
            "download_status IN ('pending', 'downloading', 'downloaded', 'failed')",
            name='check_download_status'
        ),
        sa.CheckConstraint(
            "transformation_status IN ('pending', 'processing', 'transformed', 'failed')",
            name='check_transformation_status'
        ),
        sa.CheckConstraint(
            "publication_status IN ('pending', 'scheduled', 'publishing', 'published', 'failed')",
            name='check_publication_status'
        ),
    )

    # Create indexes for videos
    op.create_index('idx_videos_channel_id', 'videos', ['channel_id'])
    op.create_index('idx_videos_publication_status', 'videos', ['publication_status'])
    op.create_index('idx_videos_download_status', 'videos', ['download_status'])
    op.create_index('idx_videos_transformation_status', 'videos', ['transformation_status'])
    op.create_index('idx_videos_youtube_video_id', 'videos', ['youtube_video_id'])
    op.create_index('idx_videos_created_at', 'videos', ['created_at'])

    # Create video_processing_jobs table
    op.create_table(
        'video_processing_jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('video_id', sa.String(36), nullable=False),
        sa.Column('channel_id', sa.String(36), nullable=False),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='queued'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),  # JSON
        sa.Column('queued_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('github_workflow_run_id', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
        sa.CheckConstraint(
            "job_type IN ('scrape', 'download', 'transform', 'publish')",
            name='check_job_type'
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'processing', 'completed', 'failed', 'retrying')",
            name='check_job_status'
        ),
        sa.CheckConstraint('attempts >= 0', name='check_attempts_positive'),
        sa.CheckConstraint('max_attempts > 0', name='check_max_attempts_positive'),
    )

    # Create indexes for video_processing_jobs
    op.create_index('idx_jobs_video_id', 'video_processing_jobs', ['video_id'])
    op.create_index('idx_jobs_channel_id', 'video_processing_jobs', ['channel_id'])
    op.create_index('idx_jobs_status', 'video_processing_jobs', ['status'])
    op.create_index('idx_jobs_job_type', 'video_processing_jobs', ['job_type'])
    op.create_index('idx_jobs_priority_status', 'video_processing_jobs', ['priority', 'status', 'queued_at'])
    op.create_index('idx_jobs_queued_at', 'video_processing_jobs', ['queued_at'])

    # Create channel_statistics table
    op.create_table(
        'channel_statistics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('channel_id', sa.String(36), nullable=False),
        sa.Column('subscriber_count', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('view_count', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('video_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_views', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('total_videos', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
    )

    # Create indexes for channel_statistics
    op.create_index('idx_channel_stats_channel_id', 'channel_statistics', ['channel_id'])
    op.create_index('idx_channel_stats_timestamp', 'channel_statistics', ['timestamp'])

    # Create video_statistics table
    op.create_table(
        'video_statistics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('video_id', sa.String(36), nullable=False),
        sa.Column('view_count', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comment_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )

    # Create indexes for video_statistics
    op.create_index('idx_video_stats_video_id', 'video_statistics', ['video_id'])
    op.create_index('idx_video_stats_timestamp', 'video_statistics', ['timestamp'])

    # Create system_configuration table
    op.create_table(
        'system_configuration',
        sa.Column('key', sa.String(255), primary_key=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('encrypted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('system_configuration')
    op.drop_table('video_statistics')
    op.drop_table('channel_statistics')
    op.drop_table('video_processing_jobs')
    op.drop_table('videos')
    op.drop_table('channels')
    op.drop_table('music')
    op.drop_table('transformation_presets')
