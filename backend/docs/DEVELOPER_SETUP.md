# Developer Setup Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Runtime |
| PostgreSQL | 15+ | Production database |
| Docker Desktop | latest | Containerized development/production |
| Git | 2.40+ | Version control |
| uv / pip | latest | Package management |

## One-Time Setup

### 1. Clone & Navigate

```bash
git clone <repo-url>
cd AssetOptima/backend
```

### 2. Python Environment

```bash
# Using venv (recommended)
python -m venv .venv

# Activate
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
cp .env.example .env
```

Minimum required variables in `.env`:

```ini
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/assetoptima
SECRET_KEY=your-32-char-secret-key-here-change-in-production
REFRESH_SECRET_KEY=your-32-char-refresh-secret-key-here
```

For quick development without PostgreSQL, use SQLite:

```ini
DATABASE_URL=sqlite+aiosqlite:///./dev.db
```

### 4. Database

```bash
# Create database (PostgreSQL)
createdb assetoptima

# Run migrations
alembic upgrade head

# Seed optional demo data
python scripts/seed_data.py
```

### 5. Verify Installation

```bash
# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test health
curl http://localhost:8000/health

# Open API docs
# Navigate to http://localhost:8000/docs
```

## Daily Workflow

### Running the server

```bash
# Development (hot-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production-like
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Running tests

```bash
# Full suite
pytest

# With coverage
pytest --cov=app --cov-report=term-missing --cov-report=html

# Watch mode (install pytest-watch)
ptw

# Specific categories
pytest tests/test_security.py -v
pytest tests/test_integration.py -v
pytest tests/test_performance.py -v
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# View history
alembic history
```

## Docker Workflow

```bash
# Build and run all services
docker compose up --build

# Run specific service
docker compose up backend -d

# Execute commands in container
docker compose exec backend alembic upgrade head
docker compose exec backend pytest
docker compose exec backend python scripts/seed_data.py

# View logs
docker compose logs -f backend

# Clean rebuild
docker compose down -v && docker compose up --build
```

## IDE Setup

### VS Code (recommended)

Install extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Python Test Explorer (littlefoxteam.vscode-python-test-adapter)

`.vscode/settings.json`:

```json
{
  "python.testing.pytestArgs": ["tests"],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

### PyCharm

- Mark `tests` directory as **Test Sources Root**
- Set pytest as default test runner: Settings → Tools → Python Integrated Tools → Testing → pytest
- Enable coverage: Run → Edit Configurations → Add Coverage

## Troubleshooting

### "ModuleNotFoundError"

```bash
pip install -r requirements.txt --force-reinstall
```

### "Database connection refused"

Check PostgreSQL is running:
```bash
pg_isready
# or Docker:
docker compose ps
```

### "Alembic target database is not populated"

```bash
alembic upgrade head
```

### Tests fail with SQLite errors

Ensure you have `aiosqlite` installed:
```bash
pip install aiosqlite
```

### Port 8000 already in use

```bash
# Find process
netstat -ano | findstr :8000
# Kill (Windows)
taskkill /PID <PID> /F
# Kill (Linux/Mac)
kill -9 $(lsof -t -i:8000)
```

## Code Quality

```bash
# Format
ruff format app/

# Lint
ruff check app/ --fix

# Type check
mypy app/

# All checks
ruff format app/ && ruff check app/ --fix && mypy app/
```

## Commit Guidelines

Format: `type(scope): description`

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `security`

Examples:
```
feat(auth): add refresh token rotation
fix(assets): prevent N+1 on assignment history query
test(security): add RBAC boundary parametrized tests
docs: add developer setup guide
```
