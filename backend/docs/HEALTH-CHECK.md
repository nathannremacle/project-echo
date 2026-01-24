# Health Check Documentation

## Overview

The health check system verifies that all critical components of Project Echo are functioning correctly. It can be accessed via the API endpoint or run as a standalone CLI script.

## Health Check Components

The health check verifies the following components:

1. **Database** - Database connectivity and query execution
2. **GitHub Actions** - Environment detection (if running in CI/CD)
3. **Dependencies** - Required Python packages availability
4. **Configuration** - Configuration loading and critical settings

## API Endpoint

### Endpoint

```
GET /health
```

### Response Format

```json
{
  "status": "healthy" | "degraded" | "unhealthy",
  "timestamp": "2026-01-23T10:00:00Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "ok" | "error",
      "message": "Database connection successful"
    },
    "github_actions": {
      "status": "ok" | "error",
      "message": "GitHub Actions environment detected"
    },
    "dependencies": {
      "status": "ok" | "error",
      "message": "All required dependencies available"
    },
    "configuration": {
      "status": "ok" | "error",
      "message": "Configuration loaded successfully"
    }
  }
}
```

### Status Codes

- **200 OK** - System is healthy (all checks passed)
- **503 Service Unavailable** - System is degraded or unhealthy (some or all checks failed)

### Example Usage

```bash
# Using curl
curl http://localhost:8000/health

# Using Python requests
import requests
response = requests.get("http://localhost:8000/health")
print(response.json())
```

## CLI Script

### Usage

```bash
# From backend directory
python scripts/health_check.py

# Or make it executable
chmod +x scripts/health_check.py
./scripts/health_check.py
```

### Output

The script outputs JSON to stdout, making it suitable for parsing by monitoring tools:

```json
{
  "status": "healthy",
  "timestamp": "2026-01-23T10:00:00Z",
  "version": "1.0.0",
  "checks": {
    ...
  }
}
```

### Exit Codes

- **0** - System is healthy
- **1** - System is degraded (some checks failed)
- **2** - System is unhealthy (all checks failed or script error)

### Example in Scripts

```bash
#!/bin/bash
if python scripts/health_check.py; then
  echo "System is healthy"
else
  echo "System health check failed"
  exit 1
fi
```

## Component Checks

### Database Check

Verifies database connectivity by executing a simple query (`SELECT 1`).

**Success Criteria:**
- Database connection can be established
- Query can be executed successfully

**Common Failures:**
- Database server not running
- Invalid `DATABASE_URL` in configuration
- Network connectivity issues
- Database permissions issues

### GitHub Actions Check

Detects if the system is running in a GitHub Actions environment.

**Success Criteria:**
- `GITHUB_ACTIONS` environment variable is set to `"true"` (if in CI)
- Or system is running locally (not an error)

**Note:** This check always returns "ok" - it's informational only. Running locally is not considered an error.

### Dependencies Check

Verifies that all required Python packages are installed and importable.

**Required Dependencies:**
- fastapi
- sqlalchemy
- pydantic
- uvicorn
- alembic
- googleapiclient (YouTube API)
- boto3 (AWS S3)
- yt_dlp (video downloading)
- cv2 (opencv-python)
- github (PyGithub)
- httpx
- requests
- jose (python-jose)
- cryptography

**Success Criteria:**
- All required dependencies can be imported

**Common Failures:**
- Missing package installation
- Virtual environment not activated
- Package version incompatibility

### Configuration Check

Verifies that critical configuration settings are loaded correctly.

**Success Criteria:**
- `DATABASE_URL` is set
- In production: `JWT_SECRET_KEY` and `ENCRYPTION_KEY` are set

**Common Failures:**
- Missing environment variables
- Invalid configuration values
- Configuration file not found

## Overall Status

The overall health status is determined by the individual component checks:

- **healthy** - All checks passed
- **degraded** - Some checks failed (partial functionality)
- **unhealthy** - All checks failed (system not operational)

## GitHub Actions Integration

The health check is automatically run in the CI pipeline after dependency installation:

```yaml
- name: Run health check
  run: python scripts/health_check.py
  continue-on-error: true
```

This allows early detection of environment or dependency issues in CI/CD.

## Monitoring

### Using Health Check for Monitoring

The health check endpoint can be used with monitoring tools:

**Prometheus:**
```yaml
scrape_configs:
  - job_name: 'project-echo'
    metrics_path: '/health'
    static_configs:
      - targets: ['localhost:8000']
```

**Uptime Monitoring:**
- Set up HTTP checks pointing to `/health`
- Alert on 503 status codes
- Monitor response time

**Custom Monitoring Script:**
```python
import requests
import sys

response = requests.get("http://localhost:8000/health", timeout=5)
data = response.json()

if data["status"] != "healthy":
    print(f"Health check failed: {data['status']}")
    sys.exit(1)
```

## Troubleshooting

### Database Check Fails

1. Verify database is running:
   ```bash
   # For SQLite
   ls -la data/project_echo.db
   
   # For PostgreSQL
   psql -h localhost -U user -d project_echo -c "SELECT 1"
   ```

2. Check `DATABASE_URL` in `.env`:
   ```bash
   cat .env | grep DATABASE_URL
   ```

3. Test connection manually:
   ```python
   from src.database import SessionLocal
   db = SessionLocal()
   db.execute("SELECT 1")
   ```

### Dependencies Check Fails

1. Verify virtual environment is activated
2. Install missing dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check specific import:
   ```python
   python -c "import fastapi; print('OK')"
   ```

### Configuration Check Fails

1. Verify `.env` file exists and is readable
2. Check required environment variables:
   ```bash
   python -c "from src.config import settings; print(settings.DATABASE_URL)"
   ```

3. In production, ensure secrets are set:
   ```bash
   echo $JWT_SECRET_KEY
   echo $ENCRYPTION_KEY
   ```

## Best Practices

1. **Run health check before deployment** - Verify system is ready
2. **Monitor health check endpoint** - Set up alerts for failures
3. **Include in CI/CD** - Catch issues early in pipeline
4. **Log health check results** - Track system health over time
5. **Use for load balancer health checks** - Route traffic only to healthy instances

## Related Documentation

- [Database Setup](../docs/DATABASE.md)
- [Configuration Management](../docs/SETUP.md)
- [CI/CD Pipeline](../../docs/GITHUB-ACTIONS-SETUP.md)
