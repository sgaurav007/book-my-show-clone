# BookMyShow Clone - Full-Stack Monorepo

A production-ready, scalable ticket booking platform built with React (Remix) frontend and Spring Boot microservices backend, designed to handle millions of concurrent users.

## 🎯 Project Overview

This is a complete full-stack implementation of BookMyShow featuring:
- **Frontend**: React with Remix framework, TanStack libraries
- **Backend**: Spring Boot microservices architecture
- **Infrastructure**: PostgreSQL, Redis, Kafka, Docker
- **Observability**: Prometheus, Grafana, ELK stack

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- 8GB+ RAM available
- Ports 3000, 8080-8085, 5432-5436, 6379, 9092 available

### Run Locally (Easy Mode)

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Or manually with Docker Compose:**
```bash
docker-compose up -d
```

Then open http://localhost:3000 in your browser.

### Stop the Application

**Linux/Mac:**
```bash
./stop.sh
```

**Windows:**
```cmd
stop.bat
```

For detailed setup instructions, troubleshooting, and development mode, see **[LOCAL_SETUP.md](./LOCAL_SETUP.md)**.

## 🏗️ Monorepo Structure

```
book-my-show-clone/
│
├── frontend/                           # React Remix Application
│   ├── app/
│   │   ├── routes/                     # Remix file-based routing
│   │   │   ├── _index.tsx             # Home page
│   │   │   ├── movies/
│   │   │   │   ├── $movieId.tsx       # Movie details
│   │   │   │   └── index.tsx          # Movies list
│   │   │   ├── theaters/
│   │   │   │   └── index.tsx          # Theaters list
│   │   │   ├── booking/
│   │   │   │   ├── $showId.tsx        # Seat selection
│   │   │   │   └── confirm.tsx        # Booking confirmation
│   │   │   ├── payment/
│   │   │   │   ├── index.tsx          # Payment page
│   │   │   │   └── success.tsx        # Payment success
│   │   │   ├── profile/
│   │   │   │   ├── index.tsx          # User profile
│   │   │   │   └── bookings.tsx       # My bookings
│   │   │   ├── auth/
│   │   │   │   ├── login.tsx          # Login
│   │   │   │   └── register.tsx       # Register
│   │   │   └── admin/                 # Admin routes
│   │   │       ├── movies.tsx
│   │   │       ├── theaters.tsx
│   │   │       └── shows.tsx
│   │   ├── components/                # React components
│   │   │   ├── ui/                    # shadcn/ui components
│   │   │   ├── MovieCard.tsx
│   │   │   ├── SeatLayout.tsx
│   │   │   ├── TheaterCard.tsx
│   │   │   ├── BookingCard.tsx
│   │   │   └── PaymentForm.tsx
│   │   ├── services/                  # API services
│   │   │   ├── api.ts                 # Axios/Fetch client
│   │   │   ├── auth.ts
│   │   │   ├── movies.ts
│   │   │   ├── bookings.ts
│   │   │   └── payments.ts
│   │   ├── hooks/                     # TanStack Query hooks
│   │   │   ├── useMovies.ts
│   │   │   ├── useTheaters.ts
│   │   │   ├── useBooking.ts
│   │   │   └── useAuth.ts
│   │   ├── utils/
│   │   │   ├── auth.ts
│   │   │   ├── constants.ts
│   │   │   └── helpers.ts
│   │   ├── root.tsx                   # Root component
│   │   └── entry.client.tsx
│   ├── public/
│   │   ├── images/
│   │   └── icons/
│   ├── package.json
│   ├── remix.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
│
├── backend/                            # Spring Boot Microservices
│   ├── api-gateway/                   # Spring Cloud Gateway
│   │   ├── src/main/java/com/bookmyshow/gateway/
│   │   │   ├── config/
│   │   │   │   ├── GatewayConfig.java
│   │   │   │   ├── SecurityConfig.java
│   │   │   │   └── CorsConfig.java
│   │   │   ├── filter/
│   │   │   │   ├── AuthenticationFilter.java
│   │   │   │   └── LoggingFilter.java
│   │   │   └── GatewayApplication.java
│   │   ├── src/main/resources/
│   │   │   └── application.yml
│   │   ├── pom.xml
│   │   └── Dockerfile
│   │
│   ├── user-service/                  # User Management
│   │   ├── src/main/java/com/bookmyshow/user/
│   │   │   ├── controller/
│   │   │   │   └── UserController.java
│   │   │   ├── service/
│   │   │   │   ├── UserService.java
│   │   │   │   └── AuthService.java
│   │   │   ├── repository/
│   │   │   │   ├── UserRepository.java
│   │   │   │   └── RefreshTokenRepository.java
│   │   │   ├── model/
│   │   │   │   ├── User.java
│   │   │   │   ├── RefreshToken.java
│   │   │   │   └── UserAddress.java
│   │   │   ├── dto/
│   │   │   │   ├── UserRegistrationRequest.java
│   │   │   │   ├── LoginRequest.java
│   │   │   │   └── LoginResponse.java
│   │   │   ├── security/
│   │   │   │   ├── JwtTokenProvider.java
│   │   │   │   └── SecurityConfig.java
│   │   │   ├── exception/
│   │   │   │   └── GlobalExceptionHandler.java
│   │   │   └── UserServiceApplication.java
│   │   ├── src/main/resources/
│   │   │   ├── application.yml
│   │   │   └── db/migration/
│   │   ├── pom.xml
│   │   └── Dockerfile
│   │
│   ├── catalog-service/               # Movies, Theaters, Shows
│   │   ├── src/main/java/com/bookmyshow/catalog/
│   │   │   ├── controller/
│   │   │   │   ├── MovieController.java
│   │   │   │   ├── TheaterController.java
│   │   │   │   └── ShowController.java
│   │   │   ├── service/
│   │   │   │   ├── MovieService.java
│   │   │   │   ├── TheaterService.java
│   │   │   │   └── ShowService.java
│   │   │   ├── repository/
│   │   │   ├── model/
│   │   │   │   ├── Movie.java
│   │   │   │   ├── Theater.java
│   │   │   │   ├── Screen.java
│   │   │   │   ├── Seat.java
│   │   │   │   └── Show.java
│   │   │   ├── dto/
│   │   │   └── CatalogServiceApplication.java
│   │   ├── src/main/resources/
│   │   ├── pom.xml
│   │   └── Dockerfile
│   │
│   ├── booking-service/               # Ticket Bookings
│   │   ├── src/main/java/com/bookmyshow/booking/
│   │   │   ├── controller/
│   │   │   │   └── BookingController.java
│   │   │   ├── service/
│   │   │   │   ├── BookingService.java
│   │   │   │   └── SeatLockService.java
│   │   │   ├── repository/
│   │   │   ├── model/
│   │   │   │   ├── Booking.java
│   │   │   │   └── BookingSeat.java
│   │   │   ├── kafka/
│   │   │   │   └── BookingEventProducer.java
│   │   │   └── BookingServiceApplication.java
│   │   ├── src/main/resources/
│   │   ├── pom.xml
│   │   └── Dockerfile
│   │
│   ├── payment-service/               # Payment Processing
│   │   ├── src/main/java/com/bookmyshow/payment/
│   │   │   ├── controller/
│   │   │   │   ├── PaymentController.java
│   │   │   │   └── WebhookController.java
│   │   │   ├── service/
│   │   │   │   ├── PaymentService.java
│   │   │   │   └── RefundService.java
│   │   │   ├── gateway/
│   │   │   │   ├── StripeGatewayAdapter.java
│   │   │   │   └── RazorpayGatewayAdapter.java
│   │   │   └── PaymentServiceApplication.java
│   │   ├── src/main/resources/
│   │   ├── pom.xml
│   │   └── Dockerfile
│   │
│   └── notification-service/          # Email/SMS Notifications
│       ├── src/main/java/com/bookmyshow/notification/
│       │   ├── kafka/
│       │   │   └── NotificationConsumer.java
│       │   ├── service/
│       │   │   ├── EmailService.java
│       │   │   └── SmsService.java
│       │   └── NotificationServiceApplication.java
│       ├── src/main/resources/
│       ├── pom.xml
│       └── Dockerfile
│
├── shared/                            # Shared configurations
│   ├── common/                        # Common utilities
│   │   └── pom.xml
│   └── types/                         # TypeScript types (shared)
│       └── api.types.ts
│
├── infrastructure/                    # Infrastructure configs
│   ├── k8s/                          # Kubernetes manifests
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── deployments/
│   │   │   ├── frontend.yaml
│   │   │   ├── api-gateway.yaml
│   │   │   ├── user-service.yaml
│   │   │   ├── catalog-service.yaml
│   │   │   ├── booking-service.yaml
│   │   │   ├── payment-service.yaml
│   │   │   └── notification-service.yaml
│   │   ├── services/
│   │   ├── ingress.yaml
│   │   └── hpa.yaml
│   │
│   ├── terraform/                    # Infrastructure as Code
│   │   ├── azure/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   └── modules/
│   │
│   └── helm/                         # Helm charts
│       └── bookmyshow/
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
│
├── monitoring/                        # Observability
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── rules/
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── services.json
│   │   │   ├── jvm.json
│   │   │   └── kafka.json
│   │   └── datasources/
│   └── logstash/
│       └── logstash.conf
│
├── docs/                             # Documentation
│   ├── api/
│   │   ├── user-service.md
│   │   ├── catalog-service.md
│   │   ├── booking-service.md
│   │   └── payment-service.md
│   ├── architecture/
│   │   ├── diagrams/
│   │   └── decisions/
│   └── deployment/
│       ├── local.md
│       ├── azure.md
│       └── aws.md
│
├── scripts/                          # Utility scripts
│   ├── build-all.sh
│   ├── start-dev.sh
│   ├── run-tests.sh
│   └── deploy.sh
│
├── docker-compose.yml                # Local development
├── docker-compose.monitoring.yml     # Monitoring stack
├── docker-compose.prod.yml           # Production-like setup
│
├── HLD.md                            # High-Level Design
├── LLD.md                            # Low-Level Design
├── claude.md                         # Development rules
├── .gitignore
├── README.md                         # This file
└── LICENSE
```

## 🎨 Frontend Architecture

### Tech Stack
- **Framework**: Remix (React)
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: TanStack Query (React Query)
- **Forms**: TanStack Form
- **Tables**: TanStack Table
- **Router**: TanStack Router (integrated with Remix)
- **Type Safety**: TypeScript
- **Build Tool**: Vite (via Remix)
- **Testing**: Vitest + React Testing Library

### Key Features
- Server-side rendering (SSR)
- Optimistic UI updates
- Real-time seat availability
- Responsive design
- Progressive Web App (PWA)
- SEO optimized

### TanStack Libraries Usage

#### TanStack Query
```typescript
// useMovies.ts
export function useMovies() {
  return useQuery({
    queryKey: ['movies'],
    queryFn: () => api.getMovies(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export function useBookSeat() {
  return useMutation({
    mutationFn: (data: BookSeatRequest) => api.bookSeat(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['seats'] })
    }
  })
}
```

#### TanStack Table
```typescript
// MyBookings.tsx
const table = useReactTable({
  data: bookings,
  columns: bookingColumns,
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
})
```

#### TanStack Form
```typescript
// LoginForm.tsx
const form = useForm({
  defaultValues: {
    email: '',
    password: '',
  },
  onSubmit: async ({ value }) => {
    await login(value)
  },
})
```

## 🔧 Backend Architecture

### Microservices

| Service | Port | Database | Purpose |
|---------|------|----------|---------|
| Frontend | 3000 | - | React Remix App |
| API Gateway | 8080 | - | Routing, Auth |
| User Service | 8081 | user_service_db | Authentication, Profiles |
| Catalog Service | 8082 | catalog_service_db | Movies, Theaters, Shows |
| Booking Service | 8083 | booking_service_db | Ticket Bookings |
| Payment Service | 8084 | payment_service_db | Payments, Refunds |
| Notification Service | 8085 | notification_service_db | Email, SMS |

### Infrastructure

| Component | Port | Purpose |
|-----------|------|---------|
| PostgreSQL (User) | 5432 | User data |
| PostgreSQL (Catalog) | 5433 | Catalog data |
| PostgreSQL (Booking) | 5434 | Booking data |
| PostgreSQL (Payment) | 5435 | Payment data |
| PostgreSQL (Notification) | 5436 | Notification data |
| Redis | 6379 | Cache, Locks |
| Kafka | 9092 | Event Streaming |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Dashboards |
| Kibana | 5601 | Log Viewer |

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+
- **Java** 17+
- **Maven** 3.8+
- **Docker** & Docker Compose
- **Git**

### 1. Clone Repository

```bash
git clone https://github.com/sgaurav007/book-my-show-clone.git
cd book-my-show-clone
```

### 2. Start Infrastructure

```bash
# Start databases, Redis, Kafka
docker-compose up -d user-db catalog-db booking-db payment-db notification-db redis zookeeper kafka
```

### 3. Build Backend Services

```bash
cd backend
./mvnw clean install -DskipTests

# Or use the script
./scripts/build-all.sh
```

### 4. Start Backend Services

```bash
# Start all backend services
docker-compose up -d api-gateway user-service catalog-service booking-service payment-service notification-service
```

### 5. Setup Frontend

```bash
cd frontend
npm install
```

### 6. Start Frontend (Development)

```bash
npm run dev
# Frontend runs on http://localhost:3000
```

### 7. Start Everything at Once

```bash
# From root directory
docker-compose up -d

# With monitoring
docker-compose --profile monitoring up -d

# With monitoring + ELK
docker-compose --profile monitoring --profile elk up -d
```

## 📱 BookMyShow Features

### User Features
- ✅ User registration and login
- ✅ Browse movies (Now Showing, Coming Soon)
- ✅ Search movies by title, genre, language
- ✅ Filter theaters by location
- ✅ View show timings
- ✅ Select seats (interactive seat map)
- ✅ Real-time seat availability
- ✅ Apply promo codes
- ✅ Multiple payment options
- ✅ Booking confirmation (Email/SMS)
- ✅ View booking history
- ✅ Cancel bookings
- ✅ Download tickets (PDF)
- ✅ Rate and review movies

### Admin Features
- ✅ Add/Edit/Delete movies
- ✅ Manage theaters and screens
- ✅ Schedule shows
- ✅ Configure seat layouts
- ✅ Set pricing (base + dynamic)
- ✅ View analytics dashboard
- ✅ Generate reports
- ✅ Manage users
- ✅ Handle refunds

### Theater Owner Features
- ✅ Register theater
- ✅ Manage screens and seats
- ✅ Schedule shows
- ✅ Set show pricing
- ✅ View bookings
- ✅ Revenue reports

## 🎯 User Flows

### 1. Movie Booking Flow

```
Home → Browse Movies → Select Movie → Choose Theater & Show
→ Select Seats → Review Booking → Payment → Confirmation
```

### 2. Seat Selection Flow

```
View Seat Layout → Select Seats (max 10) → Seats Locked (15 min)
→ Proceed to Payment → Payment Success → Booking Confirmed
→ Seats Released if Payment Fails/Timeout
```

### 3. Payment Flow

```
Review Booking → Select Payment Method → Enter Details
→ Process Payment → Webhook Callback → Confirm Booking
→ Send Confirmation Email/SMS
```

## 🖥️ Frontend Pages

### Public Pages
- `/` - Home (Featured movies, banners)
- `/movies` - Movies list with filters
- `/movies/:movieId` - Movie details
- `/theaters` - Theaters list
- `/auth/login` - Login
- `/auth/register` - Register

### Protected Pages
- `/booking/:showId` - Seat selection
- `/booking/confirm` - Booking review
- `/payment` - Payment page
- `/payment/success` - Success page
- `/profile` - User profile
- `/profile/bookings` - My bookings
- `/profile/settings` - Settings

### Admin Pages
- `/admin/dashboard` - Analytics
- `/admin/movies` - Movie management
- `/admin/theaters` - Theater management
- `/admin/shows` - Show management
- `/admin/users` - User management

## 🔌 API Endpoints

### User Service (`/api/users`)
```
POST   /register          - Register user
POST   /login            - Login
POST   /logout           - Logout
GET    /profile          - Get profile
PUT    /profile          - Update profile
POST   /refresh          - Refresh token
```

### Catalog Service (`/api/catalog`)
```
GET    /movies                    - List movies
GET    /movies/:id                - Movie details
GET    /movies/search?q=          - Search movies
GET    /theaters?city=            - List theaters
GET    /shows?movieId=&city=&date= - List shows
GET    /shows/:showId/seats       - Seat availability
```

### Booking Service (`/api/bookings`)
```
POST   /lock-seats       - Lock seats (15 min)
POST   /confirm          - Confirm booking
GET    /:id              - Booking details
DELETE /:id              - Cancel booking
GET    /user/:userId     - User's bookings
```

### Payment Service (`/api/payments`)
```
POST   /initiate         - Initiate payment
POST   /webhook          - Gateway webhook
GET    /:id              - Payment details
POST   /refund           - Process refund
```

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test              # Unit tests
npm run test:e2e          # E2E tests (Playwright)
npm run test:coverage     # Coverage report
```

### Backend Tests
```bash
cd backend
./mvnw test              # Unit tests
./mvnw verify            # Integration tests
./mvnw jacoco:report     # Coverage report
```

### Load Testing
```bash
./scripts/run-load-tests.sh
```

## 📊 Monitoring

### Access Dashboards

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601

### Key Metrics

- Request rate, latency, errors (RED metrics)
- JVM metrics (heap, GC)
- Database connection pool
- Kafka lag
- Cache hit ratio
- Seat lock success rate

## 🚢 Deployment

### Local Development
```bash
docker-compose up
```

### Production (Azure)
```bash
# Build and push Docker images
./scripts/build-and-push.sh

# Deploy with Terraform
cd infrastructure/terraform/azure
terraform init
terraform plan
terraform apply

# Or deploy with Helm
helm install bookmyshow infrastructure/helm/bookmyshow
```

### CI/CD Pipeline

```
GitHub → GitHub Actions → Build → Test → Docker Build
→ Push to Registry → Deploy to Azure K8s → Smoke Tests
```

## 🔒 Security

- ✅ JWT-based authentication
- ✅ Password hashing (BCrypt)
- ✅ HTTPS/TLS encryption
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF tokens
- ✅ Secure headers
- ✅ Input validation

## 🌍 Environment Variables

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8080
VITE_APP_NAME=BookMyShow
VITE_GOOGLE_CLIENT_ID=xxx
```

### Backend (application.yml)
```yaml
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  redis:
    host: ${REDIS_HOST}
    port: ${REDIS_PORT}
kafka:
  bootstrap-servers: ${KAFKA_BOOTSTRAP_SERVERS}
```

## 📈 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Page Load Time | < 2s | ⏳ |
| API Response (P95) | < 200ms | ⏳ |
| Concurrent Users | 1M+ | ⏳ |
| Transactions/Day | 10M+ | ⏳ |
| System Uptime | 99.9% | ⏳ |
| Seat Lock Success | > 95% | ⏳ |

## 🛠️ Development

### Code Style
- Follow [claude.md](./claude.md) guidelines
- Use ESLint + Prettier (Frontend)
- Use Checkstyle (Backend)
- Write meaningful commit messages

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Make changes
git add .
git commit -m "feat: add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

## 📚 Documentation

- [HLD.md](./HLD.md) - High-Level Design
- [LLD.md](./LLD.md) - Low-Level Design
- [claude.md](./claude.md) - Development Rules
- [API Documentation](./docs/api/)
- [Deployment Guide](./docs/deployment/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📝 License

MIT License - See [LICENSE](LICENSE)

## 👨‍💻 Author

**Gaurav Singh**
- GitHub: [@sgaurav007](https://github.com/sgaurav007)
- LinkedIn: [Gaurav Singh](https://linkedin.com/in/sgaurav007)

## 🙏 Acknowledgments

- Remix team for excellent framework
- TanStack for amazing libraries
- Spring Boot team
- BookMyShow for inspiration

---

**⭐ Star this repo if you find it helpful!**

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Email: gaurav.singh@example.com
- Discord: [Join our server](https://discord.gg/bookmyshow-clone)

---

Built with ❤️ using React, Remix, Spring Boot, and TanStack
