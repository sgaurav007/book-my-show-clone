# 🚀 BookMyShow Clone - Local Setup Guide

This guide will help you run the complete BookMyShow application on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **Docker** (version 20.10+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (version 2.0+) - Usually bundled with Docker Desktop
- **Git** - For cloning the repository

### Optional (for development)
- **Java 17+** - For running services without Docker
- **Maven 3.8+** - For building backend services
- **Node.js 18+** - For frontend development
- **npm or pnpm** - For frontend dependencies

### System Requirements
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: At least 10GB free
- **Ports**: Ensure the following ports are available:
  - `3000` - Frontend
  - `8080` - API Gateway
  - `8081-8085` - Microservices
  - `5432-5436` - PostgreSQL databases
  - `6379` - Redis
  - `9092` - Kafka
  - `2181` - Zookeeper

## 🎯 Quick Start (Recommended)

### Option 1: Run Everything with Docker Compose

This is the easiest way to get started. Docker Compose will build and start all services.

```bash
# 1. Clone the repository (if not already done)
git clone <your-repo-url>
cd book-my-show-clone

# 2. Start all services (infrastructure + backend + frontend)
docker-compose up -d

# 3. Wait for all services to start (this may take 5-10 minutes on first run)
docker-compose ps

# 4. Check logs to ensure everything is running
docker-compose logs -f
```

### Option 2: Run in Stages (Better for debugging)

```bash
# Stage 1: Start infrastructure only (databases, Redis, Kafka)
docker-compose up -d user-db catalog-db booking-db payment-db notification-db redis zookeeper kafka

# Wait for databases to be ready (30 seconds)
sleep 30

# Stage 2: Start backend services
docker-compose up -d user-service catalog-service booking-service payment-service notification-service

# Wait for backend services to be ready (60 seconds)
sleep 60

# Stage 3: Start API Gateway
docker-compose up -d api-gateway

# Wait for API Gateway to be ready (30 seconds)
sleep 30

# Stage 4: Start frontend
docker-compose up -d frontend
```

## 🔍 Verify the Setup

### Check Running Containers

```bash
# View all running containers
docker-compose ps

# Expected output: All services should be "Up"
# - user-db, catalog-db, booking-db, payment-db, notification-db
# - redis
# - zookeeper, kafka
# - user-service, catalog-service, booking-service, payment-service, notification-service
# - api-gateway
# - frontend
```

### Check Service Health

```bash
# Check API Gateway health
curl http://localhost:8080/actuator/health

# Check User Service health
curl http://localhost:8081/actuator/health

# Check Catalog Service health
curl http://localhost:8082/actuator/health

# Check Booking Service health
curl http://localhost:8083/actuator/health

# Check Payment Service health
curl http://localhost:8084/actuator/health

# Check Notification Service health
curl http://localhost:8085/actuator/health
```

### Access the Application

Open your browser and navigate to:

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **API Gateway Swagger UI**: http://localhost:8080/swagger-ui.html

## 📊 Access Databases

You can connect to the PostgreSQL databases using any database client:

```
User Service Database:
- Host: localhost
- Port: 5432
- Database: user_service_db
- Username: postgres
- Password: postgres

Catalog Service Database:
- Host: localhost
- Port: 5433
- Database: catalog_service_db
- Username: postgres
- Password: postgres

Booking Service Database:
- Host: localhost
- Port: 5434
- Database: booking_service_db
- Username: postgres
- Password: postgres

Payment Service Database:
- Host: localhost
- Port: 5435
- Database: payment_service_db
- Username: postgres
- Password: postgres

Notification Service Database:
- Host: localhost
- Port: 5436
- Database: notification_service_db
- Username: postgres
- Password: postgres
```

### Redis

```bash
# Connect to Redis CLI
docker exec -it redis redis-cli

# Test Redis connection
redis-cli -h localhost -p 6379 ping
# Expected output: PONG
```

### Kafka

```bash
# List Kafka topics
docker exec -it kafka kafka-topics --list --bootstrap-server localhost:9092

# Expected topics:
# - booking.created
# - booking.confirmed
# - booking.cancelled
# - payment.initiated
# - payment.completed
# - payment.failed
```

## 🧪 Test the Application

### 1. Register a User

```bash
curl -X POST http://localhost:8080/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "firstName": "John",
    "lastName": "Doe",
    "phoneNumber": "+1234567890"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8080/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Save the JWT token from the response
```

### 3. Get Movies

```bash
curl http://localhost:8080/api/catalog/movies
```

### 4. Get Theaters

```bash
curl http://localhost:8080/api/catalog/theaters
```

### 5. Get Shows for a Movie

```bash
# Replace {movieId} with an actual movie ID from step 3
curl http://localhost:8080/api/catalog/shows/movie/{movieId}
```

### 6. Create a Booking

```bash
# Replace {showId} and seat IDs with actual values
# Replace {JWT_TOKEN} with the token from step 2
curl -X POST http://localhost:8080/api/bookings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -d '{
    "showId": 1,
    "seatIds": [1, 2, 3],
    "userId": 1
  }'
```

## 🛠️ Development Mode

### Running Backend Services Locally (without Docker)

If you want to develop and debug backend services locally:

```bash
# 1. Start only infrastructure with Docker
docker-compose up -d user-db catalog-db booking-db payment-db notification-db redis zookeeper kafka

# 2. Build the shared common module first
cd shared/common
mvn clean install

# 3. Build and run a specific service (e.g., User Service)
cd ../../backend/user-service
mvn clean install
mvn spring-boot:run

# The service will connect to Docker infrastructure (databases, Redis, Kafka)
```

### Running Frontend Locally (without Docker)

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Start the development server
npm run dev

# The frontend will be available at http://localhost:5173 (Vite default)
# and will connect to the API Gateway at http://localhost:8080
```

## 📊 Monitoring (Optional)

### Start Prometheus & Grafana

```bash
docker-compose --profile monitoring up -d
```

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (username: admin, password: admin)

### Start ELK Stack

```bash
docker-compose --profile elk up -d
```

- **Elasticsearch**: http://localhost:9200
- **Kibana**: http://localhost:5601

## 🔧 Troubleshooting

### Issue: Port Already in Use

```bash
# Find which process is using a port (e.g., 8080)
# On Linux/Mac:
lsof -i :8080

# On Windows:
netstat -ano | findstr :8080

# Kill the process or change the port in docker-compose.yml
```

### Issue: Services Not Starting

```bash
# View logs for a specific service
docker-compose logs -f user-service

# Restart a specific service
docker-compose restart user-service

# Rebuild and restart a service
docker-compose up -d --build user-service
```

### Issue: Database Connection Errors

```bash
# Check if databases are ready
docker-compose logs user-db catalog-db booking-db payment-db notification-db

# Restart databases
docker-compose restart user-db catalog-db booking-db payment-db notification-db

# Wait 30 seconds and restart services
docker-compose restart user-service catalog-service booking-service payment-service notification-service
```

### Issue: Out of Memory

```bash
# Increase Docker memory limit in Docker Desktop settings
# Recommended: 8GB minimum, 16GB for better performance

# Or run services in stages instead of all at once
```

### Issue: Kafka Not Ready

```bash
# Kafka takes time to start. Wait at least 60 seconds after starting
# Check Kafka logs
docker-compose logs -f kafka

# Restart Kafka if needed
docker-compose restart zookeeper kafka
```

### Issue: Frontend Can't Connect to Backend

```bash
# Check if API Gateway is running
curl http://localhost:8080/actuator/health

# Check frontend environment variables in docker-compose.yml
# VITE_API_URL should be http://localhost:8080

# Restart frontend
docker-compose restart frontend
```

## 🧹 Cleanup

### Stop All Services

```bash
# Stop all services but keep data
docker-compose down

# Stop and remove all data (databases, volumes)
docker-compose down -v
```

### Remove All Docker Images

```bash
# Remove all BookMyShow images
docker-compose down --rmi all -v
```

### Start Fresh

```bash
# Complete cleanup
docker-compose down -v --rmi all
docker system prune -a

# Start again
docker-compose up -d
```

## 📝 Default Credentials

### Application Users
After the catalog service starts, test data will be automatically loaded.

### Database Access
- **Username**: postgres
- **Password**: postgres

### Monitoring
- **Grafana**: admin / admin
- **Kibana**: No authentication required

## 🎯 Next Steps

After successfully running the application locally:

1. **Explore the API** - Use the Swagger UI at http://localhost:8080/swagger-ui.html
2. **Check Test Data** - The catalog service loads 5 movies and theaters automatically
3. **Run Tests** - See TESTING.md for running the test suites
4. **Make Changes** - Follow the development mode instructions above
5. **Deploy to Azure** - See deployment documentation for production setup

## 🆘 Need Help?

- Check service logs: `docker-compose logs -f <service-name>`
- View all logs: `docker-compose logs -f`
- Check container status: `docker-compose ps`
- Restart everything: `docker-compose restart`

## 📚 Additional Resources

- [HLD.md](./HLD.md) - High-Level Design documentation
- [LLD.md](./LLD.md) - Low-Level Design documentation
- [TESTING.md](./TESTING.md) - Testing strategy and plans
- [README.md](./README.md) - Project overview and architecture
