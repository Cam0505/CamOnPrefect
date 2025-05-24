#!/bin/bash

echo "🔐 Logging into Prefect Cloud..."
if prefect cloud login --key "$PREFECT_API_KEY" --workspace "$PREFECT_WORKSPACE"; then
  echo "✅ Connected to Prefect Cloud workspace: $PREFECT_WORKSPACE"
  prefect config view
else
  echo "❌ Failed to authenticate with Prefect Cloud. Check your .env values."
  exit 1
fi