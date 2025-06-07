# Multi-stage Dockerfile with development and production targets
FROM python:3.11-slim as base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Development Stage
FROM base as development
# Install development dependencies
COPY requirements/ requirements/
RUN pip install -r requirements/dev.txt

# Install watchdog for file watching in development
RUN pip install watchdog[watchmedo]

# Create app user but don't switch to it yet (for volume mounting)
RUN useradd --create-home --shell /bin/bash app

# Copy source code (will be overridden by volume mount in dev)
COPY app/ ./app/
COPY scripts/ ./scripts/

EXPOSE 8000 9090
USER app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/app"]

# Builder Stage
FROM base as builder  
COPY requirements/ requirements/
RUN pip install --user -r requirements/prod.txt

# Production Stage
FROM python:3.11-slim as production
ENV PATH="/home/app/.local/bin:$PATH"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/app/.local

# Copy application code
COPY --chown=app:app app/ ./app/
COPY --chown=app:app scripts/ ./scripts/

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
