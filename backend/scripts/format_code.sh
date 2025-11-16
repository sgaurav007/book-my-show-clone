#!/bin/bash

# Format code for all BookMyShow Python/FastAPI services

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

SERVICES=("user-service" "catalog-service" "booking-service" "payment-service" "notification-service" "gateway-service")

echo "========================================"
echo "  BookMyShow - Code Formatting"
echo "========================================"
echo ""

# Function to format a service
format_service() {
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

    echo -e "${BLUE}Formatting $service...${NC}"
    cd "$service_dir"

    # Check if app directory exists
    if [ ! -d "app" ]; then
        echo -e "${YELLOW}⚠ No app directory found in $service${NC}"
        return 1
    fi

    # Format with Black
    echo "  Running Black..."
    poetry run black app/ tests/ 2>/dev/null || poetry run black app/

    # Lint and fix with Ruff
    echo "  Running Ruff..."
    poetry run ruff check app/ tests/ --fix 2>/dev/null || poetry run ruff check app/ --fix || true

    # Sort imports
    echo "  Sorting imports..."
    poetry run isort app/ tests/ 2>/dev/null || poetry run isort app/ 2>/dev/null || true

    echo -e "${GREEN}✓ $service formatted${NC}"
    echo ""
}

# Format shared common module first
if [ -d "$BACKEND_DIR/shared/common" ]; then
    echo -e "${BLUE}Formatting shared/common...${NC}"
    cd "$BACKEND_DIR/shared/common"
    if [ -f "pyproject.toml" ] && [ -d "bookmyshow_common" ]; then
        poetry run black bookmyshow_common/ 2>/dev/null || true
        poetry run ruff check bookmyshow_common/ --fix 2>/dev/null || true
        poetry run isort bookmyshow_common/ 2>/dev/null || true
        echo -e "${GREEN}✓ shared/common formatted${NC}"
    fi
    echo ""
fi

# Format all services
for service in "${SERVICES[@]}"; do
    format_service "$service" || true
done

echo "========================================"
echo -e "${GREEN}Code formatting complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run tests: ./backend/scripts/run_tests.sh"
echo "  3. Commit changes: git add . && git commit -m 'Format code'"
echo ""
