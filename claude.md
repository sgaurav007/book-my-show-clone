# Claude Development Rules - BookMyShow Clone

## 🚫 What NOT to Do

- ❌ **Don't over-engineer** — No defensive checks, complicated methods for type checking, unnecessary field or variables
- ❌ **Don't add unused features or extreme edge cases** — Build only what's specified
- ❌ **Don't create complex abstractions** — Keep it direct and simple
- ❌ **Don't optimize prematurely** — Make it work first
- ❌ **Don't leave TODOs** — Complete everything
- ❌ **Don't add validators or fallback behaviours "just in case"** — This is a greenfield project so keep schemas and services strict and fill fields correctly at the source
- ❌ **Don't mark arguments optional unless the flow truly allows omission** — Every parameter should be explicit and required by default

## ✅ What TO Do

- ✅ **Keep it simple** — Write straightforward, readable code
- ✅ **Build only what's needed** — No speculative features
- ✅ **Database per service** — Follow microservices pattern with separate databases
- ✅ **Complete implementations** — No TODOs, no partial work
- ✅ **Explicit parameters** — Everything required by default
- ✅ **Direct code** — No unnecessary abstractions
- ✅ **Docker-first** — Ensure everything runs locally with docker-compose

## 🏗️ Development Principles

### Keep It Simple, Stupid (KISS)
- Write code that's easy to read and understand
- Avoid clever tricks or complex patterns
- Use simple, descriptive names

### Don't Repeat Yourself (DRY)
- Extract common logic into shared functions
- But don't create abstractions until you have duplication

### Minimal Files
- Combine related logic in the same file
- Split only when it improves clarity
- Avoid excessive layers (service → repository is enough)

## 📐 Architecture Guidelines

### Database per Service
- Each microservice has its own PostgreSQL database
- Follows microservices best practices
- Database isolation for better scalability

### Local-First Development
- Everything must run with `docker-compose up`
- No complex Kubernetes setup for local dev
- Use environment variables for configuration

### No Premature Optimization
- Don't add caching until needed
- Don't add read replicas initially
- Don't add complex partitioning strategies
- Make it work, then measure, then optimize

## 🎯 Core Principles

**Working > Perfect**
- Ship functional code over perfectly architected code
- Iterate based on actual needs, not theoretical ones

**Simple > Complex**
- Choose the simplest solution that works
- Add complexity only when simplicity fails

**Complete > Partial**
- Finish features fully before moving on
- No half-implemented flows

**Clear > Clever**
- Readable code beats clever optimizations
- Future you (and others) will thank you

## 🛠️ Technology Choices

### Must Use
- **Spring Boot 3.x** - Framework
- **PostgreSQL** - Separate database per service
- **Redis** - Caching and distributed locks
- **Kafka** - Event streaming
- **Docker & Docker Compose** - Local development
- **Kubernetes** - Production deployment configs

### Keep Simple in Code
- **REST APIs** for inter-service communication (gRPC optional)
- **Spring Cloud Gateway** for API gateway
- **Simple service discovery** (Docker service names locally, Eureka/Consul for production)

## 📝 Code Style

### Entities
```java
@Entity
@Table(name = "users")
@Data
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String email;

    // Simple, direct fields - no complex mappings
}
```

### Services
```java
@Service
@Transactional
public class UserService {

    @Autowired
    private UserRepository userRepository;

    // Direct methods, no complex abstractions
    public User createUser(CreateUserRequest request) {
        User user = new User();
        user.setEmail(request.getEmail());
        return userRepository.save(user);
    }
}
```

### Controllers
```java
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserService userService;

    // Simple endpoints
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody CreateUserRequest request) {
        return ResponseEntity.ok(userService.createUser(request));
    }
}
```

## 🗄️ Database Strategy

### Database per Service Approach
```
user_service_db (PostgreSQL)
├── users
├── user_addresses
└── refresh_tokens

catalog_service_db (PostgreSQL)
├── movies
├── theaters
├── screens
├── seats
└── shows

booking_service_db (PostgreSQL)
├── bookings
├── booking_seats
└── seat_locks

payment_service_db (PostgreSQL)
├── payments
├── refunds
└── payment_audit_log

notification_service_db (PostgreSQL)
└── notifications
```

**Database per service** - Following microservices best practices for data isolation

## 🐳 Docker Strategy

### Local Development
- Single `docker-compose.yml` file
- All services, database, Redis, Kafka in one compose file
- Hot reload enabled for development
- Simple service discovery (use service names)

### No Production-Grade Setup Initially
- Don't add multi-stage Docker builds initially
- Don't add health checks until needed
- Don't add resource limits prematurely

## 🚀 Development Workflow

1. **Start simple** - Get basic functionality working
2. **Test locally** - Use docker-compose
3. **Iterate** - Add features incrementally
4. **Measure** - Add observability when needed
5. **Optimize** - Only when you have data showing bottlenecks

## 📊 Observability

### Implement from Start
- **Logging**: SLF4J with structured logging (JSON format)
- **Metrics**: Spring Actuator + Prometheus
- **Monitoring**: Grafana dashboards
- **Tracing**: Distributed tracing with correlation IDs
- **Centralized Logging**: ELK stack (Elasticsearch, Logstash, Kibana)

## ⚡ Performance

### Implement Smart Patterns
- Efficient CRUD operations with proper indexing
- Redis caching for frequently accessed data
- Connection pooling (HikariCP)
- Database indexing on foreign keys and frequently queried columns
- Distributed locks for seat booking (Redis)
- Kafka for async operations

## 🔒 Security (Keep Essential)

### Must Have
- Password hashing (BCrypt)
- JWT for authentication
- HTTPS in production

### Skip Initially
- Complex OAuth flows
- Rate limiting (add if needed)
- Advanced RBAC (start with simple roles)

## 📦 Dependencies (Minimal)

### Core Dependencies Only
```xml
- spring-boot-starter-web
- spring-boot-starter-data-jpa
- spring-boot-starter-security
- postgresql
- lombok
- spring-kafka
- spring-boot-starter-data-redis
```

### Don't Add Unless Needed
- Unnecessary validation libraries
- Complex mapping libraries (use simple setters)
- Excessive logging frameworks
- Performance monitoring libraries initially

## 🎯 Remember

**"Premature optimization is the root of all evil" - Donald Knuth**

Build it simple, make it work, then improve based on real needs.

---

## Quick Checklist Before Committing

- [ ] Is this the simplest solution?
- [ ] Did I avoid over-engineering?
- [ ] Are all parameters explicit and required?
- [ ] Did I complete this feature fully (no TODOs)?
- [ ] Can this run locally with docker-compose?
- [ ] Did I use the single database?
- [ ] Is the code readable and clear?
