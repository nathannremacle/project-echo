# Alembic Migrations

This directory contains database migration scripts managed by Alembic.

## Usage

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply migrations up to a specific revision
alembic upgrade <revision_id>
```

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Create empty migration (for manual SQL)
alembic revision -m "description of changes"
```

### Rollback Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### View Migration History

```bash
# View all migrations
alembic history

# View current revision
alembic current
```

## Migration Files

Migration files are stored in `alembic/versions/` and follow the naming pattern:
- `001_initial_schema.py` - Initial database schema
- `002_<description>.py` - Subsequent migrations

## Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations** on development database first
3. **Backup database** before running migrations in production
4. **Keep migrations small** and focused on one change
5. **Never edit existing migrations** - create new ones instead

## Troubleshooting

### Migration Conflicts

If migrations conflict:
1. Check current revision: `alembic current`
2. Review migration history: `alembic history`
3. Resolve conflicts manually or rollback and recreate

### Model Changes Not Detected

If Alembic doesn't detect model changes:
1. Ensure models are imported in `alembic/env.py`
2. Check that Base.metadata includes all models
3. Verify model changes are saved

---

For more information, see [Database Guide](../docs/DATABASE.md)
