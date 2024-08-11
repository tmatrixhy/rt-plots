#!/bin/bash

# Wait for PostgreSQL to be available
until psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Start Grafana
/run.sh &

# Wait for Grafana to be available
until curl -s http://localhost:${GRAFANA_PORT}/api/health | grep -q '"database": "ok"'; do
  >&2 echo "Grafana is unavailable - sleeping"
  sleep 1
done

# Set up Grafana datasource for PostgreSQL
curl -X POST -H "Content-Type: application/json" \
     -d '{
           "name": "rt-plots",
           "type": "postgres",
           "url": "'${POSTGRES_HOST}':'${POSTGRES_PORT}'",
           "database": "'${POSTGRES_DB}'",
           "user": "'${POSTGRES_USER}'",
           "password": "'${POSTGRES_PASSWORD}'",
           "access": "proxy",
           "isDefault": true
         }' \
     http://${GRAFANA_ADMIN_USER}:${GRAFANA_ADMIN_PASSWORD}@localhost:${GRAFANA_PORT}/api/datasources

# Wait for Grafana setup to complete
wait
