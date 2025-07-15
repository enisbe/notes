#!/usr/bin/env bash
set -euo pipefail

# ── Args ──────────────────────────────────────────────────────────────
# 1  Database name     (default: mydb)
# 2  Schema name       (default: myschema)
# 3  Host              (default: localhost)
# 4  Port              (default: 5432)
# 5  Super‑user name   (default: postgres)
# 6  Super‑user passwd (default: postgres)
# ──────────────────────────────────────────────────────────────────────
DB_NAME=${1:-mydb}
SCHEMA_NAME=${2:-myschema}
PGHOST=${3:-localhost}
PGPORT=${4:-5432}
PGUSER=${5:-postgres}
PGPASSWORD=${6:-postgres}
export PGPASSWORD

# ── Create DB if missing ─────────────────────────────────────────────
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" \
     -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" \
| grep -q 1 || \
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" \
     -c "CREATE DATABASE \"$DB_NAME\";"

# ── Create schema inside that DB (idempotent) ────────────────────────
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$DB_NAME" \
     -c "CREATE SCHEMA IF NOT EXISTS \"$SCHEMA_NAME\";"
echo "Database '$DB_NAME' and schema '$SCHEMA_NAME' ready."
