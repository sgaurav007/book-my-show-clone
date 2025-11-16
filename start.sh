#!/bin/bash

# BookMyShow Clone - Quick Start Script
# This script starts all services in the correct order

set -e

echo "🎬 Starting BookMyShow Clone..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is running${NC}"
}

# Function to check if ports are available
check_ports() {
    echo ""
    echo -e "${BLUE}Checking if required ports are available...${NC}"

    PORTS=(3000 8080 8081 8082 8083 8084 8085 5432 5433 5434 5435 5436 6379 9092 2181)
    OCCUPIED_PORTS=()

    for port in "${PORTS[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$port "; then
            OCCUPIED_PORTS+=($port)
        fi
    done

    if [ ${#OCCUPIED_PORTS[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠ Warning: The following ports are already in use: ${OCCUPIED_PORTS[*]}${NC}"
        echo "You may need to stop other services or modify docker-compose.yml"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✓ All required ports are available${NC}"
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    echo -ne "${YELLOW}Waiting for $service_name to be ready...${NC}"

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo -e " ${YELLOW}⚠ Timeout waiting for $service_name${NC}"
    return 1
}

# Main execution
echo ""
echo "================================================"
echo "  BookMyShow Clone - Local Development Setup"
echo "================================================"
echo ""

# Step 1: Check Docker
check_docker

# Step 2: Check ports
check_ports

# Step 3: Start infrastructure
echo ""
echo -e "${BLUE}Step 1/4: Starting infrastructure (databases, Redis, Kafka)...${NC}"
docker-compose up -d user-db catalog-db booking-db payment-db notification-db redis zookeeper kafka

echo -e "${YELLOW}Waiting 30 seconds for databases and Kafka to initialize...${NC}"
sleep 30

# Step 4: Start backend services
echo ""
echo -e "${BLUE}Step 2/4: Starting backend services...${NC}"
docker-compose up -d user-service catalog-service booking-service payment-service notification-service

echo -e "${YELLOW}Waiting 60 seconds for services to start...${NC}"
sleep 60

# Step 5: Start Gateway Service
echo ""
echo -e "${BLUE}Step 3/4: Starting Gateway Service...${NC}"
docker-compose up -d gateway-service

echo -e "${YELLOW}Waiting 30 seconds for Gateway Service to start...${NC}"
sleep 30

# Step 6: Start frontend
echo ""
echo -e "${BLUE}Step 4/4: Starting frontend...${NC}"
docker-compose up -d frontend

echo -e "${YELLOW}Waiting 30 seconds for frontend to start...${NC}"
sleep 30

# Step 7: Verify services
echo ""
echo -e "${BLUE}Verifying services...${NC}"
echo ""

wait_for_service "Gateway Service" "http://localhost:8080/health" || true
wait_for_service "User Service" "http://localhost:8081/health" || true
wait_for_service "Catalog Service" "http://localhost:8082/health" || true
wait_for_service "Booking Service" "http://localhost:8083/health" || true
wait_for_service "Payment Service" "http://localhost:8084/health" || true
wait_for_service "Notification Service" "http://localhost:8085/health" || true

# Step 8: Show status
echo ""
echo "================================================"
echo -e "${GREEN}🎉 BookMyShow Clone is starting up!${NC}"
echo "================================================"
echo ""
echo "📊 Service URLs:"
echo "  Frontend:           http://localhost:3000"
echo "  Gateway Service:    http://localhost:8080"
echo "  API Docs:           http://localhost:8080/docs"
echo ""
echo "  User Service:       http://localhost:8081 (docs: /docs)"
echo "  Catalog Service:    http://localhost:8082 (docs: /docs)"
echo "  Booking Service:    http://localhost:8083 (docs: /docs)"
echo "  Payment Service:    http://localhost:8084 (docs: /docs)"
echo "  Notification:       http://localhost:8085 (docs: /docs)"
echo ""
echo "🗄️  Databases:"
echo "  User DB:            localhost:5432"
echo "  Catalog DB:         localhost:5433"
echo "  Booking DB:         localhost:5434"
echo "  Payment DB:         localhost:5435"
echo "  Notification DB:    localhost:5436"
echo ""
echo "📝 Useful Commands:"
echo "  View logs:          docker-compose logs -f"
echo "  View status:        docker-compose ps"
echo "  Stop all:           docker-compose down"
echo "  Stop & clean:       docker-compose down -v"
echo ""
echo "⏳ Note: Services may take 1-2 more minutes to be fully ready."
echo "   Check logs with: docker-compose logs -f"
echo ""
echo "📖 For more details, see LOCAL_SETUP.md"
echo ""
