# 🐳 Docker Setup Guide - MCP Payments

This guide covers the streamlined Docker setup for the MCP Payments Enterprise system, optimized for both development and production environments.

## 📋 Overview

The Docker setup has been completely redesigned to focus on:
- **Development Efficiency**: Live code reloading without rebuilds
- **Production Ready**: Optimized builds with resource limits
- **Simplified Management**: Easy-to-use scripts and commands
- **Essential Services Only**: Backend, Frontend, PostgreSQL, Redis

## 🗂️ Files Structure

```
├── docker-compose.yml           # Base configuration (development-focused)
├── docker-compose.override.yml  # Development-specific overrides
├── docker-compose.prod.yml      # Production configuration
├── Dockerfile                   # Multi-stage backend Dockerfile
├── frontend/Dockerfile          # Multi-stage frontend Dockerfile
├── .env.development             # Development environment variables
├── .env.production              # Production environment variables
├── scripts/dev.sh               # Development management script
└── docker-compose.full-stack.yml.backup  # Backup of original setup
```

## 🚀 Quick Start

### Development Environment

```bash
# 1. Start development environment
./scripts/dev.sh start

# 2. View all services status
./scripts/dev.sh status

# 3. View logs
./scripts/dev.sh logs

# 4. Start development tools (PGAdmin, Redis Commander)
./scripts/dev.sh tools
```

**Services Available:**
- Backend API: http://localhost:8000
- Frontend Dashboard: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Metrics: http://localhost:9090
- PGAdmin: http://localhost:5050 (when tools are started)
- Redis Commander: http://localhost:8081 (when tools are started)

### Production Environment

```bash
# 1. Create production environment file
cp .env.production .env

# 2. Update production environment variables
nano .env

# 3. Start production environment
docker-compose -f docker-compose.prod.yml --env-file .env up -d

# 4. Check status
docker-compose -f docker-compose.prod.yml ps
```

## 🛠️ Development Features

### Live Code Reloading

The development setup includes automatic code reloading:

**Backend (FastAPI)**:
- Source code mounted as volume: `./app:/app/app:rw`
- Uvicorn with `--reload` flag
- Changes reflect immediately without rebuild

**Frontend (React)**:
- Source code mounted as volume: `./frontend/src:/app/src:rw`
- Hot Module Replacement (HMR) enabled
- `CHOKIDAR_USEPOLLING=true` for Docker file watching

**Celery Workers**:
- Source code mounted as volume
- `watchmedo` auto-restart on Python file changes
- Background tasks update automatically

### Development Tools

Optional development tools can be started with:

```bash
./scripts/dev.sh tools
```

**Includes:**
- **PGAdmin 4**: Database management interface
  - URL: http://localhost:5050
  - Email: admin@payments.local
  - Password: admin123

- **Redis Commander**: Redis management interface
  - URL: http://localhost:8081

### Volume Mounts for Development

```yaml
# Backend
- ./app:/app/app:rw                    # Source code
- ./requirements:/app/requirements:ro  # Requirements (read-only)
- ./logs:/app/logs:rw                  # Logs
- ./data/uploads:/app/uploads:rw       # Uploads

# Frontend  
- ./frontend/src:/app/src:rw           # Source code
- ./frontend/public:/app/public:rw     # Public assets
- /app/node_modules                    # Exclude node_modules
```

## 🔧 Development Script Commands

The `./scripts/dev.sh` script provides comprehensive development environment management:

### Basic Commands
```bash
./scripts/dev.sh start          # Start all services
./scripts/dev.sh stop           # Stop all services  
./scripts/dev.sh restart        # Restart all services
./scripts/dev.sh status         # Show service status
```

### Build Commands
```bash
./scripts/dev.sh build          # Build all images
./scripts/dev.sh rebuild        # Rebuild from scratch (no cache)
```

### Debugging Commands
```bash
./scripts/dev.sh logs           # Show all logs
./scripts/dev.sh logs backend   # Show specific service logs
./scripts/dev.sh shell backend  # Open shell in backend container
./scripts/dev.sh db             # Open PostgreSQL shell
./scripts/dev.sh redis          # Open Redis CLI
```

### Development Tools
```bash
./scripts/dev.sh tools          # Start PGAdmin & Redis Commander
./scripts/dev.sh test           # Run tests
./scripts/dev.sh lint           # Run linting
./scripts/dev.sh format         # Format code
```

### Database Operations
```bash
./scripts/dev.sh backup         # Backup database
./scripts/dev.sh restore backup.sql  # Restore from backup
```

### Maintenance
```bash
./scripts/dev.sh clean          # Clean containers and volumes
```

## 🏗️ Multi-Stage Dockerfiles

### Backend Dockerfile

```dockerfile
# Base stage with common dependencies
FROM python:3.11-slim as base

# Development stage - includes dev tools and live reload
FROM base as development
RUN pip install -r requirements/dev.txt
RUN pip install watchdog[watchmedo]  # For file watching
CMD ["uvicorn", "app.main:app", "--reload"]

# Production stage - optimized and secure
FROM base as production  
RUN pip install --user -r requirements/prod.txt
CMD ["uvicorn", "app.main:app", "--workers", "4"]
```

### Frontend Dockerfile

```dockerfile
# Development stage - with hot reload
FROM node:18-alpine as development
RUN npm install  # All dependencies including dev
CMD ["npm", "start"]  # Development server

# Production stage - with nginx
FROM nginx:alpine as production
COPY --from=builder /app/build /usr/share/nginx/html
CMD ["nginx", "-g", "daemon off;"]
```

## 🔒 Environment Configuration

### Development (.env.development)

```bash
ENV=development
NODE_ENV=development
BUILD_TARGET=development
DEBUG=true
ENABLE_AUTHENTICATION=false
REACT_APP_API_URL=http://localhost:8000
```

### Production (.env.production)

```bash
ENV=production
NODE_ENV=production
BUILD_TARGET=production
DEBUG=false
ENABLE_AUTHENTICATION=true
REACT_APP_API_URL=https://your-domain.com
```

## 🎯 Service Architecture

### Core Services

1. **mcp-payments** (Backend)
   - FastAPI application
   - MCP protocol implementation
   - Payment processing logic

2. **frontend** (React Dashboard)
   - Admin dashboard
   - Payment management UI
   - Analytics and monitoring

3. **postgres** (Database)
   - PostgreSQL 15 with optimized settings
   - Persistent data storage
   - Health checks enabled

4. **redis** (Cache & Message Broker)
   - Redis 7 with persistence
   - Caching and session storage
   - Celery broker and result backend

5. **celery-worker** (Background Tasks)
   - Payment processing tasks
   - Analytics aggregation
   - Notification sending

6. **celery-beat** (Task Scheduler)
   - Periodic task scheduling
   - Automated maintenance tasks

## 🔄 Docker Compose Configurations

### Base Configuration (docker-compose.yml)

Default development-oriented configuration with:
- Environment variable defaults for development
- Health checks for dependencies
- Volume mounts ready for development override

### Override Configuration (docker-compose.override.yml)

Automatically applied in development with:
- Development build targets
- Source code volume mounts
- Live reload configurations
- Development tools with profiles

### Production Configuration (docker-compose.prod.yml)

Production-optimized configuration with:
- Production build targets
- Resource limits and reservations
- Production logging configuration
- Security-focused settings
- Proper restart policies

## 📊 Resource Management

### Development Resources
- Minimal resource constraints
- Focus on development experience
- Optional tools available

### Production Resources
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

## 🔍 Monitoring & Logging

### Development Logging
- Console output for immediate feedback
- Volume-mounted logs directory
- Service-specific log access

### Production Logging
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "50m"
    max-file: "3"
```

## 🚦 Health Checks

All services include health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

## 🔧 Troubleshooting

### Common Issues

**Port Conflicts:**
```bash
# Check what's using the port
lsof -i :8000
# Stop conflicting services or change ports
```

**Permission Issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER ./logs ./data
```

**Container Won't Start:**
```bash
# Check logs
./scripts/dev.sh logs [service-name]
# Rebuild if needed
./scripts/dev.sh rebuild
```

**Live Reload Not Working:**
```bash
# Ensure volume mounts are correct
./scripts/dev.sh status
# Check file watching is enabled
docker-compose exec mcp-payments ps aux | grep uvicorn
```

### Debug Mode

For detailed debugging:

```bash
# Enable debug logging
export DEBUG=true

# Check service logs in detail
./scripts/dev.sh logs backend -f

# Open shell in container for investigation
./scripts/dev.sh shell backend
```

## 🎯 Best Practices

### Development Workflow

1. **Start Clean**: Always start with `./scripts/dev.sh clean` if issues occur
2. **Use Scripts**: Prefer the dev script over direct docker-compose commands
3. **Check Status**: Regular `./scripts/dev.sh status` to monitor services
4. **Monitor Logs**: Keep logs open during development for immediate feedback

### Production Deployment

1. **Environment Variables**: Never commit production secrets
2. **Resource Limits**: Always set appropriate resource limits
3. **Health Checks**: Ensure all health checks are properly configured
4. **Backup Strategy**: Regular database backups before deployments
5. **Rolling Updates**: Use proper deployment strategies for zero downtime

### Security Considerations

1. **Secrets Management**: Use external secret management in production
2. **Network Security**: Implement proper network policies
3. **User Permissions**: Run containers with non-root users
4. **Regular Updates**: Keep base images and dependencies updated

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Documentation](https://fastapi.tiangolo.com/deployment/docker/)
- [React Docker Guide](https://create-react-app.dev/docs/deployment/#docker)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Redis Docker Hub](https://hub.docker.com/_/redis)

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review service logs with `./scripts/dev.sh logs`
3. Ensure all dependencies are properly installed
4. Verify environment variables are correctly set

---

**Note**: This Docker setup replaces the previous full-stack configuration and focuses on the essential application services with development-first approach while maintaining production readiness. 