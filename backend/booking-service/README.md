# Booking Service

## Overview
The Booking Service is a critical microservice in the BookMyShow clone that handles seat reservations, Redis-based distributed locking, and booking management with Kafka event publishing.

## Technology Stack
- **Java 17**
- **Spring Boot 3.2.0**
- **PostgreSQL** (Port 5434)
- **Redis** (Distributed seat locking with Lua scripts)
- **Apache Kafka** (Event streaming)
- **Flyway** (Database migrations)
- **JUnit 5 + Mockito** (Unit testing)
- **TestContainers** (Integration testing)
- **JaCoCo** (Code coverage >80%)

## Features

### Core Functionality
1. **Seat Locking with Redis**
   - Atomic lock acquisition using Lua scripts
   - 15-minute lock expiry
   - Lock key format: `seat:lock:{showId}:{seatId}`
   - Prevents double booking with distributed locks

2. **Booking Management**
   - Lock seats for temporary reservation
   - Confirm booking after payment
   - Cancel booking and release locks
   - Get booking details
   - Get user's booking history

3. **Event Publishing (Kafka)**
   - `BookingCreatedEvent` - When seats are locked
   - `BookingConfirmedEvent` - When payment is successful
   - `BookingCancelledEvent` - When booking is cancelled

## API Endpoints

### POST `/api/bookings/lock-seats`
Lock seats for a show temporarily (15 minutes).

**Request:**
```json
{
  "userId": 100,
  "showId": 200,
  "seats": [
    {
      "seatId": 1,
      "seatNumber": "A1",
      "price": 250.00
    },
    {
      "seatId": 2,
      "seatNumber": "A2",
      "price": 250.00
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Seats locked successfully",
  "data": {
    "id": 1,
    "bookingReference": "BK123456789ABC",
    "userId": 100,
    "showId": 200,
    "totalAmount": 500.00,
    "bookingStatus": "PENDING",
    "expiresAt": "2025-11-16T08:15:00",
    "seats": [...]
  }
}
```

### POST `/api/bookings/{id}/confirm`
Confirm a booking after successful payment.

**Request:**
```json
{
  "paymentId": 999
}
```

**Response:**
```json
{
  "success": true,
  "message": "Booking confirmed successfully",
  "data": {
    "bookingStatus": "CONFIRMED",
    "paymentId": 999,
    ...
  }
}
```

### GET `/api/bookings/{id}`
Get booking details by ID.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "bookingReference": "BK123456789ABC",
    "bookingStatus": "CONFIRMED",
    ...
  }
}
```

### DELETE `/api/bookings/{id}`
Cancel a pending booking and release seat locks.

**Response:**
```json
{
  "success": true,
  "message": "Booking cancelled successfully"
}
```

### GET `/api/bookings/user/{userId}`
Get all bookings for a user.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "bookingReference": "BK123456789ABC",
      ...
    }
  ]
}
```

## Database Schema

### bookings
```sql
- id (PK)
- booking_reference (UNIQUE)
- user_id
- show_id
- total_amount
- booking_status (PENDING, CONFIRMED, CANCELLED, EXPIRED)
- payment_id
- expires_at
- created_at
- updated_at
```

### booking_seats
```sql
- id (PK)
- booking_id (FK)
- seat_id
- seat_number
- price
- created_at
- updated_at
```

## Redis Seat Locking

### Lua Script for Atomic Lock Acquisition
```lua
-- Check if any seat is already locked
for i, key in ipairs(KEYS) do
  if redis.call('EXISTS', key) == 1 then
    return 0  -- Lock failed
  end
end

-- Lock all seats atomically
for i, key in ipairs(KEYS) do
  redis.call('SETEX', key, ARGV[1], ARGV[2])  -- TTL: 15 min, Value: userId
end

return 1  -- Lock success
```

### Lock Key Format
```
seat:lock:{showId}:{seatId}
```

Example: `seat:lock:200:1` (Show 200, Seat 1)

## Kafka Topics

1. **booking-created** (3 partitions)
   - Published when seats are locked
   - Consumed by Notification Service

2. **booking-confirmed** (3 partitions)
   - Published when payment is successful
   - Consumed by Notification Service

3. **booking-cancelled** (3 partitions)
   - Published when booking is cancelled
   - Consumed by Notification Service

## Configuration

### application.yml
```yaml
server:
  port: 8082

spring:
  datasource:
    url: jdbc:postgresql://localhost:5434/booking_db
    username: postgres
    password: postgres

  data:
    redis:
      host: localhost
      port: 6379

  kafka:
    bootstrap-servers: localhost:9092
```

## Testing Strategy (TDD)

### Unit Tests (60%)
- `BookingTest.java` - Entity validation
- `BookingSeatTest.java` - Entity relationships
- `SeatLockServiceTest.java` - Redis lock logic with mocks
- `BookingServiceTest.java` - Business logic
- `BookingEventPublisherTest.java` - Kafka producer
- `BookingControllerTest.java` - API endpoints

### Integration Tests (30%)
- `BookingServiceIntegrationTest.java`
  - Uses TestContainers for PostgreSQL and Redis
  - Tests end-to-end flows
  - Validates Redis distributed locking
  - Ensures data persistence

### Coverage Target
- Minimum 80% line coverage (enforced by JaCoCo)

## Running Tests

```bash
# Install shared module first
cd /home/user/book-my-show-clone/shared/common
mvn clean install

# Run all tests with coverage
cd /home/user/book-my-show-clone/backend/booking-service
mvn clean test

# Generate coverage report
mvn jacoco:report

# View report at: target/site/jacoco/index.html
```

## Building the Service

```bash
# Build JAR
mvn clean package

# Build Docker image
docker build -t booking-service:1.0.0 .

# Run with Docker Compose
docker-compose up booking-service
```

## Dependencies

- **Shared Common Module** (`com.bookmyshow:common:1.0.0`)
  - BaseEntity for auditing
  - ApiResponse for standardized responses
  - GlobalExceptionHandler
  - ResourceNotFoundException

## Key Design Patterns

1. **Repository Pattern** - Data access abstraction
2. **Service Layer Pattern** - Business logic separation
3. **DTO Pattern** - Data transfer between layers
4. **Event-Driven Architecture** - Kafka for async communication
5. **Distributed Locking** - Redis Lua scripts for atomicity

## Error Handling

- `ResourceNotFoundException` - 404 Not Found
- `ValidationException` - 400 Bad Request
- `RuntimeException` - 400 Bad Request (seat already locked, invalid state transitions)
- `Exception` - 500 Internal Server Error

## Logging

- INFO level for business operations
- ERROR level for exceptions
- Structured logging with user/booking context

## Health Checks

- `/actuator/health` - Service health status
- Database connectivity
- Redis connectivity
- Kafka connectivity

## Future Enhancements

1. Add booking expiry scheduler (mark expired bookings as EXPIRED)
2. Implement booking refund flow
3. Add metrics and monitoring (Prometheus/Grafana)
4. Implement circuit breaker for external dependencies
5. Add rate limiting per user
6. Implement idempotency for lock-seats endpoint

## Author
Agent 3 - TDD-driven development with complete test coverage
