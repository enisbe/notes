FROM postgres:16

# Core Postgres settings (built‑in variables)
ENV POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=mydb            # ← default DB will be created for you

# Your own variables
ENV DB_SCHEMA=myschema          # ← script will read this

# Copy and make the script executable
COPY init_db.sh /docker-entrypoint-initdb.d/01_init_db.sh
RUN chmod +x /docker-entrypoint-initdb.d/01_init_db.sh
