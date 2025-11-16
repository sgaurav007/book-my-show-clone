# Payment Service

Payment Service for BookMyShow Clone - handles payment processing, refunds, and payment gateway integration.

## Features

- Payment initiation and processing
- Mock payment gateway (90% success rate)
- Refund processing (full and partial)
- Payment audit logging
- Kafka event publishing
- Idempotent webhook handling

## Tech Stack

- Java 17
- Spring Boot 3.2.0
- PostgreSQL (port 5435)
- Kafka
- Flyway for database migrations
- JaCoCo for code coverage

## API Endpoints

### Payment Endpoints

- `POST /api/payments/initiate` - Initiate a new payment
- `GET /api/payments/{id}` - Get payment by ID
- `GET /api/payments/booking/{bookingId}` - Get payment by booking ID
- `POST /api/payments/webhook` - Handle payment gateway webhook
- `POST /api/payments/refund` - Process refund
- `GET /api/payments/{paymentId}/refunds` - Get refunds for a payment

## Database Schema

### Payments Table
```sql
- id (BIGSERIAL)
- payment_reference (VARCHAR UNIQUE)
- booking_id (BIGINT UNIQUE)
- user_id (BIGINT)
- amount (DECIMAL)
- currency (VARCHAR)
- payment_method (VARCHAR)
- payment_status (VARCHAR)
- gateway_transaction_id (VARCHAR)
- gateway_name (VARCHAR)
- failure_reason (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Refunds Table
```sql
- id (BIGSERIAL)
- payment_id (BIGINT)
- refund_amount (DECIMAL)
- refund_status (VARCHAR)
- refund_reference (VARCHAR UNIQUE)
- gateway_refund_id (VARCHAR)
- reason (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Payment Audit Log Table
```sql
- id (BIGSERIAL)
- payment_id (BIGINT)
- event_type (VARCHAR)
- event_data (JSONB)
- created_at (TIMESTAMP)
```

## Kafka Topics

- `payment.initiated` - Published when payment is initiated
- `payment.success` - Published when payment succeeds
- `payment.failed` - Published when payment fails
- `payment.refunded` - Published when refund is processed

## Mock Payment Gateway

The service includes a mock payment gateway that simulates real payment processing:

- **Success Rate**: 90% (configurable via `payment.gateway.mock.success-rate`)
- **Processing Time**: 1000ms (configurable via `payment.gateway.mock.processing-time-ms`)
- **Transaction ID Generation**: Unique UUIDs for each transaction
- **Refund Support**: Always successful for testing

## Configuration

### application.yml
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5435/payment_db
    username: postgres
    password: postgres

  kafka:
    bootstrap-servers: localhost:9092

server:
  port: 8084

payment:
  gateway:
    mock:
      success-rate: 0.9
      processing-time-ms: 1000
```

## Running the Service

### Prerequisites
- Java 17
- PostgreSQL running on port 5435
- Kafka running on port 9092

### Using Maven
```bash
mvn spring-boot:run
```

### Using Docker
```bash
docker build -t payment-service .
docker run -p 8084:8084 payment-service
```

## Testing

### Run all tests
```bash
mvn test
```

### Run with coverage
```bash
mvn clean test jacoco:report
```

Coverage report will be available at `target/site/jacoco/index.html`

## Test Coverage

The service follows strict TDD approach with >80% code coverage:

- Unit Tests: PaymentServiceTest, RefundServiceTest, MockPaymentGatewayAdapterTest
- Controller Tests: PaymentControllerTest, WebhookControllerTest
- Integration Tests: PaymentIntegrationTest

## Payment Flow

1. **Initiate Payment**
   - Client calls `/api/payments/initiate`
   - Service creates payment record with status INITIATED
   - Service calls mock gateway to get transaction ID
   - Publishes `payment.initiated` event
   - Returns payment reference and URL

2. **Process Payment (via Webhook)**
   - Gateway calls `/api/payments/webhook` with result
   - If SUCCESS: Update status, publish `payment.success` event
   - If FAILED: Update status with reason, publish `payment.failed` event

3. **Refund**
   - Client calls `/api/payments/refund`
   - Service validates payment is successful
   - Calculates remaining refundable amount
   - Processes refund through gateway
   - Updates payment status to REFUNDED if fully refunded
   - Publishes `payment.refunded` event

## Idempotency

- Payment confirmation is idempotent - multiple webhook calls with same reference won't create duplicate confirmations
- Each booking can only have one payment
- Refund amount validation prevents over-refunding

## Error Handling

- `PaymentNotFoundException` - 404 when payment not found
- `PaymentAlreadyProcessedException` - 409 when duplicate payment attempted
- `InvalidPaymentStateException` - 400 when operation not allowed in current state
- `InsufficientRefundAmountException` - 400 when refund exceeds available amount

## Audit Logging

All payment events are logged to `payment_audit_log` table with JSONB event data for compliance and debugging.
