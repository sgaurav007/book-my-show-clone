# Catalog Service

## Overview

The Catalog Service manages movies, theaters, screens, seats, and shows in the BookMyShow clone application. Built using strict Test-Driven Development (TDD) approach.

## Technology Stack

- **Java 17**
- **Spring Boot 3.2.0**
- **PostgreSQL** (Database on port 5433)
- **Redis** (Caching)
- **Kafka** (Event Streaming)
- **Flyway** (Database Migrations)
- **JUnit 5** (Unit Testing)
- **Mockito** (Mocking)
- **RestAssured** (API Testing)
- **TestContainers** (Integration Testing)

## Architecture

### Entities
All entities extend `BaseEntity` from the shared/common module:

1. **Movie** - Movie information (title, description, duration, language, genre, etc.)
2. **Theater** - Theater information (name, city, address, location)
3. **Screen** - Theater screens with seat capacity
4. **Seat** - Individual seats with types (REGULAR, PREMIUM, VIP)
5. **Show** - Movie showings with timing and pricing

### API Endpoints

#### Movies
- `POST /api/catalog/movies` - Create a new movie (Admin)
- `GET /api/catalog/movies` - Get all movies (paginated)
- `GET /api/catalog/movies/{id}` - Get movie by ID
- `GET /api/catalog/movies/search?q={query}` - Search movies by title or genre
- `PUT /api/catalog/movies/{id}` - Update movie (Admin)
- `DELETE /api/catalog/movies/{id}` - Delete movie (Admin)

#### Theaters
- `POST /api/catalog/theaters` - Create a new theater (Admin)
- `GET /api/catalog/theaters` - Get all theaters
- `GET /api/catalog/theaters?city={city}` - Get theaters by city
- `GET /api/catalog/theaters/{id}` - Get theater by ID
- `DELETE /api/catalog/theaters/{id}` - Delete theater (Admin)

#### Shows
- `POST /api/catalog/shows` - Create a new show (Admin)
- `GET /api/catalog/shows?movieId={id}&city={city}&date={date}` - Get shows with filters
- `GET /api/catalog/shows/{id}` - Get show by ID
- `GET /api/catalog/shows/{id}/seats` - Get available seats for a show
- `DELETE /api/catalog/shows/{id}` - Delete show (Admin)

## Database Schema

### Tables
1. **movies** - Movie catalog
2. **movie_genres** - Movie genre mappings (ElementCollection)
3. **theaters** - Theater locations
4. **screens** - Theater screens
5. **seats** - Seat layout per screen
6. **shows** - Movie showings

### Indexes
- Movies: title, language, release_date, is_active
- Theaters: city, is_active
- Screens: theater_id
- Seats: screen_id, row_label
- Shows: movie_id, screen_id, start_time

## TDD Approach

### Test Coverage

#### Unit Tests (Service Layer)
1. **MovieServiceTest** - 8 test cases
   - Create, read, update, delete operations
   - Search functionality
   - Active movies filtering

2. **TheaterServiceTest** - 7 test cases
   - CRUD operations
   - Filter by city

3. **ShowServiceTest** - 9 test cases
   - Create with validation
   - Filter by movie, city, date
   - Seat availability

#### Controller Tests (REST API)
1. **MovieControllerTest** - 5 test cases (RestAssured)
2. **TheaterControllerTest** - 2 test cases (RestAssured)
3. **ShowControllerTest** - 3 test cases (RestAssured)

#### Integration Tests
1. **CatalogServiceIntegrationTest** - 3 test cases (TestContainers)
   - End-to-end testing with PostgreSQL container
   - Full request-response cycle testing

**Total Test Files:** 7
**Total Test Cases:** ~40+

## Configuration

### application.yml
- **Database:** PostgreSQL on port 5433
- **Server Port:** 8081
- **Redis:** localhost:6379
- **Kafka:** localhost:9092

### Environment Variables
```bash
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5433/catalog_db
SPRING_DATASOURCE_USERNAME=postgres
SPRING_DATASOURCE_PASSWORD=postgres
SPRING_REDIS_HOST=localhost
SPRING_KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

## Running the Service

### Prerequisites
- Java 17+
- Maven 3.8+
- PostgreSQL 15
- Redis
- Kafka

### Build
```bash
# Build shared module first
cd ../../shared/common
mvn clean install

# Build catalog service
cd ../../backend/catalog-service
mvn clean package
```

### Run Tests
```bash
mvn test
```

### Run with Test Coverage
```bash
mvn clean test jacoco:report
```

Coverage report will be available at: `target/site/jacoco/index.html`

### Run Application
```bash
mvn spring-boot:run
```

### Docker
```bash
docker build -t catalog-service:latest .
docker run -p 8081:8081 catalog-service:latest
```

## Database Migrations

Flyway migrations are located in `src/main/resources/db/migration`:

1. **V1** - Create movies table
2. **V2** - Create movie_genres table
3. **V3** - Create theaters table
4. **V4** - Create screens table
5. **V5** - Create seats table
6. **V6** - Create shows table
7. **V7** - Insert test data

Test data includes:
- 5 popular movies (Inception, The Dark Knight, Interstellar, Dangal, 3 Idiots)
- 5 theaters across Mumbai, Delhi, Bangalore
- 8 screens with complete seat layouts
- 10 shows scheduled for upcoming days

## Test Data

### Sample Movies
- **Inception** (English, Action/Sci-Fi)
- **The Dark Knight** (English, Action/Crime)
- **Interstellar** (English, Adventure/Sci-Fi)
- **Dangal** (Hindi, Biography/Sport)
- **3 Idiots** (Hindi, Comedy/Drama)

### Sample Theaters
- PVR Cinemas Phoenix (Mumbai)
- INOX Megaplex (Mumbai)
- PVR Select City Walk (Delhi)
- Cinepolis DLF Place (Delhi)
- PVR VR Mall (Bangalore)

## API Response Format

All responses follow the standard `ApiResponse` format from shared/common:

```json
{
  "success": true,
  "message": "Success",
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00"
}
```

## Error Handling

Global exception handling via `GlobalExceptionHandler` from shared/common:
- `ResourceNotFoundException` - 404
- `ValidationException` - 400
- `BusinessException` - 400
- Generic `Exception` - 500

## Development Guidelines

Following `claude.md` rules:
- ✅ No TODOs
- ✅ No over-engineering
- ✅ All parameters required by default
- ✅ Simple, direct code
- ✅ Complete implementations
- ✅ TDD approach followed strictly
- ✅ Uses shared/common module

## Monitoring

### Actuator Endpoints
- `/actuator/health` - Health check
- `/actuator/info` - Application info
- `/actuator/metrics` - Metrics
- `/actuator/prometheus` - Prometheus metrics

## Dependencies

### Core
- spring-boot-starter-web
- spring-boot-starter-data-jpa
- spring-boot-starter-data-redis
- spring-kafka
- postgresql
- flyway-core

### Testing
- spring-boot-starter-test
- testcontainers (PostgreSQL)
- rest-assured
- jacoco (code coverage)

### Shared
- common:1.0.0 (shared module)

## Project Structure

```
catalog-service/
├── src/
│   ├── main/
│   │   ├── java/com/bookmyshow/catalog/
│   │   │   ├── controller/      # REST controllers (3)
│   │   │   ├── dto/             # Request/Response DTOs (4)
│   │   │   ├── entity/          # JPA entities (5)
│   │   │   ├── repository/      # Spring Data repositories (5)
│   │   │   ├── service/         # Business logic (4)
│   │   │   └── CatalogServiceApplication.java
│   │   └── resources/
│   │       ├── db/migration/    # Flyway migrations (7)
│   │       ├── application.yml
│   │       └── application-test.yml
│   └── test/
│       └── java/com/bookmyshow/catalog/
│           ├── controller/      # Controller tests (3)
│           ├── service/         # Service tests (3)
│           └── integration/     # Integration tests (1)
├── Dockerfile
├── pom.xml
└── README.md
```

## Files Created

**Total Files:** 39
- Java Files: 29 (22 main + 7 test)
- SQL Migrations: 7
- Configuration: 2 (application.yml, application-test.yml)
- Build: 2 (pom.xml, Dockerfile)

## Next Steps

1. Run tests to verify >80% coverage
2. Deploy to Docker container
3. Integrate with API Gateway
4. Add authentication/authorization
5. Performance testing and optimization
