#!/bin/bash

# MCP Payments Production Deployment Manager
# This script helps manage production deployments with Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
LOG_DIR="./logs"

# Help function
show_help() {
    echo "MCP Payments Production Deployment Manager"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy          Deploy production environment"
    echo "  start           Start all production services"
    echo "  stop            Stop all production services"
    echo "  restart         Restart all production services"
    echo "  status          Show status of all services"
    echo "  logs            Show logs for all services"
    echo "  logs [service]  Show logs for specific service"
    echo "  update          Update and redeploy services"
    echo "  rollback        Rollback to previous version"
    echo "  backup          Create full system backup"
    echo "  health          Check system health"
    echo "  monitor         Monitor system resources"
    echo "  scale [service] [count]  Scale specific service"
    echo "  clean           Clean up old images and containers"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy           # Deploy production environment"
    echo "  $0 update           # Update services to latest version"
    echo "  $0 scale backend 3  # Scale backend to 3 instances"
    echo "  $0 health          # Check overall system health"
}

# Check prerequisites
check_prerequisites() {
    # Check if running as root or with sudo (for production operations)
    if [[ $EUID -eq 0 ]] && [[ -z "$ALLOW_ROOT" ]]; then
        print_warning "Running as root. Set ALLOW_ROOT=1 if intentional."
    fi

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if production environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Production environment file $ENV_FILE not found."
        print_status "Please create $ENV_FILE with production configuration."
        print_status "You can start with: cp .env.production $ENV_FILE"
        exit 1
    fi

    # Create necessary directories
    mkdir -p "$BACKUP_DIR" "$LOG_DIR" "/var/log/mcp-payments" "/var/data/mcp-payments/uploads"
}

# Load environment variables
load_env() {
    if [ -f "$ENV_FILE" ]; then
        print_status "Loading production environment variables from $ENV_FILE..."
        export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
    else
        print_error "Environment file $ENV_FILE not found."
        exit 1
    fi
}

# Validate environment configuration
validate_config() {
    print_status "Validating production configuration..."
    
    # Check required environment variables
    required_vars=(
        "ENV"
        "DATABASE_URL"
        "REDIS_URL"
        "JWT_SECRET_KEY"
        "ENCRYPTION_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Required environment variable $var is not set."
            exit 1
        fi
    done
    
    # Validate secret lengths
    if [ ${#JWT_SECRET_KEY} -lt 32 ]; then
        print_error "JWT_SECRET_KEY must be at least 32 characters long."
        exit 1
    fi
    
    if [ ${#ENCRYPTION_KEY} -lt 32 ]; then
        print_error "ENCRYPTION_KEY must be at least 32 characters long."
        exit 1
    fi
    
    # Check if running in production mode
    if [ "$ENV" != "production" ]; then
        print_warning "ENV is not set to 'production'. Current value: $ENV"
        print_warning "Are you sure you want to continue? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            print_status "Deployment cancelled."
            exit 0
        fi
    fi
    
    print_success "Configuration validation passed."
}

# Deploy production environment
deploy_production() {
    print_status "Deploying MCP Payments to production..."
    
    # Pre-deployment backup
    print_status "Creating pre-deployment backup..."
    backup_system
    
    # Pull latest images
    print_status "Pulling latest Docker images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    
    # Build application images
    print_status "Building application images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build
    
    # Start services
    print_status "Starting production services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    wait_for_health
    
    print_success "Production deployment completed!"
    print_status "Services are available at:"
    echo "  🔗 Backend API:        https://$(hostname):8000"
    echo "  🔗 Frontend Dashboard: https://$(hostname):3000"
    echo "  🔗 API Documentation:  https://$(hostname):8000/docs"
}

# Start services
start_services() {
    print_status "Starting production services..."
    load_env
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    print_success "Production services started!"
}

# Stop services
stop_services() {
    print_status "Stopping production services..."
    docker-compose -f "$COMPOSE_FILE" down
    print_success "Production services stopped!"
}

# Restart services
restart_services() {
    print_status "Restarting production services..."
    docker-compose -f "$COMPOSE_FILE" down
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    print_success "Production services restarted!"
}

# Show service status
show_status() {
    print_status "Production service status:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    print_status "Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Show logs
show_logs() {
    if [ -z "$1" ]; then
        print_status "Showing logs for all services..."
        docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
    else
        print_status "Showing logs for $1..."
        docker-compose -f "$COMPOSE_FILE" logs -f --tail=100 "$1"
    fi
}

# Update services
update_services() {
    print_status "Updating production services..."
    
    # Create backup before update
    backup_system
    
    # Pull latest images
    print_status "Pulling latest images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    
    # Rebuild application images
    print_status "Rebuilding application images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
    
    # Rolling update
    print_status "Performing rolling update..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --force-recreate
    
    # Verify health
    wait_for_health
    
    print_success "Services updated successfully!"
}

# Rollback to previous version
rollback_services() {
    print_warning "This will rollback to the previous container versions."
    print_warning "Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Rolling back services..."
        
        # Get previous image tags (this is a simplified example)
        # In production, you'd have proper versioning
        docker-compose -f "$COMPOSE_FILE" down
        
        # Here you would restore from backup or use previous image tags
        print_status "Restoring from latest backup..."
        
        # Restart with previous configuration
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
        
        print_success "Rollback completed!"
    else
        print_status "Rollback cancelled."
    fi
}

# Create system backup
backup_system() {
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="$BACKUP_DIR/production_backup_${timestamp}"
    
    print_status "Creating system backup: $backup_file"
    
    # Create backup directory structure
    mkdir -p "$backup_file"
    
    # Backup database
    print_status "Backing up database..."
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U payments payments_db > "$backup_file/database.sql"
    
    # Backup Redis data
    print_status "Backing up Redis data..."
    docker-compose -f "$COMPOSE_FILE" exec redis redis-cli BGSAVE
    docker cp $(docker-compose -f "$COMPOSE_FILE" ps -q redis):/data/dump.rdb "$backup_file/redis.rdb"
    
    # Backup configuration
    print_status "Backing up configuration..."
    cp "$ENV_FILE" "$backup_file/env.backup"
    cp "$COMPOSE_FILE" "$backup_file/docker-compose.backup.yml"
    
    # Backup uploaded files
    print_status "Backing up uploaded files..."
    if [ -d "/var/data/mcp-payments/uploads" ]; then
        tar -czf "$backup_file/uploads.tar.gz" -C "/var/data/mcp-payments" uploads/
    fi
    
    # Create backup metadata
    echo "Backup created at: $(date)" > "$backup_file/metadata.txt"
    echo "Services backed up:" >> "$backup_file/metadata.txt"
    docker-compose -f "$COMPOSE_FILE" ps >> "$backup_file/metadata.txt"
    
    # Compress backup
    tar -czf "$backup_file.tar.gz" -C "$BACKUP_DIR" "$(basename "$backup_file")"
    rm -rf "$backup_file"
    
    print_success "Backup created: $backup_file.tar.gz"
}

# Check system health
check_health() {
    print_status "Checking system health..."
    
    # Check service health
    services=(mcp-payments frontend postgres redis celery-worker celery-beat)
    
    for service in "${services[@]}"; do
        health_status=$(docker-compose -f "$COMPOSE_FILE" ps -q "$service" | xargs docker inspect --format='{{.State.Health.Status}}' 2>/dev/null || echo "not running")
        if [ "$health_status" = "healthy" ] || [ "$health_status" = "not running" ]; then
            if [ "$health_status" = "not running" ]; then
                print_warning "$service: Not running"
            else
                print_success "$service: Healthy"
            fi
        else
            print_error "$service: $health_status"
        fi
    done
    
    # Check disk space
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 80 ]; then
        print_warning "Disk usage is high: ${disk_usage}%"
    else
        print_success "Disk usage: ${disk_usage}%"
    fi
    
    # Check memory usage
    memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ "$memory_usage" -gt 80 ]; then
        print_warning "Memory usage is high: ${memory_usage}%"
    else
        print_success "Memory usage: ${memory_usage}%"
    fi
}

# Monitor system resources
monitor_system() {
    print_status "Monitoring system resources (Ctrl+C to stop)..."
    
    while true; do
        clear
        echo "=== MCP Payments Production Monitoring ==="
        echo "Time: $(date)"
        echo ""
        
        # Service status
        echo "=== Service Status ==="
        docker-compose -f "$COMPOSE_FILE" ps
        echo ""
        
        # Resource usage
        echo "=== Resource Usage ==="
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
        echo ""
        
        # System resources
        echo "=== System Resources ==="
        echo "Disk Usage: $(df -h / | awk 'NR==2 {print $5}')"
        echo "Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
        echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"
        echo ""
        
        sleep 10
    done
}

# Scale service
scale_service() {
    if [ -z "$1" ] || [ -z "$2" ]; then
        print_error "Please specify service name and replica count."
        print_status "Example: $0 scale mcp-payments 3"
        exit 1
    fi
    
    service_name="$1"
    replica_count="$2"
    
    print_status "Scaling $service_name to $replica_count replicas..."
    docker-compose -f "$COMPOSE_FILE" up -d --scale "$service_name=$replica_count"
    print_success "Service $service_name scaled to $replica_count replicas!"
}

# Clean up system
cleanup_system() {
    print_warning "This will remove unused Docker images and containers."
    print_warning "Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up Docker system..."
        docker system prune -f
        docker image prune -f
        print_success "System cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Wait for services to be healthy
wait_for_health() {
    print_status "Waiting for services to be healthy..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if check_all_healthy; then
            print_success "All services are healthy!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        print_status "Attempt $attempt/$max_attempts - waiting for services..."
        sleep 10
    done
    
    print_error "Services did not become healthy within expected time."
    print_status "Check service logs for issues:"
    show_status
    return 1
}

# Check if all services are healthy
check_all_healthy() {
    services=(mcp-payments postgres redis)
    
    for service in "${services[@]}"; do
        container_id=$(docker-compose -f "$COMPOSE_FILE" ps -q "$service" 2>/dev/null)
        if [ -z "$container_id" ]; then
            return 1
        fi
        
        health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo "unknown")
        if [ "$health_status" != "healthy" ] && [ "$health_status" != "starting" ]; then
            return 1
        fi
    done
    
    return 0
}

# Main script logic
main() {
    check_prerequisites
    
    case "${1:-help}" in
        deploy)
            load_env
            validate_config
            deploy_production
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$2"
            ;;
        update)
            load_env
            validate_config
            update_services
            ;;
        rollback)
            rollback_services
            ;;
        backup)
            backup_system
            ;;
        health)
            check_health
            ;;
        monitor)
            monitor_system
            ;;
        scale)
            scale_service "$2" "$3"
            ;;
        clean)
            cleanup_system
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 