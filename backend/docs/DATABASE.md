# Database Setup and Management Guide

This guide explains how to set up, manage, and migrate the Project Echo database.

## Database Overview

**MVP:** SQLite (file-based, no setup required)  
**Production:** PostgreSQL (migrated when needed)

**Schema:** 8 core tables
- `channels` - Channel configurations and credentials
- `videos` - Video metadata and processing status
- `video_processing_jobs` - Processing queue
- `transformation_presets` - Reusable effect presets
- `music` - Creator's music tracks (Phase 2)
- `channel_statistics` - Channel performance metrics
- `video_statistics` - Video performance metrics
- `system_configuration` - Global system settings

## Initial Setup

### 1. Create Database Directory

```bash
cd backend
mkdir -p data
```

### 2. Configure Database URL

Edit `.env` file:
```bash
DATABASE_URL=sqlite:///./data/project_echo.db
```

For PostgreSQL (production):
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/project_echo
```

### 3. Run Migrations

```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run migrations
alembic upgrade head
```

This creates all tables with the initial schema.

## Database Migrations

### Using Alembic

**Create a new migration:**
```bash
alembic revision --autogenerate -m "description of changes"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback one migration:**
```bash
alembic downgrade -1
```

**Rollback to specific revision:**
```bash
alembic downgrade <revision_id>
```

**View migration history:**
```bash
alembic history
```

**View current revision:**
```bash
alembic current
```

### Migration Workflow

1. **Make model changes** in `src/models/`
2. **Generate migration:** `alembic revision --autogenerate -m "description"`
3. **Review migration file** in `alembic/versions/`
4. **Test migration:** `alembic upgrade head`
5. **Test rollback:** `alembic downgrade -1` then `alembic upgrade head`

## Backup and Restore

### SQLite Backup

**Create backup:**
```bash
python scripts/backup_database.py backup --output-dir backups
```

**Restore from backup:**
```bash
python scripts/backup_database.py restore --backup-file backups/project_echo_backup_20260123_120000.db
```

**Automatic backup (recommended):**
- Set up cron job or scheduled task
- Backup before migrations
- Keep multiple backup versions

### PostgreSQL Backup

**Using pg_dump:**
```bash
pg_dump -U user -d project_echo > backup_$(date +%Y%m%d).sql
```

**Restore:**
```bash
psql -U user -d project_echo < backup_20260123.sql
```

## Configuration Management

### Loading Configuration

Configuration is loaded with priority:
1. **Environment variables** (highest priority)
2. **Database** (system_configuration table)
3. **Config files** (future)
4. **Defaults** (lowest priority)

### Setting Configuration

**Via code:**
```python
from src.services.config_service import ConfigService

config_service = ConfigService(db)
config_service.set("key", "value", description="Description")
```

**Via database:**
```sql
INSERT INTO system_configuration (key, value, description)
VALUES ('key', '"value"', 'Description');
```

### Default Configurations

Default configurations are set automatically on first run:
- `default_posting_frequency`: "daily"
- `default_min_resolution`: "720p"
- `max_concurrent_jobs`: 5
- `default_retry_attempts`: 3

## PostgreSQL Migration

### Preparation

1. **Backup SQLite database:**
   ```bash
   python scripts/backup_database.py backup
   ```

2. **Install PostgreSQL:**
   - Install PostgreSQL 14+ on your server
   - Create database: `CREATE DATABASE project_echo;`

3. **Update DATABASE_URL:**
   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/project_echo
   ```

### Migration Steps

1. **Test connection:**
   ```python
   from src.database import engine
   engine.connect()
   ```

2. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Verify schema:**
   - Check all tables exist
   - Verify indexes are created
   - Test data access

### Schema Compatibility

The schema is designed to be compatible with both SQLite and PostgreSQL:
- Uses SQLAlchemy abstractions (no raw SQL)
- No SQLite-specific features
- Data types compatible with both databases
- Indexes work on both platforms

## Database Access Patterns

### Using Repositories

```python
from src.database import get_db
from src.repositories.channel_repository import ChannelRepository

# In FastAPI route
def get_channels(db: Session = Depends(get_db)):
    repo = ChannelRepository(db)
    return repo.get_all(active_only=True)
```

### Direct Model Access

```python
from src.database import SessionLocal
from src.models.channel import Channel

db = SessionLocal()
channels = db.query(Channel).filter(Channel.is_active == True).all()
db.close()
```

## Troubleshooting

### Database Locked (SQLite)

**Problem:** `database is locked` error
- **Cause:** Multiple processes accessing database
- **Solution:** Ensure only one process accesses SQLite at a time
- **Production:** Use PostgreSQL for concurrent access

### Migration Fails

**Problem:** Migration fails with errors
- **Check:** Review migration file for syntax errors
- **Solution:** Fix migration file or rollback and recreate
- **Prevention:** Test migrations on development database first

### Connection Errors

**Problem:** Cannot connect to database
- **Check:** DATABASE_URL is correct
- **Check:** Database file exists (SQLite) or server is running (PostgreSQL)
- **Check:** Permissions for database file/directory

### Foreign Key Violations

**Problem:** Foreign key constraint errors
- **Cause:** Referenced record doesn't exist
- **Solution:** Ensure parent records exist before creating child records
- **Check:** Use transactions for related operations

## Best Practices

1. **Always backup before migrations**
2. **Test migrations on development database first**
3. **Use transactions for related operations**
4. **Use repositories for data access (not direct queries)**
5. **Keep migrations small and focused**
6. **Document schema changes in migration messages**
7. **Monitor database size and performance**

## Performance Tips

### SQLite (Development)

- Keep database file size reasonable (< 1GB recommended)
- Use indexes for frequently queried columns
- Vacuum database periodically: `VACUUM;`

### PostgreSQL (Production)

- Use connection pooling (SQLAlchemy handles this)
- Monitor query performance
- Set up read replicas for statistics queries (future)

## Security

### Credential Storage

- Credentials stored encrypted in database
- Encryption key from environment variable (ENCRYPTION_KEY)
- Never commit encryption keys to repository

### Database Access

- Use least privilege principle
- Restrict database access to application only
- Use SSL/TLS for PostgreSQL connections

---

For more information, see:
- [Architecture Document](../docs/architecture.md#database-schema)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
