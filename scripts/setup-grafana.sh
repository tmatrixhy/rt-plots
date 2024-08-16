#!/bin/bash

# Load environment variables from the .env file
set -o allexport
source ./scripts/sample.env
set +o allexport

echo "Waiting for services to settle..."
sleep 5

# Script to setup Grafana with a PostgreSQL datasource using the API

# Grafana configuration
grafana_host="${SYS_HOSTNAME}"
service_account_name="admin_svc_acc"
service_account_role="Admin"
service_account_token_name="primary-token"

# PostgreSQL datasource configuration
datasource_name="rt-plots"
datasource_access="proxy"
datasource_is_default="true"
datasource_json_data_sslmode="disable"

# Create the service account and get the ID
response=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name":"'${service_account_name}'", "role": "'${service_account_role}'"}' \
  http://${GRAFANA_ADMIN_USER}:${GRAFANA_ADMIN_PASSWORD}@${grafana_host}:${GRAFANA_PORT}/api/serviceaccounts)

service_id=$(echo $response | jq -r '.id')

if [ -z "$service_id" ] || [ "$service_id" == "null" ]; then
  echo "Failed to create the service account or extract the service ID."
  exit 1
fi

# Create the token for the service account and get the key
response=$(curl -s -X POST -H "Content-Type: application/json" \
  -d '{"name":"'${service_account_token_name}'"}' \
  http://${GRAFANA_ADMIN_USER}:${GRAFANA_ADMIN_PASSWORD}@${grafana_host}:${GRAFANA_PORT}/api/serviceaccounts/${service_id}/tokens)

token_key=$(echo $response | jq -r '.key')

if [ -z "$token_key" ] || [ "$token_key" == "null" ]; then
  echo "Failed to create the service account token or extract the token key."
  exit 1
fi

# Use the token key to configure the PostgreSQL datasource
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $token_key" \
  -d '{
        "name": "'${datasource_name}'",
        "type": "postgres",
        "url": "'${POSTGRES_HOST}':'${POSTGRES_PORT}'",
        "database": "'${POSTGRES_DB}'",
        "user": "'${POSTGRES_USER}'",
        "password": "'${POSTGRES_PASSWORD}'",
        "access": "'${datasource_access}'",
        "isDefault": '${datasource_is_default}',
        "jsonData": {
          "sslmode": "'${datasource_json_data_sslmode}'"
        }
      }' \
  http://${grafana_host}:${GRAFANA_PORT}/api/datasources)

if [ "$response" -eq 200 ] || [ "$response" -eq 201 ]; then
  echo "Grafana PostgreSQL datasource configured successfully."
else
  echo "Failed to configure Grafana PostgreSQL datasource. HTTP status code: $response"
  exit 1
fi

# Delete the service account
response=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
  -H "Authorization: Bearer $token_key" \
  http://${GRAFANA_ADMIN_USER}:${GRAFANA_ADMIN_PASSWORD}@${grafana_host}:${GRAFANA_PORT}/api/serviceaccounts/${service_id})

if [ "$response" -eq 200 ] || [ "$response" -eq 204 ]; then
  echo "Service account deleted successfully."
else
  echo "Failed to delete service account. HTTP status code: $response"
  exit 1
fi