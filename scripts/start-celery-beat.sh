#!/bin/bash

# Enterprise MCP Payments - Celery Beat Startup Script
# Handles permission issues and Redis-based scheduling

set -e

echo "Starting Celery Beat Scheduler..."

# Create temporary directory for beat schedule
BEAT_DIR="/tmp/celery-beat"
mkdir -p "$BEAT_DIR"
chmod 755 "$BEAT_DIR"

# Set proper permissions
chown -R $(whoami):$(whoami) "$BEAT_DIR" 2>/dev/null || true

# Start celery beat with Redis scheduler
exec celery -A app.tasks.celery_app beat \
    --loglevel=info \
    --scheduler=redbeat.RedBeatScheduler \
    --max-interval=60 