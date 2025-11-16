# Parallel Development Plan - BookMyShow Clone

## 🚀 Overview

Building all services **simultaneously** using sub-agents with **maximum reusability** and **BookMyShow-like UI**.

---

## 🎨 Frontend Library Choice

**Material-UI (MUI)** - Complete component library that matches BookMyShow's professional look

**Why MUI?**
- ✅ Complete component set (no custom components needed)
- ✅ Professional, clean design similar to BookMyShow
- ✅ Built-in theming system
- ✅ Accessibility compliant
- ✅ TypeScript support
- ✅ Highly customizable
- ✅ Large community and documentation

**Components We'll Use:**
- AppBar, Drawer, BottomNavigation (Navigation)
- Card, CardMedia (Movie cards)
- Grid, Container (Layouts)
- Button, TextField, Select (Forms)
- Dialog, Snackbar (Modals/Toasts)
- Chip (Tags/Filters)
- Rating (Movie ratings)
- Tabs (Theater selection)
- Stepper (Booking flow)
- DataGrid (Admin tables)

---

## 🔧 Maximum Reusability Strategy

### Backend Reusability

#### Shared Module (`shared/common`)
```
shared/common/
├── src/main/java/com/bookmyshow/common/
│   ├── dto/
│   │   ├── ApiResponse.java         # Standard API response wrapper
│   │   ├── ErrorResponse.java       # Standard error response
│   │   └── PageResponse.java        # Paginated response
│   ├── exception/
│   │   ├── GlobalExceptionHandler.java
│   │   ├── ResourceNotFoundException.java
│   │   ├── ValidationException.java
│   │   └── BusinessException.java
│   ├── config/
│   │   ├── RedisConfig.java         # Shared Redis config
│   │   ├── KafkaConfig.java         # Shared Kafka config
│   │   └── SecurityConfig.java      # Shared security config
│   ├── util/
│   │   ├── DateUtils.java
│   │   ├── StringUtils.java
│   │   └── ValidationUtils.java
│   ├── constants/
│   │   └── AppConstants.java
│   └── audit/
│       ├── Auditable.java           # Base audit entity
│       └── AuditListener.java
└── pom.xml
```

**All services will depend on this shared module.**

#### Base Entity Pattern
```java
@MappedSuperclass
@EntityListeners(AuditListener.class)
public abstract class BaseEntity {
    @CreatedDate
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @CreatedBy
    private String createdBy;

    @LastModifiedBy
    private String lastModifiedBy;
}
```

#### Standard API Response Pattern
```java
public class ApiResponse<T> {
    private boolean success;
    private String message;
    private T data;
    private LocalDateTime timestamp;
}
```

### Frontend Reusability

#### Shared Components (`frontend/app/components/shared`)
```typescript
shared/
├── Layout/
│   ├── MainLayout.tsx          # Common layout with header/footer
│   ├── AdminLayout.tsx         # Admin layout
│   └── AuthLayout.tsx          # Auth pages layout
├── MovieCard/
│   └── MovieCard.tsx           # Reusable movie card (MUI Card)
├── TheaterCard/
│   └── TheaterCard.tsx         # Reusable theater card
├── SeatLayout/
│   └── SeatLayout.tsx          # Reusable seat selection
├── Loader/
│   └── Loader.tsx              # Loading spinner
├── ErrorBoundary/
│   └── ErrorBoundary.tsx       # Error boundary
└── ProtectedRoute/
    └── ProtectedRoute.tsx      # Auth wrapper
```

#### Shared Hooks (`frontend/app/hooks/shared`)
```typescript
shared/
├── useAuth.ts                  # Auth state management
├── useApi.ts                   # API call wrapper
├── useLocalStorage.ts          # Local storage hook
├── useDebounce.ts              # Debounce hook
└── usePagination.ts            # Pagination hook
```

#### Shared Utils (`frontend/app/utils/shared`)
```typescript
shared/
├── api.ts                      # Axios instance with interceptors
├── constants.ts                # App constants
├── formatters.ts               # Date, currency formatters
├── validators.ts               # Form validators
└── storage.ts                  # Local/session storage utils
```

---

## 👥 Agent Assignment

### Agent 1: Shared Backend Module + User Service
**Responsibility:**
1. Create `shared/common` module with all reusable backend code
2. Build User Service using TDD
3. Implement JWT authentication
4. Write comprehensive tests

**Deliverables:**
- `shared/common/` (complete)
- `backend/user-service/` (complete with tests)
- JaCoCo coverage >80%

---

### Agent 2: Catalog Service
**Responsibility:**
1. Use shared module from Agent 1
2. Build Catalog Service using TDD
3. Implement movies, theaters, shows, seats APIs
4. Write comprehensive tests

**Deliverables:**
- `backend/catalog-service/` (complete with tests)
- JaCoCo coverage >80%

---

### Agent 3: Booking Service
**Responsibility:**
1. Use shared module from Agent 1
2. Build Booking Service using TDD
3. Implement Redis-based seat locking
4. Kafka event publishing
5. Write comprehensive tests

**Deliverables:**
- `backend/booking-service/` (complete with tests)
- JaCoCo coverage >80%

---

### Agent 4: Payment Service
**Responsibility:**
1. Use shared module from Agent 1
2. Build Payment Service using TDD
3. Implement mock payment gateway
4. Webhook handling
5. Write comprehensive tests

**Deliverables:**
- `backend/payment-service/` (complete with tests)
- JaCoCo coverage >80%

---

### Agent 5: Notification Service
**Responsibility:**
1. Use shared module from Agent 1
2. Build Notification Service using TDD
3. Kafka consumers for events
4. Mock email/SMS sending
5. Write comprehensive tests

**Deliverables:**
- `backend/notification-service/` (complete with tests)
- JaCoCo coverage >80%

---

### Agent 6: API Gateway
**Responsibility:**
1. Build Spring Cloud Gateway
2. Route configuration for all services
3. JWT validation
4. CORS configuration
5. Rate limiting

**Deliverables:**
- `backend/api-gateway/` (complete)

---

### Agent 7: Frontend (Material-UI)
**Responsibility:**
1. Set up Remix + TypeScript + Material-UI
2. Create shared components/hooks/utils
3. Build all pages (Home, Movies, Booking, Payment, Admin)
4. Implement BookMyShow-like UI
5. TanStack Query integration
6. Write tests (Vitest + Playwright)

**Deliverables:**
- `frontend/` (complete with tests)
- Vitest coverage >80%
- E2E tests for critical flows

---

## 📋 Development Standards (All Agents)

### TDD Approach
1. Write failing test first (RED)
2. Write minimal code to pass (GREEN)
3. Refactor while keeping tests green
4. Repeat

### Code Quality
- ✅ No TODOs
- ✅ No commented code
- ✅ All parameters required by default
- ✅ Simple, direct code (no over-engineering)
- ✅ Follow claude.md rules strictly

### Testing Requirements
- ✅ Unit tests: 60%
- ✅ Integration tests: 30%
- ✅ E2E tests: 10%
- ✅ Total coverage: >80%

### Shared Components Must Be Used
- Backend: All services MUST use `shared/common`
- Frontend: All pages MUST use shared components/hooks/utils

---

## 🎨 BookMyShow UI Requirements

### Design Principles
1. **Modern & Clean**: Material-UI's default theme
2. **Red Primary Color**: #C31E2E (BookMyShow red)
3. **Responsive**: Mobile-first design
4. **Fast**: Optimistic updates, skeleton loaders
5. **Accessible**: WCAG 2.1 AA compliant

### Theme Configuration
```typescript
const theme = createTheme({
  palette: {
    primary: {
      main: '#C31E2E', // BookMyShow red
    },
    secondary: {
      main: '#2B3148', // Dark blue
    },
    background: {
      default: '#F5F5F5',
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});
```

### Page Layouts

**1. Home Page**
- Hero banner (Carousel with MUI)
- "Now Showing" movies grid (MUI Grid + Card)
- "Coming Soon" section
- Footer with links

**2. Movies List**
- Filters sidebar (Genre, Language, Format)
- Movie cards grid
- Pagination

**3. Movie Details**
- Movie poster and info
- Show timings by theater
- "Book Now" button

**4. Seat Selection**
- Screen layout visualization
- Seat grid (color-coded: available, selected, booked)
- Price breakdown
- Timer (15 minutes countdown)

**5. Payment**
- Payment method selection
- Card input form
- Order summary
- Secure payment badge

**6. My Bookings**
- Bookings list (MUI DataGrid)
- Filters (Upcoming, Past, Cancelled)
- Download ticket button

**7. Admin Dashboard**
- Stats cards
- Charts (MUI Charts)
- Management tables

---

## 📦 Project Structure After Parallel Build

```
book-my-show-clone/
├── shared/
│   └── common/                    # ✅ Agent 1
│       ├── src/
│       └── pom.xml
├── backend/
│   ├── api-gateway/               # ✅ Agent 6
│   ├── user-service/              # ✅ Agent 1
│   ├── catalog-service/           # ✅ Agent 2
│   ├── booking-service/           # ✅ Agent 3
│   ├── payment-service/           # ✅ Agent 4
│   └── notification-service/      # ✅ Agent 5
└── frontend/                      # ✅ Agent 7
    ├── app/
    │   ├── components/
    │   │   ├── shared/
    │   │   └── pages/
    │   ├── hooks/
    │   │   └── shared/
    │   ├── utils/
    │   │   └── shared/
    │   ├── routes/
    │   └── styles/
    └── package.json
```

---

## 🔄 Integration Points

### Agent Dependencies
```
Agent 1 (Shared + User) → MUST complete first
    ↓
Agents 2-5 (Services) → Depend on shared module
    ↓
Agent 6 (Gateway) → Depends on all services being built
    ↓
Agent 7 (Frontend) → Depends on gateway being available
```

**Strategy:**
1. Start Agent 1 immediately
2. Once Agent 1 completes shared module, start Agents 2-5 in parallel
3. Start Agent 6 and 7 after services are ready

---

## ✅ Acceptance Criteria

### Per Service (Agents 1-5)
- [ ] All tests passing (Unit + Integration)
- [ ] Coverage >80%
- [ ] Dockerfile created
- [ ] application.yml configured
- [ ] README.md with API docs
- [ ] Uses shared/common module
- [ ] Follows TDD approach

### API Gateway (Agent 6)
- [ ] Routes all services correctly
- [ ] JWT validation working
- [ ] CORS configured
- [ ] Rate limiting implemented
- [ ] Health checks endpoint

### Frontend (Agent 7)
- [ ] All pages implemented
- [ ] BookMyShow-like UI
- [ ] Material-UI components used
- [ ] Shared components created
- [ ] All tests passing (Vitest + Playwright)
- [ ] Coverage >80%
- [ ] Responsive design
- [ ] Type-safe (TypeScript strict mode)

---

## 📊 Metrics to Track

Each agent will report:
- Lines of code written
- Number of tests written
- Test coverage percentage
- Time taken
- Issues encountered

---

## 🚀 Timeline Estimate

**Total Time:** ~2-3 hours (parallel execution)

| Agent | Task | Estimated Time |
|-------|------|----------------|
| Agent 1 | Shared + User Service | 45-60 min |
| Agent 2 | Catalog Service | 30-45 min |
| Agent 3 | Booking Service | 30-45 min |
| Agent 4 | Payment Service | 30-45 min |
| Agent 5 | Notification Service | 20-30 min |
| Agent 6 | API Gateway | 20-30 min |
| Agent 7 | Frontend | 60-90 min |

**Sequential Time:** ~4-5 hours
**Parallel Time:** ~2-3 hours
**Time Saved:** 40-50%

---

## 🎯 Ready to Launch!

All agents will:
1. Follow TDD strictly
2. Use shared modules for maximum reusability
3. Write comprehensive tests
4. Follow claude.md rules
5. Complete their assigned tasks fully (no TODOs)

**Frontend will look exactly like BookMyShow using Material-UI components.**

Let's build! 🚀
