#!/bin/bash

# MCP Payments Development Environment Manager
# This script helps manage the development environment with Docker Compose

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

# Help function
show_help() {
    echo "MCP Payments Development Environment Manager"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Start all services in development mode"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  build           Build all Docker images"
    echo "  rebuild         Rebuild all Docker images from scratch"
    echo "  logs            Show logs for all services"
    echo "  logs [service]  Show logs for specific service"
    echo "  shell [service] Open shell in service container"
    echo "  db              Open PostgreSQL shell"
    echo "  redis           Open Redis CLI"
    echo "  status          Show status of all services"
    echo "  clean           Clean up containers and volumes"
    echo "  tools           Start development tools (PGAdmin, Redis Commander)"
    echo "  test            Run tests"
    echo "  lint            Run linting checks"
    echo "  format          Format code"
    echo "  backup          Backup database"
    echo "  restore [file]  Restore database from backup"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start development environment"
    echo "  $0 logs backend   # Show backend logs"
    echo "  $0 shell backend  # Open shell in backend container"
    echo "  $0 tools          # Start PGAdmin and Redis Commander"
}

# Check if Docker and Docker Compose are installed
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Load environment variables
load_env() {
    if [ -f .env.development ]; then
        print_status "Loading development environment variables..."
        export $(cat .env.development | grep -v '^#' | xargs)
    else
        print_warning ".env.development not found. Using default values."
    fi
}

# Start services
start_services() {
    print_status "Starting MCP Payments development environment..."
    load_env
    docker-compose --env-file .env.development up -d
    print_success "Development environment started!"
    echo ""
    print_status "Services are available at:"
    echo "  🔗 Backend API:        http://localhost:8000"
    echo "  🔗 Frontend Dashboard: http://localhost:3000"
    echo "  🔗 API Documentation:  http://localhost:8000/docs"
    echo "  🔗 Metrics:            http://localhost:9090"
    echo ""
    print_status "To view logs: $0 logs"
    print_status "To start dev tools: $0 tools"
}

# Stop services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "All services stopped!"
}

# Restart services
restart_services() {
    print_status "Restarting all services..."
    docker-compose down
    docker-compose --env-file .env.development up -d
    print_success "All services restarted!"
}

# Build images
build_images() {
    print_status "Building Docker images..."
    load_env
    docker-compose --env-file .env.development build
    print_success "Images built successfully!"
}

# Rebuild images
rebuild_images() {
    print_status "Rebuilding Docker images from scratch..."
    load_env
    docker-compose --env-file .env.development build --no-cache
    print_success "Images rebuilt successfully!"
}

# Show logs
show_logs() {
    if [ -z "$1" ]; then
        print_status "Showing logs for all services..."
        docker-compose logs -f
    else
        print_status "Showing logs for $1..."
        docker-compose logs -f "$1"
    fi
}

# Open shell in container
open_shell() {
    if [ -z "$1" ]; then
        print_error "Please specify a service name."
        print_status "Available services: mcp-payments, frontend, postgres, redis, celery-worker, celery-beat"
        exit 1
    fi
    
    service_name="$1"
    if [ "$1" = "backend" ]; then
        service_name="mcp-payments"
    fi
    
    print_status "Opening shell in $service_name container..."
    docker-compose exec "$service_name" /bin/bash
}

# Open PostgreSQL shell
open_db_shell() {
    print_status "Opening PostgreSQL shell..."
    docker-compose exec postgres psql -U payments -d payments_db
}

# Open Redis CLI
open_redis_cli() {
    print_status "Opening Redis CLI..."
    docker-compose exec redis redis-cli
}

# Show service status
show_status() {
    print_status "Service status:"
    docker-compose ps
}

# Clean up
cleanup() {
    print_warning "This will remove all containers and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up containers and volumes..."
        docker-compose down -v --remove-orphans
        docker system prune -f
        print_success "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Start development tools
start_tools() {
    print_status "Starting development tools..."
    docker-compose --profile dev-tools up -d pgadmin redis-commander
    print_success "Development tools started!"
    echo ""
    print_status "Development tools are available at:"
    echo "  🔗 PGAdmin:         http://localhost:5050"
    echo "     Email: admin@payments.local"
    echo "     Password: admin123"
    echo "  🔗 Redis Commander: http://localhost:8081"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    docker-compose exec mcp-payments python -m pytest tests/ -v
    print_success "Tests completed!"
}

# Run linting
run_lint() {
    print_status "Running linting checks..."
    docker-compose exec mcp-payments python -m flake8 app/
    docker-compose exec mcp-payments python -m mypy app/
    print_success "Linting completed!"
}

# Format code
format_code() {
    print_status "Formatting code..."
    docker-compose exec mcp-payments python -m black app/
    docker-compose exec mcp-payments python -m isort app/
    print_success "Code formatting completed!"
}

# Backup database
backup_db() {
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="backup_${timestamp}.sql"
    print_status "Creating database backup: $backup_file"
    docker-compose exec postgres pg_dump -U payments payments_db > "backups/$backup_file"
    print_success "Database backup created: backups/$backup_file"
}

# Restore database
restore_db() {
    if [ -z "$1" ]; then
        print_error "Please specify backup file path."
        exit 1
    fi
    
    backup_file="$1"
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_warning "This will restore the database from $backup_file. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Restoring database from $backup_file..."
        docker-compose exec -T postgres psql -U payments payments_db < "$backup_file"
        print_success "Database restored from $backup_file"
    else
        print_status "Database restore cancelled."
    fi
}

# Main script logic
main() {
    check_dependencies
    
    # Create necessary directories
    mkdir -p logs backups data/uploads
    
    case "${1:-help}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        build)
            build_images
            ;;
        rebuild)
            rebuild_images
            ;;
        logs)
            show_logs "$2"
            ;;
        shell)
            open_shell "$2"
            ;;
        db)
            open_db_shell
            ;;
        redis)
            open_redis_cli
            ;;
        status)
            show_status
            ;;
        clean)
            cleanup
            ;;
        tools)
            start_tools
            ;;
        test)
            run_tests
            ;;
        lint)
            run_lint
            ;;
        format)
            format_code
            ;;
        backup)
            backup_db
            ;;
        restore)
            restore_db "$2"
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