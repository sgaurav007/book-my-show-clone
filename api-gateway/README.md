# API Gateway - BookMyShow Clone

Spring Cloud Gateway implementation for the BookMyShow Clone microservices architecture.

## Features

- **Route Management**: Routes requests to appropriate microservices
- **JWT Authentication**: Validates JWT tokens on protected endpoints
- **CORS Configuration**: Configured for frontend (localhost:3000)
- **Rate Limiting**: 100 requests per minute per user (Redis-based)
- **Circuit Breaker**: Resilience4j for fault tolerance
- **Request/Response Logging**: Comprehensive logging for monitoring
- **Health Checks**: Actuator endpoints for service health

## Routes

| Path | Service | Port |
|------|---------|------|
| /api/users/** | user-service | 8081 |
| /api/catalog/** | catalog-service | 8082 |
| /api/bookings/** | booking-service | 8083 |
| /api/payments/** | payment-service | 8084 |

## Public Endpoints (No Authentication Required)

- POST /api/users/register
- POST /api/users/login
- POST /api/users/refresh-token
- GET /api/catalog/movies/**
- GET /api/catalog/theaters/**
- GET /api/catalog/shows/**
- GET /actuator/health

## Protected Endpoints

All other endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt-token>
```

## Configuration

### Environment Variables

- `SPRING_REDIS_HOST`: Redis host (default: localhost)
- `SPRING_REDIS_PORT`: Redis port (default: 6379)
- `JWT_SECRET`: JWT secret key for token validation
- `USER_SERVICE_URL`: User service URL (default: http://localhost:8081)
- `CATALOG_SERVICE_URL`: Catalog service URL (default: http://localhost:8082)
- `BOOKING_SERVICE_URL`: Booking service URL (default: http://localhost:8083)
- `PAYMENT_SERVICE_URL`: Payment service URL (default: http://localhost:8084)

### Rate Limiting

Rate limiting is configured per user (based on X-User-Id header or IP address):
- Replenish rate: 100 tokens per minute
- Burst capacity: 100 tokens

### Circuit Breaker

Circuit breaker configuration:
- Sliding window size: 10 requests
- Failure rate threshold: 50%
- Wait duration in open state: 5 seconds
- Timeout: 5 seconds

## Building and Running

### Local Development

```bash
mvn clean install
mvn spring-boot:run
```

### Docker

```bash
docker build -t api-gateway:latest .
docker run -p 8080:8080 \
  -e SPRING_REDIS_HOST=redis \
  -e USER_SERVICE_URL=http://user-service:8081 \
  api-gateway:latest
```

### Using Docker Compose

```bash
docker-compose up api-gateway
```

## Testing

Run tests:

```bash
mvn test
```

## Health Check

Check service health:

```bash
curl http://localhost:8080/actuator/health
```

## Monitoring

Actuator endpoints:
- Health: http://localhost:8080/actuator/health
- Info: http://localhost:8080/actuator/info
- Metrics: http://localhost:8080/actuator/metrics
- Prometheus: http://localhost:8080/actuator/prometheus

## CORS Configuration

CORS is configured to allow requests from:
- http://localhost:3000 (Frontend)
- http://localhost:3001

Allowed methods: GET, POST, PUT, DELETE, PATCH, OPTIONS

## Security

- JWT tokens are validated using HMAC-SHA256 algorithm
- Tokens must contain: userId, username, role
- Expired tokens are automatically rejected
- User information is passed to downstream services via headers:
  - X-User-Id
  - X-Username
  - X-User-Role

## Error Handling

Circuit breaker fallback endpoints:
- /fallback/user-service
- /fallback/catalog-service
- /fallback/booking-service
- /fallback/payment-service

Returns 503 Service Unavailable when a service is down.
