@echo off
REM BookMyShow Clone - Quick Start Script for Windows

echo.
echo ================================================
echo   BookMyShow Clone - Local Development Setup
echo ================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)
echo [OK] Docker is running
echo.

REM Step 1: Start infrastructure
echo Step 1/4: Starting infrastructure (databases, Redis, Kafka)...
docker-compose up -d user-db catalog-db booking-db payment-db notification-db redis zookeeper kafka

echo Waiting 30 seconds for databases and Kafka to initialize...
timeout /t 30 /nobreak >nul
echo.

REM Step 2: Start backend services
echo Step 2/4: Starting backend services...
docker-compose up -d user-service catalog-service booking-service payment-service notification-service

echo Waiting 60 seconds for services to start...
timeout /t 60 /nobreak >nul
echo.

REM Step 3: Start Gateway Service
echo Step 3/4: Starting Gateway Service...
docker-compose up -d gateway-service

echo Waiting 30 seconds for Gateway Service to start...
timeout /t 30 /nobreak >nul
echo.

REM Step 4: Start frontend
echo Step 4/4: Starting frontend...
docker-compose up -d frontend

echo Waiting 30 seconds for frontend to start...
timeout /t 30 /nobreak >nul
echo.

REM Show status
echo ================================================
echo BookMyShow Clone is starting up!
echo ================================================
echo.
echo Service URLs:
echo   Frontend:           http://localhost:3000
echo   Gateway Service:    http://localhost:8080
echo   API Docs:           http://localhost:8080/docs
echo.
echo   User Service:       http://localhost:8081 (docs: /docs)
echo   Catalog Service:    http://localhost:8082 (docs: /docs)
echo   Booking Service:    http://localhost:8083 (docs: /docs)
echo   Payment Service:    http://localhost:8084 (docs: /docs)
echo   Notification:       http://localhost:8085 (docs: /docs)
echo.
echo Databases:
echo   User DB:            localhost:5432
echo   Catalog DB:         localhost:5433
echo   Booking DB:         localhost:5434
echo   Payment DB:         localhost:5435
echo   Notification DB:    localhost:5436
echo.
echo Useful Commands:
echo   View logs:          docker-compose logs -f
echo   View status:        docker-compose ps
echo   Stop all:           docker-compose down
echo   Stop ^& clean:       docker-compose down -v
echo.
echo Note: Services may take 1-2 more minutes to be fully ready.
echo       Check logs with: docker-compose logs -f
echo.
echo For more details, see LOCAL_SETUP.md
echo.
pause
