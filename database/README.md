# AssetOptima — Database

PostgreSQL 17+ production database for the AssetOptima Enterprise IT Asset & License Optimizer.

---

## Folder Structure

```
database/
├── schema/
│   └── schema.sql              # Complete database schema (idempotent)
├── migrations/
│   └── 001_initial_schema.sql   # Initial migration wrapper
├── seeds/
│   └── seed_template.sql        # Minimal seed data for development
└── README.md                    # This file
```

---

## Migration Order

When deploying to a new environment, execute in this order:

```
1. database/schema/schema.sql         # Creates everything
   --- OR ---
1. database/migrations/001_initial_schema.sql  # Wrapper with version check
2. database/seeds/seed_template.sql   # (dev only) Seed reference data
```

---

## How to Import

### Option 1: Direct psql import

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE assetoptima;"

# Apply schema
psql -U postgres -d assetoptima -f database/schema/schema.sql

# (Dev only) Seed data
psql -U postgres -d assetoptima -f database/seeds/seed_template.sql
```

### Option 2: Using the migration wrapper

```bash
psql -U postgres -d assetoptima -f database/migrations/001_initial_schema.sql
```

### Option 3: Docker-based (with docker-compose)

```bash
# Start PostgreSQL container
docker compose up -d db

# Copy schema into container
docker cp database/schema/schema.sql postgres:/schema.sql

# Execute inside container
docker exec -i postgres psql -U postgres -d assetoptima -f /schema.sql
```

---

## How to Reset Database

```bash
# Drop and recreate
psql -U postgres -c "DROP DATABASE IF EXISTS assetoptima;"
psql -U postgres -c "CREATE DATABASE assetoptima;"

# Re-apply schema
psql -U postgres -d assetoptima -f database/schema/schema.sql

# (Dev only) Re-seed
psql -U postgres -d assetoptima -f database/seeds/seed_template.sql
```

---

## Rollback

Initial migration (001) is a forward-only schema creation. Rollback requires:

```bash
psql -U postgres -c "DROP DATABASE IF EXISTS assetoptima;"
psql -U postgres -c "CREATE DATABASE assetoptima;"
```

Future migrations should include a `down.sql` for rollback support.

---

## Database Configuration (PostgreSQL 17+)

Recommended `postgresql.conf` settings:

```ini
shared_buffers = '4GB'                  # 25% of RAM
effective_cache_size = '12GB'           # 75% of RAM
work_mem = '64MB'
maintenance_work_mem = '1GB'
random_page_cost = 1.1                  # SSD storage
max_connections = 200
wal_level = replica                     # For PITR / streaming replication
max_wal_size = '4GB'
default_statistics_target = 500
```

---

## Row-Level Security (RLS)

The schema includes RLS policies on all tenant-scoped tables. The backend must set session variables after authentication:

```sql
-- Set by backend after login:
SET app.current_company_id = '<company-uuid>';
SET app.is_super_admin = 'false';  -- or 'true'
```

Policies automatically filter all queries to the current company's data. Super admins can see all companies.

---

## Key Tables

| Table | Purpose | Approx. Row Count (Year 5) |
|-------|---------|---------------------------|
| `companies` | Tenant organizations | 100 |
| `employees` | People employed | 50,000 |
| `assets` | Physical IT assets | 100,000 |
| `asset_assignments` | Current asset holdings | 60,000 |
| `asset_histories` | Immutable asset event log | 1,000,000 |
| `licenses` | Software license seats | 50,000 |
| `software_usage_logs` | Daily usage records (partitioned) | 18,250,000 |
| `audit_logs` | Compliance trail (partitioned) | 5,000,000 |
| `ai_chat_histories` | RAG conversation messages | 500,000 |

---

## Partitioning Strategy (Future)

For production at scale, partition high-volume tables:

| Table | Partition Key | Granularity |
|-------|--------------|-------------|
| `software_usage_logs` | `usage_date` | Monthly |
| `audit_logs` | `created_at` | Monthly |
| `asset_histories` | `created_at` | Quarterly |

Refer to the Database Design Document (`docs/database/database-design.md`) for partitioning DDL patterns.

---

## Related Documents

- `docs/database/database-design.md` — Full database design specification
- `docs/database/entity-relationship-diagram.md` — Complete ERD with Mermaid diagrams
