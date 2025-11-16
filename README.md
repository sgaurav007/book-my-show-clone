# BookMyShow Clone - Microservices Architecture

A production-ready, scalable ticket booking system built with Spring Boot microservices, designed to handle millions of concurrent users.

## Architecture Overview

This project implements a complete microservices architecture with:
- 5 independent microservices (User, Catalog, Booking, Payment, Notification)
- API Gateway for routing and authentication
- Separate PostgreSQL database for each service
- Redis for distributed locking and caching
- Apache Kafka for event-driven communication
- Complete observability stack (Prometheus, Grafana, ELK)

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Spring Boot 3.x | Microservices framework |
| API Gateway | Spring Cloud Gateway | API routing and security |
| Databases | PostgreSQL 15 | One database per service |
| Cache & Locks | Redis 7 | Distributed locks and caching |
| Message Queue | Apache Kafka | Event streaming |
| Monitoring | Prometheus + Grafana | Metrics and dashboards |
| Logging | ELK Stack | Centralized logging |
| Containerization | Docker Compose | Local orchestration |
| Production | Kubernetes | Cloud deployment |

## Services Architecture

```
┌─────────────────────────────────────────────────────┐
│                  API Gateway :8080                   │
└──────┬────────┬─────────┬─────────┬─────────────────┘
       │        │         │         │
       ▼        ▼         ▼         ▼
┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│  User    │ │Catalog │ │Booking │ │Payment │
│  :8081   │ │ :8082  │ │ :8083  │ │ :8084  │
└────┬─────┘ └───┬────┘ └───┬────┘ └───┬────┘
     │           │           │           │
┌────▼───────────▼───────────▼───────────▼────┐
│          Notification Service :8085          │
└──────────────────────────────────────────────┘

Infrastructure:
- 5 PostgreSQL databases (one per service)
- Redis (distributed locks & cache)
- Kafka (event streaming)
```

## Database Architecture

Each service has its own isolated database following microservices best practices:

- **user_service_db** (Port 5432) - User authentication and profiles
- **catalog_service_db** (Port 5433) - Movies, theaters, shows, seats
- **booking_service_db** (Port 5434) - Bookings and seat locks
- **payment_service_db** (Port 5435) - Payments and refunds
- **notification_service_db** (Port 5436) - Notification tracking

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Java 17+
- Maven 3.8+

### Running Locally

1. **Clone the repository**
```bash
git clone https://github.com/sgaurav007/book-my-show-clone.git
cd book-my-show-clone
```

2. **Start infrastructure only** (databases, Redis, Kafka)
```bash
docker-compose up -d user-db catalog-db booking-db payment-db notification-db redis zookeeper kafka
```

3. **Build all services**
```bash
./build-all.sh
```

4. **Start all services**
```bash
docker-compose up -d
```

5. **Check service health**
```bash
# API Gateway
curl http://localhost:8080/actuator/health

# User Service
curl http://localhost:8081/actuator/health

# Catalog Service
curl http://localhost:8082/actuator/health

# Booking Service
curl http://localhost:8083/actuator/health

# Payment Service
curl http://localhost:8084/actuator/health

# Notification Service
curl http://localhost:8085/actuator/health
```

### Running with Monitoring

To start services with Prometheus and Grafana:

```bash
docker-compose --profile monitoring up -d
```

Access:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### Running with ELK Stack

To start services with centralized logging:

```bash
docker-compose --profile elk up -d
```

Access:
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200

### Running Everything

To run all services with monitoring and logging:

```bash
docker-compose --profile monitoring --profile elk up -d
```

## API Endpoints

### User Service (Port 8081)
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile

### Catalog Service (Port 8082)
- `GET /api/movies` - List all movies
- `GET /api/movies/{id}` - Get movie details
- `GET /api/theaters?city={city}` - Get theaters by city
- `GET /api/shows?movieId={id}&city={city}&date={date}` - Get shows
- `GET /api/shows/{showId}/seats` - Get seat availability

### Booking Service (Port 8083)
- `POST /api/bookings/lock-seats` - Lock seats (15 min timeout)
- `POST /api/bookings/confirm` - Confirm booking
- `GET /api/bookings/{id}` - Get booking details
- `DELETE /api/bookings/{id}` - Cancel booking
- `GET /api/bookings/user/{userId}` - Get user bookings

### Payment Service (Port 8084)
- `POST /api/payments/initiate` - Initiate payment
- `POST /api/payments/webhook` - Payment gateway webhook
- `GET /api/payments/{id}` - Get payment details
- `POST /api/payments/refund` - Process refund

### API Gateway (Port 8080)

All services are accessible through the API Gateway with path-based routing:
- `/users/**` → User Service
- `/catalog/**` → Catalog Service
- `/bookings/**` → Booking Service
- `/payments/**` → Payment Service

## Kafka Topics

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `booking.created` | Booking Service | Analytics | Booking initiation |
| `booking.confirmed` | Booking Service | Notification | Send confirmation |
| `booking.cancelled` | Booking Service | Notification | Send cancellation notice |
| `payment.initiated` | Payment Service | Analytics | Payment started |
| `payment.success` | Payment Service | Notification, Booking | Payment completed |
| `payment.failed` | Payment Service | Notification, Booking | Payment failed |

## Key Features

### Real-Time Seat Locking
- Distributed locks using Redis
- 15-minute timeout on seat reservations
- Automatic lock release on timeout or payment failure
- Prevents double booking

### Event-Driven Architecture
- Asynchronous communication via Kafka
- Eventual consistency across services
- Decoupled service interactions
- High scalability

### Observability
- **Metrics**: Prometheus scrapes Spring Actuator endpoints
- **Dashboards**: Pre-configured Grafana dashboards
- **Logging**: Structured JSON logs to ELK stack
- **Tracing**: Correlation IDs across service calls

### Security
- JWT-based authentication
- Password hashing with BCrypt
- HTTPS in production
- Role-based access control (CUSTOMER, ADMIN, THEATER_OWNER)

## Development Guidelines

See [claude.md](./claude.md) for detailed development rules and best practices.

Key principles:
- ✅ Keep it simple - No over-engineering
- ✅ Complete features - No TODOs
- ✅ Explicit parameters - Everything required by default
- ✅ Direct code - Minimal abstractions
- ✅ Working > Perfect

## Project Structure

```
book-my-show-clone/
├── api-gateway/             # Spring Cloud Gateway
├── user-service/            # User management
├── catalog-service/         # Movies, theaters, shows
├── booking-service/         # Ticket bookings
├── payment-service/         # Payment processing
├── notification-service/    # Email/SMS notifications
├── monitoring/
│   ├── prometheus/          # Prometheus config
│   ├── grafana/             # Grafana dashboards
│   └── logstash/            # Logstash pipeline
├── k8s/                     # Kubernetes manifests
├── docker-compose.yml       # Local development
├── HLD.md                   # High-Level Design
├── LLD.md                   # Low-Level Design
├── claude.md                # Development rules
└── README.md
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

### Load Testing (JMeter)
```bash
./run-load-tests.sh
```

## Scaling Strategy

### Horizontal Scaling
- Stateless services (session in Redis)
- Kubernetes HPA based on CPU/memory
- Kafka consumer groups for parallel processing

### Database Scaling
- Read replicas for read-heavy operations
- Connection pooling (HikariCP)
- Proper indexing on foreign keys

### Caching Strategy
- Redis for frequently accessed data
- Seat availability cached with short TTL
- Cache invalidation via Kafka events

## Deployment

### Local Development
```bash
docker-compose up
```

### Kubernetes (Production)
```bash
kubectl apply -f k8s/
```

### Azure Deployment
See [docs/azure-deployment.md](./docs/azure-deployment.md)

## Monitoring & Alerts

### Grafana Dashboards
- Service health and uptime
- Request rate, latency, errors (RED metrics)
- JVM metrics (heap, GC)
- Database connection pool
- Kafka lag and throughput

### Prometheus Alerts
- High error rate (>5%)
- High latency (P95 >500ms)
- Service down
- Database connection pool exhaustion
- Kafka consumer lag

## Troubleshooting

### Service Not Starting
```bash
# Check logs
docker-compose logs -f <service-name>

# Check dependencies
docker-compose ps
```

### Database Connection Issues
```bash
# Check database is running
docker-compose ps user-db catalog-db booking-db payment-db notification-db

# Check connection from service
docker-compose exec user-service ping user-db
```

### Kafka Issues
```bash
# Check Kafka topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Check consumer groups
docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list
```

## Performance Benchmarks

| Metric | Target | Achieved |
|--------|--------|----------|
| Concurrent Users | 1M+ | TBD |
| Transactions/Day | 10M+ | TBD |
| API Latency (P95) | <200ms | TBD |
| System Uptime | 99.9% | TBD |
| Booking Success Rate | >95% | TBD |

## Future Enhancements

- [ ] AI-powered movie recommendations
- [ ] Dynamic pricing based on demand
- [ ] Social features (reviews, sharing)
- [ ] Mobile app (React Native)
- [ ] Multi-region deployment
- [ ] Chaos engineering tests

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Author

**Gaurav Singh**
- GitHub: [@sgaurav007](https://github.com/sgaurav007)
- Email: gaurav.singh@example.com

## Acknowledgments

- Spring Boot team for excellent framework
- Confluent for Kafka
- HashiCorp for best practices guides
- BookMyShow for inspiration

---

**⭐ Star this repo if you find it helpful!**
