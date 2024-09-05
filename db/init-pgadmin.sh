#!/bin/bash

PGADMIN_URL="http://pgadmin:80"
DB_HOST="postgres"
DB_PORT="5432"

# Get CSRF tokenl
TOKEN=$(curl -s -X GET -c cookies.txt $PGADMIN_URL/api/v1/servers | jq -r '.csrf_token')

# Create a new server connection
curl -s -X POST -b cookies.txt -H "Content-Type: application/json" -H "X-CSRFToken: $TOKEN" \
  -d "{\"name\": \"myserver\", \"group\": \"Servers\", \"host\": \"$DB_HOST\", \"port\": \"$DB_PORT\", \"username\": \"$POSTGRES_USER\", \"password\": \"$POSTGRES_PASSWORD\", \"ssl_mode\": \"prefer\"}" \
  $PGADMIN_URL/api/v1/servers