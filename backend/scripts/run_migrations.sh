#!/usr/bin/env bash
# =============================================================================
# AssetOptima — Database Migration Runner
# =============================================================================
# Usage:
#   ./scripts/run_migrations.sh          # Apply all pending migrations
#   ./scripts/run_migrations.sh downgrade # Rollback the last migration
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

cd "$BACKEND_DIR"

# Ensure we have the required packages
pip install -q alembic psycopg2-binary

COMMAND="${1:-upgrade}"

if [ "$COMMAND" = "downgrade" ]; then
    echo "Rolling back last migration..."
    alembic downgrade -1
else
    echo "Applying pending migrations..."
    alembic upgrade head
fi

echo "Migration '$COMMAND' completed successfully."
