# AssetOptima Backend

Enterprise asset management API built with FastAPI, SQLAlchemy, PostgreSQL, and AI-powered analytics.

## Architecture

```
┌─────────────────────────────────────────────┐
│                  Clients                     │
│  (Web, Mobile, Postman, Curl)               │
└──────────────────┬──────────────────────────┘
                   │ HTTP/HTTPS
┌──────────────────▼──────────────────────────┐
│           FastAPI Application                │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │ Middleware│ │Exception │ │ OpenAPI/Swagger│
│  │(Logging, │ │ Handlers │ │ Docs          │  │
│  │ CORS)    │ │          │ │              │  │
│  └────┬─────┘ └────┬─────┘ └──────┬──────┘  │
│       │            │              │          │
│  ┌────▼────────────▼──────────────▼──────┐   │
│  │           API Endpoints (v1)           │   │
│  │  Auth │ Assets │ Software │ Notify    │   │
│  │  AI   │ Master │ Audit               │   │
│  └──────────────────┬────────────────────┘   │
│                     │                        │
│  ┌──────────────────▼────────────────────┐   │
│  │              Services                  │   │
│  │   Business logic, validation, AI       │   │
│  └──────────────────┬────────────────────┘   │
│                     │                        │
│  ┌──────────────────▼────────────────────┐   │
│  │           Repositories                 │   │
│  │      Data access layer (SQLAlchemy)    │   │
│  └──────────────────┬────────────────────┘   │
└─────────────────────┼────────────────────────┘
                      │
┌─────────────────────▼────────────────────────┐
│                PostgreSQL                     │
│           (Primary Data Store)                │
└──────────────────────────────────────────────┘
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `app/api/v1/endpoints/` | REST API route handlers |
| `app/services/` | Business logic layer |
| `app/repositories/` | Database access (SQLAlchemy async) |
| `app/models/` | SQLAlchemy ORM models |
| `app/schemas/` | Pydantic request/response schemas |
| `app/security/` | Auth, password hashing, JWT, RBAC |
| `app/ai/` | AI-powered predictions, anomaly detection |
| `app/core/` | Configuration and logging |
| `app/database/` | DB engine, session, connection management |
| `app/middleware/` | Request logging, CORS |
| `app/exceptions/` | Global exception handlers |

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 15+ (or SQLite for development/testing)
- pip/uv

### Installation

```bash
# Clone repository
git clone <repo-url> && cd AssetOptima/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Environment configuration
cp .env.example .env
# Edit .env with your database credentials
```

### Database Setup

```bash
# Create database
createdb assetoptima

# Run migrations
alembic upgrade head

# Seed demo data (optional)
python scripts/seed_data.py
```

### Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app --cov-report=term-missing

# Specific test file
pytest tests/test_auth.py -v

# Performance benchmarks
pytest tests/test_performance.py -v --benchmark

# Integration tests
pytest tests/test_integration.py -v
```

Tests use an in-memory SQLite database — no PostgreSQL required.

### Test Categories

| File | Coverage |
|------|----------|
| `tests/test_auth.py` | Login, refresh, logout, RBAC, token expiry, inactive user |
| `tests/test_assets.py` | Asset CRUD, assign, return, transfer, QR, history, RBAC |
| `tests/test_master_data.py` | Companies, departments, employees, locations, vendors, roles, users |
| `tests/test_software.py` | Software CRUD, licenses, assignments, usage logs, RBAC |
| `tests/test_notification_audit.py` | Notifications, preferences, audit logs, system activities |
| `tests/test_ai.py` | Chat, predict, anomaly, analytics, prompt injection |
| `tests/test_security.py` | RBAC boundaries, token security, validation, XSS |
| `tests/test_integration.py` | End-to-end business flows across modules |
| `tests/test_performance.py` | Pagination, N+1 detection, concurrency, response time |
| `tests/test_unit_services.py` | Service layer unit tests with mocks |

## Docker

```bash
# Build and run
docker compose up --build

# Run migrations
docker compose exec backend alembic upgrade head

# Seed data
docker compose exec backend python scripts/seed_data.py

# Run tests
docker compose exec backend pytest
```

## API Overview

### Authentication
- `POST /auth/login` — Get access + refresh tokens
- `POST /auth/refresh` — Refresh access token
- `POST /auth/logout` — Invalidate token
- `GET /auth/me` — Current user profile

### Asset Management
- `GET /assets` — List assets (paginated, filterable)
- `POST /assets` — Create asset
- `GET /assets/{id}` — Get asset details
- `PUT /assets/{id}` — Update asset
- `DELETE /assets/{id}` — Soft-delete asset (super_admin only)
- `POST /assets/{id}/assign` — Assign to employee
- `POST /assets/{id}/return` — Return from assignment
- `POST /assets/{id}/transfer` — Transfer to another employee
- `GET /assets/{id}/qr` — Get QR code value
- `GET /assets/{id}/history` — Get assignment history

### Software & License Management
- `POST /software/licenses` — Create license
- `GET /software/licenses/expiring?days=30` — Expiring licenses
- `GET /software/licenses/available` — Licenses with free seats
- `GET /software/licenses/unused` — Licenses with zero allocations
- `POST /software/assignments/assign` — Assign software to employee
- `POST /software/assignments/remove/{id}` — Remove assignment

### AI Endpoints
- `POST /ai/chat` — AI assistant chat
- `POST /ai/predict/licenses` — License predictions
- `POST /ai/anomaly/licenses` — Anomaly detection
- `POST /ai/recommendations` — Software recommendations
- `GET /ai/analytics` — Usage analytics

### Notifications & Audit
- `POST /notifications` — Create notification
- `GET /notifications/unread` — Unread notifications
- `GET /audit-logs` — Audit trail (manager/super_admin)
- `GET /system-activities` — System activity log

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./test.db` | Database connection string |
| `SECRET_KEY` | (required) | JWT signing key (min 32 chars) |
| `REFRESH_SECRET_KEY` | (required) | Refresh token signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `CORS_ORIGINS` | `["*"]` | CORS allowed origins |
| `POSTGRES_POOL_SIZE` | `10` | Connection pool size |
| `POSTGRES_MAX_OVERFLOW` | `20` | Max pool overflow |
| `LOG_LEVEL` | `INFO` | Logging level |
| `LOG_FILE` | (empty) | Log file path (optional) |

## RBAC Roles

| Role | Permissions |
|------|-------------|
| `super_admin` | Full access: create, read, update, delete all resources |
| `it_manager` | Read-only access to all resources + read audit/system logs |
| `it_support` | Read-only access (no audit/system logs), AI chat only |

## Deployment

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for production deployment instructions.

## Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/   # Route handlers
│   ├── services/           # Business logic
│   ├── repositories/       # Data access
│   ├── models/             # ORM models
│   ├── schemas/            # Pydantic schemas
│   ├── security/           # Auth, JWT, RBAC
│   ├── ai/                 # AI services
│   ├── core/               # Config, logging
│   ├── database/           # DB connection
│   ├── middleware/         # Request logging
│   ├── exceptions/        # Error handlers
│   ├── dependencies/      # DI stubs
│   ├── tests/             # Test suite
│   └── main.py            # App entry point
├── alembic/               # DB migrations
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── deployment/            # Production config
├── Dockerfile
└── requirements.txt
```
