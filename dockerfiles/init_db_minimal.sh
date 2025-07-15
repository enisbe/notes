#!/usr/bin/env bash
set -euo pipefail

# Official Postgres image already sets these if you used the standard env vars
DB_NAME="${POSTGRES_DB:-mydb}"       # docker run -e POSTGRES_DB=mydb …
DB_SCHEMA="${DB_SCHEMA:-myschema}"   # custom var you add
DB_USER="${POSTGRES_USER:-postgres}" # default super‑user

echo ">> ensure schema '${DB_SCHEMA}' in database '${DB_NAME}'"
# local socket, no host/port needed
psql -v ON_ERROR_STOP=1 \
     --username "$DB_USER" \
     --dbname "$DB_NAME" \
     -c "CREATE SCHEMA IF NOT EXISTS \"${DB_SCHEMA}\";"
