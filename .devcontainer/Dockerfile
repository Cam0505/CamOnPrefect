FROM mcr.microsoft.com/devcontainers/python:3.11

# Fix for expired Yarn key and installation of system dependencies in one layer
RUN rm -f /etc/apt/sources.list.d/yarn.list && \
    apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# USER vscode
# Correct syntax for dbt installer (if required)
# RUN curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | sh -s -- --update

WORKDIR /workspaces/CamOnPrefect