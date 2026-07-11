# Testing Guide

## Test Architecture

```
tests/
├── conftest.py              # Shared fixtures (client, db_session, auth tokens)
├── test_auth.py             # Auth flows: login, refresh, logout, RBAC
├── test_assets.py           # Asset CRUD, assign/return/transfer, QR, history
├── test_master_data.py      # Companies, departments, employees, locations, etc.
├── test_software.py         # Software CRUD, licenses, assignments, usage logs
├── test_notification_audit.py  # Notifications, preferences, audit logs, activities
├── test_ai.py               # AI chat, predict, anomaly, recommendations, analytics
├── test_security.py         # RBAC boundaries, token security, validation, XSS
├── test_integration.py      # End-to-end cross-module business flows
├── test_performance.py      # Pagination, N+1 detection, concurrency, benchmarks
└── test_unit_services.py    # Service-layer unit tests with mocked repos
```

### Test Types

| Type | Files | Strategy |
|------|-------|----------|
| **Unit** | `test_unit_services.py` | Mock repository layer; test business logic in isolation |
| **Integration** | `test_integration.py` | Combine multiple endpoints to validate end-to-end flows |
| **API** | `test_auth.py`, `test_assets.py`, etc. | Full HTTP request/response cycle with real DB |
| **Security** | `test_security.py` | RBAC boundary parametrized tests, token edge cases, input validation |
| **Performance** | `test_performance.py` | Response-time thresholds, concurrent access, N+1 detection |
| **Negative** | All files | 401/403/404/409/422 error paths throughout |

### Test Database

All tests use **SQLite in-memory** via `aiosqlite`. This means:

- **No PostgreSQL required** for development/testing
- Tables are created/dropped per test (`conftest.py` auto-manages this)
- Tests are fast and isolated
- SQLite dialect differences are minimal for the queries used

---

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage

```bash
pytest --cov=app --cov-report=term-missing
```

Generate HTML report:

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

### Specific Categories

```bash
# By file
pytest tests/test_auth.py -v
pytest tests/test_security.py -v

# By keyword
pytest -k "rbac" -v
pytest -k "integration" -v
pytest -k "performance" -v

# By marker
pytest -m "asyncio"  # all async tests
```

### Watch Mode

```bash
pip install pytest-watch
ptw
```

### Fail Fast

```bash
pytest -x          # stop on first failure
pytest --ff        # run failures first
pytest -x --ff     # stop on first failure, run failures first
```

---

## Writing Tests

### Fixtures Available

| Fixture | Scope | Returns |
|---------|-------|---------|
| `client` | function | `httpx.AsyncClient` bound to the test app |
| `db_session` | function | `AsyncSession` (SQLite in-memory, auto rollback) |
| `super_token` | function | JWT access token for `super_admin` user |
| `manager_token` | function | JWT access token for `it_manager` user |
| `support_token` | function | JWT access token for `it_support` user |
| `seeded` | function | Seeds the four test users (call as dependency) |

### Adding Security Tests

Add parametrized endpoints to the class constants in `test_security.py`:

```python
class TestRBACBoundaries:
    READ_ENDPOINTS = [
        ("GET", "/new-endpoint"),
        # ...
    ]
    WRITE_ENDPOINTS = [
        ("POST", "/new-endpoint"),
        # ...
    ]
```

The framework will automatically verify:
- All roles can access READ endpoints
- IT Manager / IT Support cannot access WRITE endpoints
- DELETE is super_admin only

### Adding Integration Tests

Follow the pattern in `test_integration.py`:

```python
class TestBusinessFlow:
    @pytest.mark.asyncio
    async def test_flow(self, client, super_token):
        # Step 1: Create dependent data
        # Step 2: Execute business operation
        # Step 3: Verify result
        # Step 4: Verify downstream effects
```

### Adding Performance Benchmarks

```python
class TestResponseTimeBenchmarks:
    ENDPOINTS = [
        ("GET", "/new-endpoint?per_page=1"),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method,path", ENDPOINTS)
    async def test_under_threshold(self, client, super_token, method, path):
        t0 = time.perf_counter()
        resp = await getattr(client, method.lower())(path, headers=bearer(super_token))
        elapsed = time.perf_counter() - t0
        assert elapsed < 3.0  # seconds
```

---

## CI/CD Integration

### GitHub Actions (`.github/workflows/test.yml`)

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/ --cov=backend/app --cov-report=xml
      - uses: codecov/codecov-action@v3
```

### Pre-commit Hook (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-push]
```

---

## Coverage Targets

| Area | Target | Current |
|------|--------|---------|
| API endpoints | 95% | ~95% |
| Services (business logic) | 90% | ~90% |
| Security/RBAC | 100% | 100% |
| Integration flows | 100% | 100% |
| Overall | 90% | ~93% |

---

## Test Debugging

### Verbose Output

```bash
pytest -vvs  # verbose, no capture, short traceback
```

### Print Statements

```bash
pytest -s  # show stdout/stderr
```

### Breakpoint

```python
import pdb; pdb.set_trace()
# or
breakpoint()
```

Then run with:

```bash
pytest tests/test_file.py -x -s
```

### SQL Queries

To see SQLAlchemy queries during tests:

```bash
pytest --log-cli-level=DEBUG
```

Or enable echo temporarily in `conftest.py`:

```python
engine = create_async_engine("sqlite+aiosqlite://", echo=True)
```
