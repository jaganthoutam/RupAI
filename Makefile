# MCP Payments Enterprise - Development Makefile

# Variables
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker-compose

# Default target
.PHONY: help
help:
	@echo "🚀 MCP Payments Enterprise - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "📋 Setup Commands:"
	@echo "  make install          Install dependencies"
	@echo "  make install-test     Install test dependencies"
	@echo "  make setup-dev        Setup development environment"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  make docker-build     Build all Docker containers"
	@echo "  make docker-up        Start all services"
	@echo "  make docker-down      Stop all services"
	@echo "  make docker-logs      View container logs"
	@echo "  make docker-clean     Clean containers and volumes"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  make test             Run unit tests"
	@echo "  make test-e2e         Run end-to-end tests"
	@echo "  make test-all         Run all tests"
	@echo "  make test-coverage    Run tests with coverage"
	@echo "  make test-performance Run performance tests"
	@echo ""
	@echo "🔍 Quality Commands:"
	@echo "  make lint             Run code linting"
	@echo "  make format           Format code"
	@echo "  make type-check       Run type checking"
	@echo "  make security-scan    Run security analysis"
	@echo ""
	@echo "📊 Monitoring Commands:"
	@echo "  make health-check     Check system health"
	@echo "  make logs             View application logs"
	@echo "  make metrics          View system metrics"
	@echo ""

# Setup Commands
.PHONY: install
install:
	$(PIP) install -r requirements/base.txt

.PHONY: install-test
install-test:
	$(PIP) install -r tests/requirements.txt

.PHONY: setup-dev
setup-dev: install install-test
	$(PIP) install -r requirements/dev.txt
	pre-commit install

# Docker Commands
.PHONY: docker-build
docker-build:
	$(DOCKER_COMPOSE) build

.PHONY: docker-up
docker-up:
	$(DOCKER_COMPOSE) up -d
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@make health-check

.PHONY: docker-down
docker-down:
	$(DOCKER_COMPOSE) down

.PHONY: docker-logs
docker-logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: docker-clean
docker-clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans
	docker system prune -f

# Testing Commands
.PHONY: test
test:
	pytest tests/unit/ -v

.PHONY: test-e2e
test-e2e:
	@echo "🚀 Starting MCP Payments E2E Test Suite..."
	@echo "=========================================="
	@$(PYTHON) scripts/run_e2e_tests.py

.PHONY: test-e2e-verbose
test-e2e-verbose:
	@echo "🚀 Starting MCP Payments E2E Test Suite (Verbose)..."
	@echo "================================================="
	@$(PYTHON) tests/e2e/test_mcp_payments_e2e.py

.PHONY: test-all
test-all: test test-e2e

.PHONY: test-coverage
test-coverage:
	pytest tests/unit/ --cov=app --cov-report=html --cov-report=term

.PHONY: test-performance
test-performance:
	locust -f tests/performance/locustfile.py --headless -u 100 -r 10 -t 60s

# Quality Commands
.PHONY: lint
lint:
	flake8 app/ tests/
	black --check app/ tests/
	isort --check-only app/ tests/

.PHONY: format
format:
	black app/ tests/
	isort app/ tests/

.PHONY: type-check
type-check:
	mypy app/

.PHONY: security-scan
security-scan:
	bandit -r app/
	safety check

# Monitoring Commands
.PHONY: health-check
health-check:
	@echo "🏥 Checking system health..."
	@curl -s http://localhost:8000/health | jq . || echo "❌ Health check failed"

.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f backend

.PHONY: metrics
metrics:
	@echo "📊 System Metrics:"
	@curl -s http://localhost:8000/api/v1/monitoring/system-metrics | jq . || echo "❌ Metrics unavailable"

# Development Commands
.PHONY: dev-server
dev-server:
	cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8000

.PHONY: dev-frontend
dev-frontend:
	cd frontend && npm start

.PHONY: db-migrate
db-migrate:
	alembic upgrade head

.PHONY: db-reset
db-reset:
	alembic downgrade base
	alembic upgrade head

# Quick Tests
.PHONY: quick-test
quick-test:
	@echo "⚡ Quick System Test"
	@echo "==================="
	@echo "🔍 Health Check:"
	@curl -s http://localhost:8000/health | jq '.status' || echo "❌ Failed"
	@echo ""
	@echo "💰 Revenue Analytics:"
	@curl -s http://localhost:8000/api/v1/analytics/revenue?days=1 | jq '.total_revenue' || echo "❌ Failed"
	@echo ""
	@echo "💳 Payments API:"
	@curl -s http://localhost:8000/api/v1/payments?limit=1 | jq 'length' || echo "❌ Failed"
	@echo ""
	@echo "👛 Wallets API:"
	@curl -s http://localhost:8000/api/v1/wallets?limit=1 | jq 'length' || echo "❌ Failed"

# Production Commands
.PHONY: prod-build
prod-build:
	docker build -t mcp-payments:latest .

.PHONY: prod-deploy
prod-deploy: prod-build
	@echo "🚀 Deploying to production..."
	# Add production deployment commands here

# Cleanup Commands
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf htmlcov/
	rm -rf .coverage

.PHONY: clean-all
clean-all: clean docker-clean

# Backup Commands
.PHONY: backup-db
backup-db:
	$(DOCKER_COMPOSE) exec postgres pg_dump -U payments payments > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Documentation
.PHONY: docs
docs:
	cd docs && mkdocs serve

# All-in-one commands
.PHONY: start
start: docker-up
	@echo "🎉 MCP Payments system is starting up!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

.PHONY: stop
stop: docker-down
	@echo "🛑 MCP Payments system stopped"

.PHONY: restart
restart: stop start
	@echo "🔄 MCP Payments system restarted"

.PHONY: status
status:
	@echo "📊 MCP Payments System Status"
	@echo "=============================="
	@$(DOCKER_COMPOSE) ps

# CI/CD Commands
.PHONY: ci-test
ci-test: install-test lint type-check test test-coverage security-scan

.PHONY: ci-e2e
ci-e2e: docker-up test-e2e docker-down 