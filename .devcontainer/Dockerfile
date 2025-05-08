# Use the official Python 3.11 image as a base
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install required packages
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    curl && \
    # && rm -rf /var/lib/apt/lists/*
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Prefect and tools
RUN pip install prefect psycopg2-binary

# Set working directory to match compose file
WORKDIR /workspaces/CamOnPrefect