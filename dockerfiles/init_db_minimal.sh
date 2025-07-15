#!/usr/bin/env bash
set -euo pipefail

# Variables supplied via ENV
DB_NAME="${POSTGRES_DB:-postgres}"
SCHEMA_NAME="${DB_SCHEMA:-public}"

# Create schema (idempotent)
psql -v ON_ERROR_STOP=1 \
     --username "$POSTGRES_USER" \
     --dbname "$DB_NAME" <<-EOSQL
  CREATE SCHEMA IF NOT EXISTS "${SCHEMA_NAME}";
EOSQL
