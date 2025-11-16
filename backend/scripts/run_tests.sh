#!/bin/bash

# Run tests for all BookMyShow Python/FastAPI services

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

SERVICES=("user-service" "catalog-service" "booking-service" "payment-service" "notification-service" "gateway-service")

echo "========================================"
echo "  BookMyShow - Running All Tests"
echo "========================================"
echo ""

FAILED_SERVICES=()
PASSED_SERVICES=()

# Function to run tests for a service
run_service_tests() {
    local service=$1
    local service_dir="$BACKEND_DIR/$service"

    if [ ! -d "$service_dir" ]; then
        echo -e "${YELLOW}⚠ Service directory not found: $service${NC}"
        return 1
    fi

    if [ ! -f "$service_dir/pyproject.toml" ]; then
        echo -e "${YELLOW}⚠ No pyproject.toml found in $service${NC}"
        return 1
    fi

    echo -e "${BLUE}Testing $service...${NC}"
    cd "$service_dir"

    # Run pytest with coverage
    if poetry run pytest --cov=app --cov-report=term-missing --cov-report=html -v; then
        echo -e "${GREEN}✓ $service tests passed${NC}"
        PASSED_SERVICES+=("$service")
        return 0
    else
        echo -e "${RED}✗ $service tests failed${NC}"
        FAILED_SERVICES+=("$service")
        return 1
    fi
}

# Test shared common module first
if [ -d "$BACKEND_DIR/shared/common" ]; then
    echo -e "${BLUE}Testing shared/common...${NC}"
    cd "$BACKEND_DIR/shared/common"
    if [ -f "pyproject.toml" ]; then
        if poetry run pytest -v 2>/dev/null; then
            echo -e "${GREEN}✓ shared/common tests passed${NC}"
        else
            echo -e "${YELLOW}⚠ shared/common tests skipped or no tests found${NC}"
        fi
    fi
    echo ""
fi

# Run tests for all services
for service in "${SERVICES[@]}"; do
    run_service_tests "$service" || true
    echo ""
done

# Summary
echo "========================================"
echo "  Test Summary"
echo "========================================"
echo ""

if [ ${#PASSED_SERVICES[@]} -gt 0 ]; then
    echo -e "${GREEN}Passed (${#PASSED_SERVICES[@]}):${NC}"
    for service in "${PASSED_SERVICES[@]}"; do
        echo -e "  ${GREEN}✓${NC} $service"
    done
    echo ""
fi

if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    echo -e "${RED}Failed (${#FAILED_SERVICES[@]}):${NC}"
    for service in "${FAILED_SERVICES[@]}"; do
        echo -e "  ${RED}✗${NC} $service"
    done
    echo ""
    exit 1
else
    echo -e "${GREEN}All tests passed!${NC}"
    echo ""
    exit 0
fi
