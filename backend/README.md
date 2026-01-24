# Project Echo Backend

FastAPI orchestration service for managing multi-channel YouTube automation.

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e ../shared  # Install shared libraries
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database:**
   ```bash
   alembic upgrade head
   ```

## Development

**Run development server:**
```bash
uvicorn src.main:app --reload
```

**Run tests:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=src --cov-report=html
```

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── routes/              # API route modules
│   ├── services/            # Business logic layer
│   ├── repositories/        # Data access layer
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── middleware/          # FastAPI middleware
│   ├── utils/               # Utility functions
│   └── config.py            # Configuration management
├── tests/                   # Backend tests
├── alembic/                 # Database migrations
└── requirements.txt         # Python dependencies
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Environment Variables

See `.env.example` for all required environment variables.

## Database Migrations

**Create migration:**
```bash
alembic revision --autogenerate -m "description"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1
```
