#!/bin/bash

# BookMyShow Clone - Stop Script

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "================================================"
echo "  Stopping BookMyShow Clone"
echo "================================================"
echo ""

# Ask user if they want to remove volumes
echo -e "${BLUE}Do you want to remove data volumes (databases will be wiped)?${NC}"
read -p "Remove volumes? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Stopping all services and removing volumes...${NC}"
    docker-compose down -v
    echo -e "${GREEN}✓ All services stopped and data removed${NC}"
else
    echo -e "${BLUE}Stopping all services (keeping data)...${NC}"
    docker-compose down
    echo -e "${GREEN}✓ All services stopped (data preserved)${NC}"
fi

echo ""
echo "To start again, run: ./start.sh"
echo ""
