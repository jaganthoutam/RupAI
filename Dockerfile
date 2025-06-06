# Multi-stage production Dockerfile
FROM python:3.11-slim as builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements/ requirements/
RUN pip install --user -r requirements/prod.txt

FROM python:3.11-slim as runtime
ENV PATH="/home/app/.local/bin:$PATH"
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app
COPY --from=builder /root/.local /home/app/.local
COPY --chown=app:app app/ ./app/
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "-m", "app.main"]
