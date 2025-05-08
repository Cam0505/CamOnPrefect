#!/bin/bash

# Initialize Prefect profile
prefect profile create default
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
prefect config set PREFECT_UI_URL=http://127.0.0.1:4200

# Fix permissions for Prefect UI
sudo mkdir -p /usr/local/lib/python3.11/site-packages/prefect/server/ui_build
sudo chmod 777 /usr/local/lib/python3.11/site-packages/prefect/server/ui_build

# Start Prefect server with PostgreSQL (detached)
echo "🚀 Starting Prefect server..."
prefect server start --host 0.0.0.0 &

# Wait for server to be ready (optional)
until curl -s http://127.0.0.1:4200/api/health > /dev/null; do
  echo "Waiting for Prefect server..."
  sleep 2
done

echo "✅ Prefect server is up and running!"
prefect config view