#!/bin/bash

# Sqrly ADHD Planner Docker Setup Script
# This script helps set up the Docker environment for the Sqrly application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Sqrly ADHD Planner Docker Setup${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed and running
check_docker() {
    print_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed and running"
}

# Setup environment file
setup_env() {
    print_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
            print_warning "Please edit .env file with your configuration before starting services"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p init-scripts
    
    # Create .gitkeep files to preserve directory structure
    touch logs/.gitkeep
    touch data/.gitkeep
    
    print_success "Directories created"
}

# Generate secure keys
generate_keys() {
    print_info "Generating secure keys..."
    
    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -hex 32)
        POSTGRES_PASSWORD=$(openssl rand -base64 16)
        REDIS_PASSWORD=$(openssl rand -base64 16)
        
        echo ""
        print_info "Generated secure keys (add these to your .env file):"
        echo "JWT_SECRET_KEY=$JWT_SECRET"
        echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
        echo "REDIS_PASSWORD=$REDIS_PASSWORD"
        echo ""
    else
        print_warning "OpenSSL not found. Please generate secure keys manually."
    fi
}

# Validate environment
validate_env() {
    print_info "Validating environment configuration..."
    
    if [ -f ".env" ]; then
        # Check for required variables
        if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=your-openai-api-key-here" .env; then
            print_warning "OPENAI_API_KEY not set in .env file"
        fi
        
        if ! grep -q "JWT_SECRET_KEY=" .env || grep -q "JWT_SECRET_KEY=your-super-secure-jwt-secret-key-here" .env; then
            print_warning "JWT_SECRET_KEY not set in .env file"
        fi
        
        if ! grep -q "POSTGRES_PASSWORD=" .env || grep -q "POSTGRES_PASSWORD=your-secure-postgres-password-here" .env; then
            print_warning "POSTGRES_PASSWORD not set in .env file"
        fi
        
        print_success "Environment file validated"
    else
        print_error ".env file not found"
        exit 1
    fi
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."
    
    if docker-compose build; then
        print_success "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Start services
start_services() {
    local mode=$1
    
    if [ "$mode" = "dev" ]; then
        print_info "Starting services in development mode..."
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    else
        print_info "Starting services in production mode..."
        docker-compose up -d
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Services started successfully"
        
        print_info "Waiting for services to be ready..."
        sleep 10
        
        # Check service health
        if docker-compose ps | grep -q "Up"; then
            print_success "Services are running"
            echo ""
            print_info "Access your application:"
            echo "  🌐 API: http://localhost:8000"
            echo "  📖 API Docs: http://localhost:8000/api/docs"
            echo "  ❤️  Health Check: http://localhost:8000/health"
            echo ""
            print_info "Useful commands:"
            echo "  📋 View logs: docker-compose logs -f"
            echo "  🔍 Check status: docker-compose ps"
            echo "  🛑 Stop services: docker-compose down"
        else
            print_warning "Some services may not be running properly. Check logs with: docker-compose logs"
        fi
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Main menu
show_menu() {
    echo ""
    print_info "What would you like to do?"
    echo "1) Full setup (recommended for first time)"
    echo "2) Setup environment only"
    echo "3) Build images only"
    echo "4) Start services (production)"
    echo "5) Start services (development)"
    echo "6) Generate secure keys"
    echo "7) Exit"
    echo ""
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1)
            setup_env
            create_directories
            generate_keys
            validate_env
            build_images
            start_services "prod"
            ;;
        2)
            setup_env
            create_directories
            validate_env
            ;;
        3)
            build_images
            ;;
        4)
            validate_env
            start_services "prod"
            ;;
        5)
            validate_env
            start_services "dev"
            ;;
        6)
            generate_keys
            ;;
        7)
            print_info "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            show_menu
            ;;
    esac
}

# Main execution
main() {
    print_header
    check_docker
    
    # If arguments provided, run non-interactively
    if [ $# -gt 0 ]; then
        case $1 in
            "setup")
                setup_env
                create_directories
                generate_keys
                validate_env
                build_images
                start_services "prod"
                ;;
            "dev")
                validate_env
                start_services "dev"
                ;;
            "build")
                build_images
                ;;
            *)
                print_error "Unknown command: $1"
                print_info "Usage: $0 [setup|dev|build]"
                exit 1
                ;;
        esac
    else
        show_menu
    fi
}

# Run main function
main "$@"
