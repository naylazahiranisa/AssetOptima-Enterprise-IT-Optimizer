# Deployment Guide

## Deployment Options

- [Docker Compose (recommended)](#docker-compose)
- [Manual Deployment](#manual-deployment)
- [Cloud Deployment](#cloud-deployment)

---

## Docker Compose

### Prerequisites
- Docker Engine 24+
- Docker Compose v2+

### Steps

1. **Prepare environment**

```bash
cd AssetOptima
cp backend/.env.example .env
# Edit .env with production values (see below)
```

2. **Configure production environment**

```bash
# Required: strong unique secrets
SECRET_KEY=<openssl rand -hex 32>
REFRESH_SECRET_KEY=<openssl rand -hex 32>

# Database
POSTGRES_USER=assetoptima
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=assetoptima
DATABASE_URL=postgresql+asyncpg://assetoptima:<password>@postgres:5432/assetoptima

# Security
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

3. **Deploy**

```bash
# Build and start
docker compose up -d --build

# Verify health
docker compose ps
curl http://localhost:8000/health

# Run migrations
docker compose exec backend alembic upgrade head

# Seed initial data (optional)
docker compose exec backend python scripts/seed_data.py
```

4. **Monitor**

```bash
# Logs
docker compose logs -f backend

# Resource usage
docker stats
```

### Production `docker-compose.override.yml`

```yaml
services:
  backend:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"

  postgres:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    volumes:
      - pgdata:/var/lib/postgresql/data
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"
```

---

## Manual Deployment

### System Requirements

- Linux server (Ubuntu 22.04+ or RHEL 9+)
- Python 3.12+
- PostgreSQL 15+
- Nginx or Apache (reverse proxy)
- Supervisor or systemd (process manager)

### Steps

**1. Server Preparation**

```bash
apt update && apt upgrade -y
apt install -y python3.12 python3.12-venv postgresql nginx supervisor
```

**2. Database Setup**

```bash
sudo -u postgres psql
CREATE USER assetoptima WITH PASSWORD 'strong-password';
CREATE DATABASE assetoptima OWNER assetoptima;
\q
```

**3. Application Setup**

```bash
# Deploy code
mkdir -p /opt/assetoptima
rsync -avz ./ /opt/assetoptima/ --exclude .venv --exclude __pycache__

# Python environment
cd /opt/assetoptima/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env with production values

# Run migrations
alembic upgrade head
```

**4. Systemd Service**

Create `/etc/systemd/system/assetoptima-backend.service`:

```ini
[Unit]
Description=AssetOptima Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/assetoptima/backend
Environment=PATH=/opt/assetoptima/backend/.venv/bin
ExecStart=/opt/assetoptima/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now assetoptima-backend
```

**5. Nginx Reverse Proxy**

```nginx
server {
    listen 80;
    server_name api.assetoptima.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    location /static/ {
        alias /opt/assetoptima/backend/static/;
        expires 7d;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/assetoptima /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

**6. SSL (Let's Encrypt)**

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d api.assetoptima.com
```

---

## Cloud Deployment

### AWS ECS (Fargate)

1. Push Docker image to ECR
2. Create ECS task definition with backend + sidecar containers
3. Configure ALB with SSL termination
4. Use RDS PostgreSQL and ElastiCache Redis
5. Enable CloudWatch logging

### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/$PROJECT/assetoptima-backend
gcloud run deploy assetoptima-backend \
  --image gcr.io/$PROJECT/assetoptima-backend \
  --add-cloudsql-instances $PROJECT:region:instance \
  --set-env-vars="DATABASE_URL=postgresql+asyncpg://..."
```

### Azure App Service

1. Create App Service with Python 3.12 stack
2. Configure PostgreSQL Flexible Server
3. Deploy via GitHub Actions or Azure CLI
4. Enable Application Insights for monitoring

---

## Environment Reference

### Production Configuration Template

See `deployment/production.env` for the full template.

### Critical Security Settings

| Variable | Production Guidance |
|----------|-------------------|
| `SECRET_KEY` | **Required**. Generate with `openssl rand -hex 32`. Never commit. |
| `REFRESH_SECRET_KEY` | **Required**. Different from SECRET_KEY. |
| `DATABASE_URL` | Use connection pooling (e.g., PgBouncer) for high traffic. |
| `CORS_ORIGINS` | Restrict to your frontend domain(s). Never use `["*"]` in production. |
| `LOG_LEVEL` | Set to `WARNING` or `ERROR` in production to reduce noise. |
| `POSTGRES_POOL_SIZE` | Tune based on expected concurrent connections (start: 10-20). |

---

## Health Checks

The application exposes:
- `GET /health` — Basic health (returns `{"status": "healthy"}`)
- Docker HEALTHCHECK runs every 30s with 3 retries
- Add external monitoring (Pingdom, UptimeRobot, AWS CloudWatch)

## Backup & Restore

### PostgreSQL

```bash
# Backup
pg_dump -U assetoptima assetoptima > backup_$(date +%Y%m%d).sql

# Restore
psql -U assetoptima assetoptima < backup_20260101.sql

# Docker
docker compose exec postgres pg_dump -U assetoptima assetoptima > backup.sql
```

### Automated backup (cron)

```bash
0 2 * * * pg_dump -U assetoptima assetoptima | gzip > /backups/assetoptima_$(date +\%Y\%m\%d).sql.gz
```

---

## Monitoring & Alerting

### Prometheus + Grafana

Add `prometheus-fastapi-instrumentator` to expose metrics:

```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

### Key Metrics

- Request rate, latency (p50/p95/p99), error rate
- Database connection pool utilization
- Active users and token usage
- Asset/license counts

### Logging

- Logs go to stdout by default (Docker-friendly)
- Production: configure `LOG_FILE` or use Docker logging driver
- Aggregate with ELK/Loki/Datadog

---

## Rollback Plan

1. **Docker**: `docker compose down` then redeploy previous image tag:

```bash
docker compose up -d --build  # builds current
# OR revert to specific image:
docker compose up -d  # if images are tagged
```

2. **Database**: Downgrade migration:

```bash
docker compose exec backend alembic downgrade -1
```

3. **Verify**: Check health endpoint, run smoke tests, monitor error rate.
