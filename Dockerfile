FROM python:3.12-slim



WORKDIR /workspaces/CamOnPrefect

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . /workspaces/CamOnPrefect

# Set permissions and environment
RUN chmod -R 777 /workspaces/CamOnPrefect

ENV PREFECT_HOME=/workspaces/CamOnPrefect\
    PYTHONPATH=/workspaces/CamOnPrefect/pipelines

# Override entrypoint completely
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]