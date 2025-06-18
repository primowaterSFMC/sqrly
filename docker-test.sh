#!/bin/bash

# Sqrly ADHD Planner Docker Test Script
# This script tests the Docker deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Test function
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    print_info "Testing: $description"
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null); then
        if [ "$response" = "$expected_status" ]; then
            print_success "$description - Status: $response"
            return 0
        else
            print_error "$description - Expected: $expected_status, Got: $response"
            return 1
        fi
    else
        print_error "$description - Failed to connect"
        return 1
    fi
}

# Main test function
run_tests() {
    local base_url="http://localhost:8000"
    local failed_tests=0
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  Sqrly ADHD Planner Docker Tests${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    print_info "Waiting for services to be ready..."
    sleep 5
    
    # Test health endpoint
    if test_endpoint "$base_url/health" "200" "Health Check"; then
        :
    else
        ((failed_tests++))
    fi
    
    # Test root endpoint
    if test_endpoint "$base_url/" "200" "Root Endpoint"; then
        :
    else
        ((failed_tests++))
    fi
    
    # Test API docs
    if test_endpoint "$base_url/api/docs" "200" "API Documentation"; then
        :
    else
        ((failed_tests++))
    fi
    
    # Test OpenAPI spec
    if test_endpoint "$base_url/api/openapi.json" "200" "OpenAPI Specification"; then
        :
    else
        ((failed_tests++))
    fi
    
    # Test database connectivity (through health endpoint)
    print_info "Testing database connectivity..."
    if health_response=$(curl -s "$base_url/health" 2>/dev/null); then
        if echo "$health_response" | grep -q "healthy"; then
            print_success "Database connectivity - OK"
        else
            print_error "Database connectivity - Failed"
            ((failed_tests++))
        fi
    else
        print_error "Database connectivity - Cannot reach health endpoint"
        ((failed_tests++))
    fi
    
    # Check Docker services
    print_info "Checking Docker services..."
    if docker-compose ps | grep -q "Up"; then
        print_success "Docker services are running"
    else
        print_error "Some Docker services are not running"
        ((failed_tests++))
    fi
    
    # Summary
    echo ""
    echo -e "${BLUE}========================================${NC}"
    if [ $failed_tests -eq 0 ]; then
        print_success "All tests passed! 🎉"
        echo -e "${GREEN}Your Sqrly ADHD Planner is ready to use!${NC}"
        echo ""
        print_info "Access your application:"
        echo "  🌐 API: $base_url"
        echo "  📖 API Docs: $base_url/api/docs"
        echo "  ❤️  Health Check: $base_url/health"
    else
        print_error "$failed_tests test(s) failed"
        echo ""
        print_info "Troubleshooting:"
        echo "  📋 Check logs: docker-compose logs -f"
        echo "  🔍 Check status: docker-compose ps"
        echo "  🔧 Check environment: cat .env"
        exit 1
    fi
    echo -e "${BLUE}========================================${NC}"
}

# Check if services are running
check_services() {
    if ! docker-compose ps | grep -q "sqrly"; then
        print_error "Sqrly services are not running"
        print_info "Start services with: docker-compose up -d"
        exit 1
    fi
}

# Main execution
main() {
    case "${1:-test}" in
        "test")
            check_services
            run_tests
            ;;
        "quick")
            check_services
            test_endpoint "http://localhost:8000/health" "200" "Quick Health Check"
            ;;
        *)
            echo "Usage: $0 [test|quick]"
            echo "  test  - Run all tests (default)"
            echo "  quick - Quick health check only"
            exit 1
            ;;
    esac
}

main "$@"
