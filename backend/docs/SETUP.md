# Backend Setup Guide

This guide explains how to set up the Project Echo backend development environment.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

## Virtual Environment Setup

### Create Virtual Environment

**Windows:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### Verify Activation

Your terminal prompt should show `(venv)` prefix when activated.

**Windows:**
```powershell
(venv) PS C:\...\backend>
```

**macOS/Linux:**
```bash
(venv) user@host:~/backend$
```

### Deactivate Virtual Environment

When done working, deactivate the virtual environment:
```bash
deactivate
```

## Install Dependencies

Once the virtual environment is activated:

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Install shared libraries in development mode
cd ../shared
pip install -e .
cd ../backend
```

## Environment Configuration

1. **Copy example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your configuration:
   - Database URL
   - YouTube API credentials
   - AWS credentials
   - GitHub token
   - JWT secret key
   - Encryption key

**Important:** Never commit `.env` file to Git. It contains sensitive information.

## Verify Installation

Run the application to verify everything is set up correctly:

```bash
# From backend directory with venv activated
python -m uvicorn src.main:app --reload
```

You should see:
- FastAPI startup messages
- API documentation available at http://localhost:8000/docs
- Health check endpoint at http://localhost:8000/health

## Development Commands

### Run Development Server
```bash
uvicorn src.main:app --reload
```

### Run Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Lint Code
```bash
ruff check src/
```

### Format Code
```bash
ruff format src/
```

### Type Check
```bash
mypy src/
```

## Troubleshooting

### Virtual Environment Not Activating

**Windows:**
- Ensure you're using PowerShell or Command Prompt (not Git Bash)
- Try: `venv\Scripts\activate.bat` instead

**macOS/Linux:**
- Ensure execute permissions: `chmod +x venv/bin/activate`
- Use `source` command, not just `./venv/bin/activate`

### Import Errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11+)

### Module Not Found

- Ensure you're in the `backend` directory
- Check that `src/` directory exists
- Verify `__init__.py` files are present in all modules

## Next Steps

After setup is complete:
1. Configure environment variables in `.env`
2. Run tests to verify installation
3. Start development server
4. Visit http://localhost:8000/docs for API documentation
