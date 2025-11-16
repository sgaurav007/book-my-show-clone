# Notification Service

## Overview
The Notification Service is a Kafka consumer-based microservice that handles all notification-related functionality for the BookMyShow application. It consumes events from Kafka topics and sends notifications via Email and SMS.

## Features
- Kafka event consumption for booking and payment events
- Email notification service (mock implementation with logging)
- SMS notification service (mock implementation with logging)
- Notification history tracking in PostgreSQL database
- Built following strict TDD principles

## Technology Stack
- **Framework**: Spring Boot 3.2.0
- **Language**: Java 17
- **Database**: PostgreSQL (port 5436)
- **Message Broker**: Apache Kafka
- **Migration**: Flyway
- **Testing**: JUnit 5, Mockito, Spring Kafka Test, Embedded Kafka, Testcontainers
- **Code Coverage**: JaCoCo (target: >80%)

## Architecture

### Package Structure
```
notification-service/
├── src/main/java/com/bookmyshow/notification/
│   ├── entity/
│   │   └── Notification.java
│   ├── repository/
│   │   └── NotificationRepository.java
│   ├── service/
│   │   ├── NotificationService.java
│   │   ├── EmailService.java
│   │   └── SmsService.java
│   ├── kafka/
│   │   ├── BookingNotificationConsumer.java
│   │   └── PaymentNotificationConsumer.java
│   ├── dto/
│   │   ├── BookingConfirmedEvent.java
│   │   ├── BookingCancelledEvent.java
│   │   ├── PaymentSuccessEvent.java
│   │   └── PaymentFailedEvent.java
│   ├── config/
│   │   └── KafkaConsumerConfig.java
│   └── NotificationServiceApplication.java
└── src/test/java/com/bookmyshow/notification/
    ├── entity/
    │   └── NotificationTest.java
    ├── repository/
    │   └── NotificationRepositoryTest.java
    ├── service/
    │   ├── NotificationServiceTest.java
    │   ├── EmailServiceTest.java
    │   └── SmsServiceTest.java
    ├── kafka/
    │   ├── BookingNotificationConsumer Test.java
    │   └── PaymentNotificationConsumerTest.java
    └── integration/
        └── NotificationServiceIntegrationTest.java
```

## Kafka Topics Consumed

| Topic | Event Type | Action |
|-------|-----------|--------|
| `booking.confirmed` | BookingConfirmedEvent | Send booking confirmation email & SMS |
| `booking.cancelled` | BookingCancelledEvent | Send cancellation email & SMS |
| `payment.success` | PaymentSuccessEvent | Send payment receipt email & SMS |
| `payment.failed` | PaymentFailedEvent | Send payment failure notice email & SMS |

## Database Schema

### Notifications Table
```sql
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    recipient VARCHAR(255),
    subject VARCHAR(500),
    content TEXT,
    status VARCHAR(20) NOT NULL,
    metadata TEXT,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_notifications_user_id`
- `idx_notifications_notification_type`
- `idx_notifications_status`
- `idx_notifications_created_at`
- `idx_notifications_user_type`
- `idx_notifications_user_status`

## API Endpoints

The service runs on port 8084 with context path `/api/notifications`.

### Actuator Endpoints
- `GET /api/notifications/actuator/health` - Health check
- `GET /api/notifications/actuator/info` - Service information
- `GET /api/notifications/actuator/metrics` - Service metrics
- `GET /api/notifications/actuator/prometheus` - Prometheus metrics

## Configuration

### Application Properties (application.yml)
- **Server Port**: 8084
- **Database**: PostgreSQL on localhost:5436
- **Kafka Bootstrap Servers**: localhost:9092
- **Consumer Group ID**: notification-service

### Environment Variables
- `SPRING_DATASOURCE_URL`: PostgreSQL connection URL
- `SPRING_DATASOURCE_USERNAME`: Database username
- `SPRING_DATASOURCE_PASSWORD`: Database password
- `SPRING_KAFKA_BOOTSTRAP_SERVERS`: Kafka server addresses

## Running the Service

### Prerequisites
1. PostgreSQL running on port 5436
2. Apache Kafka running on port 9092
3. Shared common module built and installed (`mvn install`)

### Build
```bash
cd backend/notification-service
mvn clean install
```

### Run
```bash
mvn spring-boot:run
```

### Docker
```bash
docker build -t notification-service:1.0.0 .
docker run -p 8084:8084 notification-service:1.0.0
```

## Testing

### Unit Tests
```bash
mvn test
```

### Integration Tests
```bash
mvn verify
```

### Test Coverage
```bash
mvn clean test jacoco:report
```
Coverage report available at: `target/site/jacoco/index.html`

## Test Summary

### Unit Tests
- **NotificationTest**: Entity tests (7 tests)
- **NotificationRepositoryTest**: Repository layer tests (9 tests)
- **NotificationServiceTest**: Service layer tests (9 tests)
- **EmailServiceTest**: Email service tests (10 tests)
- **SmsServiceTest**: SMS service tests (10 tests)
- **BookingNotificationConsumerTest**: Booking consumer tests (6 tests)
- **PaymentNotificationConsumerTest**: Payment consumer tests (6 tests)

### Integration Tests
- **NotificationServiceIntegrationTest**: End-to-end Kafka integration tests (4 tests)

**Total Tests**: 61 tests
**Expected Coverage**: >80%

## TDD Approach

This service was built following strict Test-Driven Development:

1. **RED**: Write failing test
2. **GREEN**: Write minimal code to pass
3. **REFACTOR**: Improve code while keeping tests green

All implementation was done after writing comprehensive tests first.

## Mock Implementations

### Email Service
- Logs email content to console
- Simulates email sending
- Records notification in database

### SMS Service
- Logs SMS content to console
- Truncates messages to 160 characters
- Masks phone numbers in logs
- Records notification in database

## Error Handling

- Individual notification failures don't stop other notifications
- Failed notifications are recorded with status "FAILED"
- Error messages are stored for debugging
- Kafka consumers continue processing even if individual messages fail

## Monitoring & Observability

- Spring Boot Actuator health checks
- Prometheus metrics export
- Structured logging for all operations
- Notification status tracking

## Dependencies

### Core Dependencies
- Spring Boot Starter Web
- Spring Boot Starter Data JPA
- Spring Kafka
- PostgreSQL Driver
- Flyway
- Lombok
- Jackson

### Test Dependencies
- Spring Boot Starter Test
- Spring Kafka Test
- Testcontainers (PostgreSQL, Kafka)
- Awaitility
- H2 Database (for tests)

## Shared Module Usage

This service uses the shared/common module for:
- `BaseEntity`: Base entity with audit fields
- `ApiResponse`: Standard API response wrapper
- `ErrorResponse`: Standard error response
- Exception handling classes
- Utility classes

## Future Enhancements

- Real email integration (SendGrid, AWS SES)
- Real SMS integration (Twilio, AWS SNS)
- Push notification support
- Notification templates
- Retry mechanism for failed notifications
- Notification preferences per user
- Webhook support for third-party integrations

## License

Copyright © 2024 BookMyShow Clone Project
