FROM mcr.microsoft.com/devcontainers/python:3.11

# Install required packages
RUN apt-get update && apt-get install -y \
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
# RUN curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | sh -s -- --update
# ENV PATH="/home/vscode/.local/bin:${PATH}"


WORKDIR /workspaces/CamOnPrefect