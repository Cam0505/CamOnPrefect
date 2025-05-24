#!/bin/bash

# Automatically export all variables from the .env file into the current shell
set -a
source /workspaces/CamOnPrefect/.env
set +a

# Append env loading to .bashrc if not already present
if ! grep -Fq "# Load .env variables" ~/.bashrc; then
  echo -e "\n# Load .env variables" >> ~/.bashrc
  echo "if [ -f /workspaces/CamOnPrefect/.env ]; then export \$(grep -v '^#' /workspaces/CamOnPrefect/.env | xargs); fi" >> ~/.bashrc
fi

# Ensure profile exists and is used
if ! prefect profile ls | grep -q camonprefect; then
  echo "Creating Prefect profile 'camonprefect'..."
  prefect profile create camonprefect
fi

echo "Switching to profile 'camonprefect'..."
prefect profile use camonprefect

echo "🔐 Logging into Prefect Cloud..."

# Attempt to log in to Prefect Cloud using environment variables
if prefect cloud login --key "$PREFECT_API_KEY" --workspace "$PREFECT_WORKSPACE"; then
  echo "✅ Connected to Prefect Cloud workspace: $PREFECT_WORKSPACE"
  prefect config view
else
  echo "❌ Failed to authenticate with Prefect Cloud. Check your .env values."
  exit 1
fi
