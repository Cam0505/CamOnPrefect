#!/bin/bash

# Force working directory
cd /workspaces/CamOnPrefect

# Debug output
echo "=== ENTRYPOINT DEBUG ==="
echo "Working dir: $(pwd)"
echo "Contents:"
ls -la
echo "DBT dir exists: $(test -d dbt && echo YES || echo NO)"
echo "Pipelines dir exists: $(test -d pipelines && echo YES || echo NO)"

# Execute flow
exec prefect flow-run execute