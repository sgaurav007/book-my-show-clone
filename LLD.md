# Low-Level Design (LLD) - BookMyShow Clone

## Table of Contents
1. [Database Schemas](#1-database-schemas)
2. [User Service](#2-user-service)
3. [Catalog Service](#3-catalog-service)
4. [Booking Service](#4-booking-service)
5. [Payment Service](#5-payment-service)
6. [Notification Service](#6-notification-service)
7. [API Contracts](#7-api-contracts)
8. [Sequence Diagrams](#8-sequence-diagrams)
9. [Class Diagrams](#9-class-diagrams)
10. [Kafka Topics & Events](#10-kafka-topics--events)

---

## 1. Database Schemas

### 1.1 User Service Database (user_db)

#### Table: users
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) UNIQUE,
    role VARCHAR(50) NOT NULL DEFAULT 'CUSTOMER', -- CUSTOMER, ADMIN, THEATER_OWNER
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_phone (phone_number)
);
```

#### Table: user_addresses
```sql
CREATE TABLE user_addresses (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_user_id (user_id)
);
```

#### Table: refresh_tokens
```sql
CREATE TABLE refresh_tokens (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(512) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_token (token)
);
```

---

### 1.2 Catalog Service Database (catalog_db)

#### Table: movies
```sql
CREATE TABLE movies (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL,
    language VARCHAR(50) NOT NULL,
    release_date DATE NOT NULL,
    rating VARCHAR(10), -- U, U/A, A, R
    genre VARCHAR(255), -- JSON array: ["Action", "Drama"]
    poster_url VARCHAR(512),
    trailer_url VARCHAR(512),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_title (title),
    INDEX idx_release_date (release_date),
    INDEX idx_language (language)
);
```

#### Table: theaters
```sql
CREATE TABLE theaters (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(512) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    owner_id BIGINT NOT NULL, -- References users.id
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_city (city),
    INDEX idx_owner_id (owner_id)
);
```

#### Table: screens
```sql
CREATE TABLE screens (
    id BIGSERIAL PRIMARY KEY,
    theater_id BIGINT NOT NULL REFERENCES theaters(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    total_seats INT NOT NULL,
    screen_type VARCHAR(50), -- IMAX, 3D, 4DX, STANDARD
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_theater_id (theater_id)
);
```

#### Table: seats
```sql
CREATE TABLE seats (
    id BIGSERIAL PRIMARY KEY,
    screen_id BIGINT NOT NULL REFERENCES screens(id) ON DELETE CASCADE,
    seat_number VARCHAR(10) NOT NULL, -- A1, A2, B1, etc.
    row_name VARCHAR(5) NOT NULL,
    seat_type VARCHAR(50) NOT NULL, -- REGULAR, PREMIUM, VIP
    price_multiplier DECIMAL(3, 2) DEFAULT 1.00,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (screen_id, seat_number),
    INDEX idx_screen_id (screen_id)
);
```

#### Table: shows
```sql
CREATE TABLE shows (
    id BIGSERIAL PRIMARY KEY,
    movie_id BIGINT NOT NULL REFERENCES movies(id),
    screen_id BIGINT NOT NULL REFERENCES screens(id),
    show_date DATE NOT NULL,
    show_time TIME NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    available_seats INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_movie_id (movie_id),
    INDEX idx_screen_id (screen_id),
    INDEX idx_show_date (show_date),
    UNIQUE (screen_id, show_date, show_time)
);
```

---

### 1.3 Booking Service Database (booking_db)

#### Table: bookings
```sql
CREATE TABLE bookings (
    id BIGSERIAL PRIMARY KEY,
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL, -- References users.id
    show_id BIGINT NOT NULL, -- References shows.id
    total_amount DECIMAL(10, 2) NOT NULL,
    booking_status VARCHAR(50) NOT NULL, -- PENDING, CONFIRMED, CANCELLED, EXPIRED
    payment_id BIGINT, -- References payments.id
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP, -- Seat lock expiry (15 mins from creation)
    INDEX idx_user_id (user_id),
    INDEX idx_show_id (show_id),
    INDEX idx_booking_reference (booking_reference),
    INDEX idx_booking_status (booking_status),
    INDEX idx_expires_at (expires_at)
);
```

#### Table: booking_seats
```sql
CREATE TABLE booking_seats (
    id BIGSERIAL PRIMARY KEY,
    booking_id BIGINT NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    seat_id BIGINT NOT NULL, -- References seats.id
    seat_number VARCHAR(10) NOT NULL,
    seat_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_booking_id (booking_id),
    UNIQUE (booking_id, seat_id)
);
```

#### Table: seat_locks
```sql
CREATE TABLE seat_locks (
    id BIGSERIAL PRIMARY KEY,
    show_id BIGINT NOT NULL,
    seat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    lock_expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (show_id, seat_id),
    INDEX idx_show_seat (show_id, seat_id),
    INDEX idx_lock_expires (lock_expires_at)
);
```

---

### 1.4 Payment Service Database (payment_db)

#### Table: payments
```sql
CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    payment_reference VARCHAR(100) UNIQUE NOT NULL,
    booking_id BIGINT NOT NULL UNIQUE, -- References bookings.id
    user_id BIGINT NOT NULL, -- References users.id
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    payment_method VARCHAR(50), -- CARD, UPI, NETBANKING, WALLET
    payment_status VARCHAR(50) NOT NULL, -- INITIATED, SUCCESS, FAILED, REFUNDED
    gateway_transaction_id VARCHAR(255),
    gateway_name VARCHAR(50), -- STRIPE, RAZORPAY
    failure_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_booking_id (booking_id),
    INDEX idx_user_id (user_id),
    INDEX idx_payment_status (payment_status),
    INDEX idx_payment_reference (payment_reference)
);
```

#### Table: refunds
```sql
CREATE TABLE refunds (
    id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT NOT NULL REFERENCES payments(id),
    refund_amount DECIMAL(10, 2) NOT NULL,
    refund_status VARCHAR(50) NOT NULL, -- INITIATED, SUCCESS, FAILED
    refund_reference VARCHAR(100) UNIQUE,
    gateway_refund_id VARCHAR(255),
    reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_payment_id (payment_id),
    INDEX idx_refund_status (refund_status)
);
```

#### Table: payment_audit_log
```sql
CREATE TABLE payment_audit_log (
    id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT NOT NULL REFERENCES payments(id),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_payment_id (payment_id),
    INDEX idx_event_type (event_type)
);
```

---

### 1.5 Notification Service Database (notification_db)

#### Table: notifications
```sql
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL, -- References users.id
    notification_type VARCHAR(50) NOT NULL, -- EMAIL, SMS, PUSH
    channel VARCHAR(50) NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    status VARCHAR(50) NOT NULL, -- PENDING, SENT, FAILED
    sent_at TIMESTAMP,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    metadata JSONB, -- Additional data like booking_id, etc.
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_notification_type (notification_type)
);
```

---

## 2. User Service

### 2.1 Package Structure
```
user-service/
├── src/main/java/com/bookmyshow/user/
│   ├── controller/
│   │   └── UserController.java
│   ├── service/
│   │   ├── UserService.java
│   │   └── AuthService.java
│   ├── repository/
│   │   ├── UserRepository.java
│   │   └── RefreshTokenRepository.java
│   ├── model/
│   │   ├── User.java
│   │   ├── RefreshToken.java
│   │   └── UserAddress.java
│   ├── dto/
│   │   ├── UserRegistrationRequest.java
│   │   ├── LoginRequest.java
│   │   ├── LoginResponse.java
│   │   └── UserProfileResponse.java
│   ├── security/
│   │   ├── JwtTokenProvider.java
│   │   └── SecurityConfig.java
│   ├── exception/
│   │   ├── UserNotFoundException.java
│   │   └── InvalidCredentialsException.java
│   └── config/
│       └── RedisConfig.java
└── src/main/resources/
    ├── application.yml
    └── db/migration/
```

### 2.2 Core Classes

#### User.java (Entity)
```java
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String passwordHash;

    @Column(nullable = false)
    private String firstName;

    @Column(nullable = false)
    private String lastName;

    @Column(unique = true)
    private String phoneNumber;

    @Enumerated(EnumType.STRING)
    private UserRole role = UserRole.CUSTOMER;

    private Boolean isActive = true;
    private Boolean isEmailVerified = false;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;

    private LocalDateTime lastLoginAt;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<UserAddress> addresses;
}

enum UserRole {
    CUSTOMER, ADMIN, THEATER_OWNER
}
```

#### UserService.java
```java
@Service
@Slf4j
public class UserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    public User registerUser(UserRegistrationRequest request) {
        // Validate email uniqueness
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new UserAlreadyExistsException("Email already registered");
        }

        User user = new User();
        user.setEmail(request.getEmail());
        user.setPasswordHash(passwordEncoder.encode(request.getPassword()));
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setPhoneNumber(request.getPhoneNumber());
        user.setRole(UserRole.CUSTOMER);

        User savedUser = userRepository.save(user);

        // Cache user profile
        cacheUserProfile(savedUser);

        log.info("User registered successfully: {}", savedUser.getEmail());
        return savedUser;
    }

    public User getUserById(Long userId) {
        // Check cache first
        String cacheKey = "user:profile:" + userId;
        User cachedUser = (User) redisTemplate.opsForValue().get(cacheKey);

        if (cachedUser != null) {
            return cachedUser;
        }

        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException("User not found"));

        cacheUserProfile(user);
        return user;
    }

    private void cacheUserProfile(User user) {
        String cacheKey = "user:profile:" + user.getId();
        redisTemplate.opsForValue().set(cacheKey, user, 30, TimeUnit.MINUTES);
    }
}
```

#### AuthService.java
```java
@Service
@Slf4j
public class AuthService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private RefreshTokenRepository refreshTokenRepository;

    public LoginResponse authenticate(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
            .orElseThrow(() -> new InvalidCredentialsException("Invalid credentials"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new InvalidCredentialsException("Invalid credentials");
        }

        if (!user.getIsActive()) {
            throw new AccountInactiveException("Account is inactive");
        }

        // Generate JWT tokens
        String accessToken = jwtTokenProvider.generateAccessToken(user);
        String refreshToken = jwtTokenProvider.generateRefreshToken(user);

        // Save refresh token
        saveRefreshToken(user, refreshToken);

        // Update last login
        user.setLastLoginAt(LocalDateTime.now());
        userRepository.save(user);

        log.info("User authenticated successfully: {}", user.getEmail());

        return new LoginResponse(accessToken, refreshToken, user.getId(), user.getEmail());
    }

    private void saveRefreshToken(User user, String token) {
        RefreshToken refreshToken = new RefreshToken();
        refreshToken.setUser(user);
        refreshToken.setToken(token);
        refreshToken.setExpiresAt(LocalDateTime.now().plusDays(7));
        refreshTokenRepository.save(refreshToken);
    }
}
```

### 2.3 API Endpoints

| Method | Endpoint                | Description                |
|--------|-------------------------|----------------------------|
| POST   | `/api/users/register`   | Register new user          |
| POST   | `/api/users/login`      | Login user                 |
| POST   | `/api/users/logout`     | Logout user                |
| POST   | `/api/users/refresh`    | Refresh access token       |
| GET    | `/api/users/profile`    | Get user profile           |
| PUT    | `/api/users/profile`    | Update user profile        |
| POST   | `/api/users/verify-email` | Verify email             |
| POST   | `/api/users/forgot-password` | Request password reset |

---

## 3. Catalog Service

### 3.1 Package Structure
```
catalog-service/
├── src/main/java/com/bookmyshow/catalog/
│   ├── controller/
│   │   ├── MovieController.java
│   │   ├── TheaterController.java
│   │   └── ShowController.java
│   ├── service/
│   │   ├── MovieService.java
│   │   ├── TheaterService.java
│   │   ├── ShowService.java
│   │   └── SearchService.java
│   ├── repository/
│   │   ├── MovieRepository.java
│   │   ├── TheaterRepository.java
│   │   ├── ScreenRepository.java
│   │   ├── SeatRepository.java
│   │   └── ShowRepository.java
│   ├── model/
│   │   ├── Movie.java
│   │   ├── Theater.java
│   │   ├── Screen.java
│   │   ├── Seat.java
│   │   └── Show.java
│   └── elasticsearch/
│       └── MovieDocument.java
```

### 3.2 Core Classes

#### Movie.java (Entity)
```java
@Entity
@Table(name = "movies")
@Data
public class Movie {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    private Integer durationMinutes;
    private String language;
    private LocalDate releaseDate;
    private String rating; // U, U/A, A, R

    @Type(JsonBinaryType.class)
    @Column(columnDefinition = "jsonb")
    private List<String> genre;

    private String posterUrl;
    private String trailerUrl;
    private Boolean isActive = true;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
```

#### Show.java (Entity)
```java
@Entity
@Table(name = "shows")
@Data
public class Show {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "movie_id")
    private Movie movie;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "screen_id")
    private Screen screen;

    private LocalDate showDate;
    private LocalTime showTime;
    private BigDecimal basePrice;
    private Integer availableSeats;
    private Boolean isActive = true;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}
```

#### ShowService.java
```java
@Service
@Slf4j
public class ShowService {

    @Autowired
    private ShowRepository showRepository;

    @Autowired
    private SeatRepository seatRepository;

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    public List<Show> getShowsByMovieAndCity(Long movieId, String city, LocalDate date) {
        String cacheKey = String.format("shows:movie:%d:city:%s:date:%s", movieId, city, date);

        // Check cache
        List<Show> cachedShows = (List<Show>) redisTemplate.opsForValue().get(cacheKey);
        if (cachedShows != null) {
            return cachedShows;
        }

        List<Show> shows = showRepository.findByMovieAndCityAndDate(movieId, city, date);

        // Cache for 5 minutes
        redisTemplate.opsForValue().set(cacheKey, shows, 5, TimeUnit.MINUTES);

        return shows;
    }

    public ShowSeatsResponse getShowSeats(Long showId) {
        Show show = showRepository.findById(showId)
            .orElseThrow(() -> new ShowNotFoundException("Show not found"));

        List<Seat> seats = seatRepository.findByScreenId(show.getScreen().getId());

        // Get locked seats from Redis
        Set<Long> lockedSeats = getLockedSeats(showId);

        // Get booked seats from database
        Set<Long> bookedSeats = getBookedSeats(showId);

        return new ShowSeatsResponse(seats, lockedSeats, bookedSeats);
    }

    private Set<Long> getLockedSeats(Long showId) {
        String pattern = String.format("seat:lock:%d:*", showId);
        Set<String> keys = redisTemplate.keys(pattern);

        return keys.stream()
            .map(key -> Long.parseLong(key.split(":")[3]))
            .collect(Collectors.toSet());
    }
}
```

### 3.3 API Endpoints

| Method | Endpoint                          | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/api/movies`                     | Get all movies                 |
| GET    | `/api/movies/{id}`                | Get movie by ID                |
| GET    | `/api/movies/search`              | Search movies                  |
| GET    | `/api/theaters`                   | Get theaters by city           |
| GET    | `/api/shows?movieId=&city=&date=` | Get shows for movie            |
| GET    | `/api/shows/{showId}/seats`       | Get seat availability          |
| POST   | `/api/movies` (Admin)             | Create movie                   |
| PUT    | `/api/movies/{id}` (Admin)        | Update movie                   |

---

## 4. Booking Service

### 4.1 Package Structure
```
booking-service/
├── src/main/java/com/bookmyshow/booking/
│   ├── controller/
│   │   └── BookingController.java
│   ├── service/
│   │   ├── BookingService.java
│   │   ├── SeatLockService.java
│   │   └── BookingEventPublisher.java
│   ├── repository/
│   │   ├── BookingRepository.java
│   │   └── BookingSeatRepository.java
│   ├── model/
│   │   ├── Booking.java
│   │   └── BookingSeat.java
│   ├── dto/
│   │   ├── LockSeatsRequest.java
│   │   ├── ConfirmBookingRequest.java
│   │   └── BookingResponse.java
│   └── kafka/
│       └── BookingEventProducer.java
```

### 4.2 Core Classes

#### Booking.java (Entity)
```java
@Entity
@Table(name = "bookings")
@Data
public class Booking {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String bookingReference;

    private Long userId;
    private Long showId;

    private BigDecimal totalAmount;

    @Enumerated(EnumType.STRING)
    private BookingStatus bookingStatus;

    private Long paymentId;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;

    private LocalDateTime expiresAt;

    @OneToMany(mappedBy = "booking", cascade = CascadeType.ALL)
    private List<BookingSeat> seats;
}

enum BookingStatus {
    PENDING, CONFIRMED, CANCELLED, EXPIRED
}
```

#### SeatLockService.java
```java
@Service
@Slf4j
public class SeatLockService {

    @Autowired
    private RedisTemplate<String, Object> redisTemplate;

    private static final int LOCK_DURATION_MINUTES = 15;

    public boolean lockSeats(Long showId, List<Long> seatIds, Long userId) {
        List<String> lockKeys = seatIds.stream()
            .map(seatId -> getLockKey(showId, seatId))
            .collect(Collectors.toList());

        // Try to acquire locks atomically using Lua script
        String luaScript =
            "for i, key in ipairs(KEYS) do " +
            "  if redis.call('EXISTS', key) == 1 then " +
            "    return 0 " +
            "  end " +
            "end " +
            "for i, key in ipairs(KEYS) do " +
            "  redis.call('SETEX', key, ARGV[1], ARGV[2]) " +
            "end " +
            "return 1";

        DefaultRedisScript<Long> script = new DefaultRedisScript<>(luaScript, Long.class);

        Long result = redisTemplate.execute(
            script,
            lockKeys,
            String.valueOf(LOCK_DURATION_MINUTES * 60),
            userId.toString()
        );

        boolean locked = result != null && result == 1;

        if (locked) {
            log.info("Seats locked successfully for showId: {}, userId: {}", showId, userId);
        } else {
            log.warn("Failed to lock seats for showId: {}, userId: {}", showId, userId);
        }

        return locked;
    }

    public void unlockSeats(Long showId, List<Long> seatIds) {
        List<String> lockKeys = seatIds.stream()
            .map(seatId -> getLockKey(showId, seatId))
            .collect(Collectors.toList());

        redisTemplate.delete(lockKeys);
        log.info("Seats unlocked for showId: {}", showId);
    }

    private String getLockKey(Long showId, Long seatId) {
        return String.format("seat:lock:%d:%d", showId, seatId);
    }

    public boolean validateLock(Long showId, Long seatId, Long userId) {
        String lockKey = getLockKey(showId, seatId);
        String lockedUserId = (String) redisTemplate.opsForValue().get(lockKey);

        return lockedUserId != null && lockedUserId.equals(userId.toString());
    }
}
```

#### BookingService.java
```java
@Service
@Slf4j
@Transactional
public class BookingService {

    @Autowired
    private BookingRepository bookingRepository;

    @Autowired
    private SeatLockService seatLockService;

    @Autowired
    private BookingEventPublisher eventPublisher;

    @Autowired
    private ShowServiceClient showServiceClient; // Feign client

    public LockSeatsResponse lockSeats(LockSeatsRequest request) {
        Long showId = request.getShowId();
        List<Long> seatIds = request.getSeatIds();
        Long userId = request.getUserId();

        // Validate show exists and is active
        ShowDTO show = showServiceClient.getShow(showId);
        if (!show.getIsActive()) {
            throw new ShowNotAvailableException("Show is not active");
        }

        // Try to lock seats
        boolean locked = seatLockService.lockSeats(showId, seatIds, userId);

        if (!locked) {
            throw new SeatsNotAvailableException("Some seats are already locked/booked");
        }

        // Calculate total amount
        BigDecimal totalAmount = calculateTotalAmount(show, seatIds);

        // Create pending booking
        Booking booking = new Booking();
        booking.setBookingReference(generateBookingReference());
        booking.setUserId(userId);
        booking.setShowId(showId);
        booking.setTotalAmount(totalAmount);
        booking.setBookingStatus(BookingStatus.PENDING);
        booking.setExpiresAt(LocalDateTime.now().plusMinutes(15));

        // Add seats
        List<BookingSeat> bookingSeats = seatIds.stream()
            .map(seatId -> {
                BookingSeat seat = new BookingSeat();
                seat.setBooking(booking);
                seat.setSeatId(seatId);
                seat.setSeatPrice(show.getBasePrice());
                return seat;
            })
            .collect(Collectors.toList());

        booking.setSeats(bookingSeats);

        Booking savedBooking = bookingRepository.save(booking);

        log.info("Booking created with reference: {}", savedBooking.getBookingReference());

        return new LockSeatsResponse(savedBooking.getId(), savedBooking.getBookingReference(), totalAmount);
    }

    public BookingResponse confirmBooking(ConfirmBookingRequest request) {
        Booking booking = bookingRepository.findById(request.getBookingId())
            .orElseThrow(() -> new BookingNotFoundException("Booking not found"));

        // Validate booking status
        if (booking.getBookingStatus() != BookingStatus.PENDING) {
            throw new InvalidBookingStateException("Booking is not in pending state");
        }

        // Validate not expired
        if (LocalDateTime.now().isAfter(booking.getExpiresAt())) {
            booking.setBookingStatus(BookingStatus.EXPIRED);
            bookingRepository.save(booking);
            throw new BookingExpiredException("Booking has expired");
        }

        // Update booking status
        booking.setBookingStatus(BookingStatus.CONFIRMED);
        booking.setPaymentId(request.getPaymentId());

        Booking confirmedBooking = bookingRepository.save(booking);

        // Release seat locks (they're now booked)
        List<Long> seatIds = booking.getSeats().stream()
            .map(BookingSeat::getSeatId)
            .collect(Collectors.toList());
        seatLockService.unlockSeats(booking.getShowId(), seatIds);

        // Publish booking confirmed event
        eventPublisher.publishBookingConfirmed(confirmedBooking);

        log.info("Booking confirmed: {}", confirmedBooking.getBookingReference());

        return new BookingResponse(confirmedBooking);
    }

    private String generateBookingReference() {
        return "BMS" + System.currentTimeMillis() + RandomStringUtils.randomAlphanumeric(6).toUpperCase();
    }
}
```

### 4.3 API Endpoints

| Method | Endpoint                        | Description                  |
|--------|---------------------------------|------------------------------|
| POST   | `/api/bookings/lock-seats`      | Lock seats for booking       |
| POST   | `/api/bookings/confirm`         | Confirm booking after payment|
| GET    | `/api/bookings/{id}`            | Get booking details          |
| DELETE | `/api/bookings/{id}`            | Cancel booking               |
| GET    | `/api/bookings/user/{userId}`   | Get user's bookings          |

---

## 5. Payment Service

### 5.1 Package Structure
```
payment-service/
├── src/main/java/com/bookmyshow/payment/
│   ├── controller/
│   │   ├── PaymentController.java
│   │   └── WebhookController.java
│   ├── service/
│   │   ├── PaymentService.java
│   │   ├── PaymentGatewayService.java
│   │   └── RefundService.java
│   ├── repository/
│   │   ├── PaymentRepository.java
│   │   └── RefundRepository.java
│   ├── model/
│   │   ├── Payment.java
│   │   └── Refund.java
│   └── gateway/
│       ├── StripeGatewayAdapter.java
│       └── RazorpayGatewayAdapter.java
```

### 5.2 Core Classes

#### Payment.java (Entity)
```java
@Entity
@Table(name = "payments")
@Data
public class Payment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true)
    private String paymentReference;

    private Long bookingId;
    private Long userId;

    private BigDecimal amount;
    private String currency = "INR";

    @Enumerated(EnumType.STRING)
    private PaymentMethod paymentMethod;

    @Enumerated(EnumType.STRING)
    private PaymentStatus paymentStatus;

    private String gatewayTransactionId;
    private String gatewayName;

    @Column(columnDefinition = "TEXT")
    private String failureReason;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;
}

enum PaymentStatus {
    INITIATED, SUCCESS, FAILED, REFUNDED
}

enum PaymentMethod {
    CARD, UPI, NETBANKING, WALLET
}
```

#### PaymentService.java
```java
@Service
@Slf4j
@Transactional
public class PaymentService {

    @Autowired
    private PaymentRepository paymentRepository;

    @Autowired
    private PaymentGatewayService gatewayService;

    @Autowired
    private BookingServiceClient bookingServiceClient;

    @Autowired
    private KafkaTemplate<String, Object> kafkaTemplate;

    public PaymentResponse initiatePayment(PaymentRequest request) {
        // Validate booking exists and is in pending state
        BookingDTO booking = bookingServiceClient.getBooking(request.getBookingId());

        if (!booking.getStatus().equals("PENDING")) {
            throw new InvalidBookingStateException("Booking is not in pending state");
        }

        // Create payment record
        Payment payment = new Payment();
        payment.setPaymentReference(generatePaymentReference());
        payment.setBookingId(request.getBookingId());
        payment.setUserId(request.getUserId());
        payment.setAmount(booking.getTotalAmount());
        payment.setPaymentMethod(request.getPaymentMethod());
        payment.setPaymentStatus(PaymentStatus.INITIATED);
        payment.setGatewayName(request.getGatewayName());

        Payment savedPayment = paymentRepository.save(payment);

        // Initiate payment with gateway
        GatewayResponse gatewayResponse = gatewayService.initiatePayment(
            savedPayment.getPaymentReference(),
            savedPayment.getAmount(),
            request.getPaymentMethod()
        );

        savedPayment.setGatewayTransactionId(gatewayResponse.getTransactionId());
        paymentRepository.save(savedPayment);

        // Publish payment initiated event
        publishPaymentEvent("payment.initiated", savedPayment);

        log.info("Payment initiated: {}", savedPayment.getPaymentReference());

        return new PaymentResponse(
            savedPayment.getId(),
            savedPayment.getPaymentReference(),
            gatewayResponse.getPaymentUrl()
        );
    }

    public void handlePaymentSuccess(String paymentReference, String gatewayTransactionId) {
        Payment payment = paymentRepository.findByPaymentReference(paymentReference)
            .orElseThrow(() -> new PaymentNotFoundException("Payment not found"));

        // Idempotency check
        if (payment.getPaymentStatus() == PaymentStatus.SUCCESS) {
            log.warn("Payment already processed: {}", paymentReference);
            return;
        }

        payment.setPaymentStatus(PaymentStatus.SUCCESS);
        payment.setGatewayTransactionId(gatewayTransactionId);
        paymentRepository.save(payment);

        // Confirm booking
        bookingServiceClient.confirmBooking(payment.getBookingId(), payment.getId());

        // Publish payment success event
        publishPaymentEvent("payment.success", payment);

        log.info("Payment successful: {}", paymentReference);
    }

    public void handlePaymentFailure(String paymentReference, String reason) {
        Payment payment = paymentRepository.findByPaymentReference(paymentReference)
            .orElseThrow(() -> new PaymentNotFoundException("Payment not found"));

        payment.setPaymentStatus(PaymentStatus.FAILED);
        payment.setFailureReason(reason);
        paymentRepository.save(payment);

        // Release seat locks
        bookingServiceClient.cancelBooking(payment.getBookingId());

        // Publish payment failed event
        publishPaymentEvent("payment.failed", payment);

        log.error("Payment failed: {}, reason: {}", paymentReference, reason);
    }

    private void publishPaymentEvent(String topic, Payment payment) {
        PaymentEvent event = new PaymentEvent(payment);
        kafkaTemplate.send(topic, event);
    }

    private String generatePaymentReference() {
        return "PAY" + System.currentTimeMillis() + RandomStringUtils.randomAlphanumeric(8).toUpperCase();
    }
}
```

### 5.3 API Endpoints

| Method | Endpoint                     | Description                |
|--------|------------------------------|----------------------------|
| POST   | `/api/payments/initiate`     | Initiate payment           |
| POST   | `/api/payments/webhook`      | Handle gateway webhook     |
| GET    | `/api/payments/{id}`         | Get payment details        |
| POST   | `/api/payments/refund`       | Initiate refund            |
| GET    | `/api/payments/booking/{id}` | Get payment by booking ID  |

---

## 6. Notification Service

### 6.1 Package Structure
```
notification-service/
├── src/main/java/com/bookmyshow/notification/
│   ├── kafka/
│   │   └── NotificationConsumer.java
│   ├── service/
│   │   ├── EmailService.java
│   │   ├── SmsService.java
│   │   └── PushNotificationService.java
│   ├── repository/
│   │   └── NotificationRepository.java
│   ├── model/
│   │   └── Notification.java
│   └── template/
│       ├── EmailTemplateService.java
│       └── templates/
```

### 6.2 Core Classes

#### NotificationConsumer.java
```java
@Component
@Slf4j
public class NotificationConsumer {

    @Autowired
    private EmailService emailService;

    @Autowired
    private SmsService smsService;

    @Autowired
    private NotificationRepository notificationRepository;

    @KafkaListener(topics = "booking.confirmed", groupId = "notification-service")
    public void handleBookingConfirmed(BookingConfirmedEvent event) {
        log.info("Received booking confirmed event: {}", event.getBookingId());

        try {
            // Send email
            emailService.sendBookingConfirmationEmail(
                event.getUserEmail(),
                event.getBookingReference(),
                event.getMovieTitle(),
                event.getTheaterName(),
                event.getShowDateTime(),
                event.getSeats(),
                event.getTotalAmount()
            );

            // Send SMS
            smsService.sendBookingConfirmationSms(
                event.getUserPhone(),
                event.getBookingReference(),
                event.getMovieTitle(),
                event.getShowDateTime()
            );

            // Save notification record
            saveNotification(event.getUserId(), "BOOKING_CONFIRMED", "SUCCESS");

        } catch (Exception e) {
            log.error("Failed to send booking confirmation notification", e);
            saveNotification(event.getUserId(), "BOOKING_CONFIRMED", "FAILED");
        }
    }

    @KafkaListener(topics = "payment.success", groupId = "notification-service")
    public void handlePaymentSuccess(PaymentSuccessEvent event) {
        log.info("Received payment success event: {}", event.getPaymentId());

        // Send payment receipt email
        emailService.sendPaymentReceiptEmail(event);
    }

    @KafkaListener(topics = "payment.failed", groupId = "notification-service")
    public void handlePaymentFailed(PaymentFailedEvent event) {
        log.info("Received payment failed event: {}", event.getPaymentId());

        // Send payment failure notification
        emailService.sendPaymentFailureEmail(event);
    }

    private void saveNotification(Long userId, String type, String status) {
        Notification notification = new Notification();
        notification.setUserId(userId);
        notification.setNotificationType(type);
        notification.setStatus(status);
        notificationRepository.save(notification);
    }
}
```

#### EmailService.java
```java
@Service
@Slf4j
public class EmailService {

    @Autowired
    private JavaMailSender mailSender;

    @Autowired
    private EmailTemplateService templateService;

    @Value("${app.email.from}")
    private String fromEmail;

    public void sendBookingConfirmationEmail(
        String toEmail,
        String bookingReference,
        String movieTitle,
        String theaterName,
        String showDateTime,
        List<String> seats,
        BigDecimal totalAmount
    ) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");

            helper.setFrom(fromEmail);
            helper.setTo(toEmail);
            helper.setSubject("Booking Confirmed - " + bookingReference);

            // Generate HTML content from template
            String htmlContent = templateService.generateBookingConfirmationTemplate(
                bookingReference, movieTitle, theaterName, showDateTime, seats, totalAmount
            );

            helper.setText(htmlContent, true);

            mailSender.send(message);

            log.info("Booking confirmation email sent to: {}", toEmail);

        } catch (Exception e) {
            log.error("Failed to send booking confirmation email", e);
            throw new EmailSendException("Failed to send email", e);
        }
    }
}
```

---

## 7. API Contracts

### 7.1 Request/Response DTOs

#### LockSeatsRequest
```json
{
  "showId": 101,
  "seatIds": [1, 2, 3],
  "userId": 1001
}
```

#### LockSeatsResponse
```json
{
  "bookingId": 5001,
  "bookingReference": "BMS1699876543ABCD12",
  "totalAmount": 900.00,
  "expiresAt": "2024-11-16T10:30:00",
  "message": "Seats locked successfully. Complete payment within 15 minutes."
}
```

#### PaymentRequest
```json
{
  "bookingId": 5001,
  "userId": 1001,
  "paymentMethod": "CARD",
  "gatewayName": "RAZORPAY"
}
```

#### PaymentResponse
```json
{
  "paymentId": 7001,
  "paymentReference": "PAY1699876543XYZ12345",
  "paymentUrl": "https://razorpay.com/checkout/xyz123",
  "status": "INITIATED"
}
```

---

## 8. Sequence Diagrams

### 8.1 Booking Flow (Happy Path)

```
User -> Gateway: GET /api/shows/{showId}/seats
Gateway -> Catalog Service: getShowSeats()
Catalog Service -> Redis: getLockedSeats()
Catalog Service -> Database: getBookedSeats()
Catalog Service -> Gateway: return available seats
Gateway -> User: display seat layout

User -> Gateway: POST /api/bookings/lock-seats
Gateway -> Booking Service: lockSeats(request)
Booking Service -> Redis: acquireDistributedLock(seats)
Redis -> Booking Service: lock acquired
Booking Service -> Database: createBooking(PENDING)
Booking Service -> Gateway: return bookingReference
Gateway -> User: seats locked for 15 mins

User -> Gateway: POST /api/payments/initiate
Gateway -> Payment Service: initiatePayment(request)
Payment Service -> Booking Service: validateBooking()
Payment Service -> Database: createPayment(INITIATED)
Payment Service -> Payment Gateway: createPaymentOrder()
Payment Gateway -> Payment Service: return paymentUrl
Payment Service -> Kafka: publish payment.initiated
Payment Service -> Gateway: return paymentUrl
Gateway -> User: redirect to payment page

User -> Payment Gateway: complete payment
Payment Gateway -> Payment Service: POST /webhook (payment success)
Payment Service -> Database: updatePayment(SUCCESS)
Payment Service -> Booking Service: confirmBooking()
Booking Service -> Database: updateBooking(CONFIRMED)
Booking Service -> Redis: releaseSeatsLock()
Booking Service -> Kafka: publish booking.confirmed
Payment Service -> Kafka: publish payment.success
Payment Service -> Payment Gateway: acknowledge webhook

Notification Service <- Kafka: consume booking.confirmed
Notification Service -> Email Service: sendConfirmationEmail()
Notification Service -> SMS Service: sendConfirmationSms()
```

### 8.2 Payment Failure Flow

```
Payment Gateway -> Payment Service: POST /webhook (payment failed)
Payment Service -> Database: updatePayment(FAILED)
Payment Service -> Booking Service: cancelBooking()
Booking Service -> Database: updateBooking(CANCELLED)
Booking Service -> Redis: releaseSeatsLock()
Booking Service -> Kafka: publish booking.cancelled
Payment Service -> Kafka: publish payment.failed

Notification Service <- Kafka: consume payment.failed
Notification Service -> Email Service: sendPaymentFailureEmail()
```

---

## 9. Class Diagrams

### 9.1 Booking Service Domain Model

```
┌─────────────────────────────────┐
│         Booking                 │
├─────────────────────────────────┤
│ - id: Long                      │
│ - bookingReference: String      │
│ - userId: Long                  │
│ - showId: Long                  │
│ - totalAmount: BigDecimal       │
│ - bookingStatus: BookingStatus  │
│ - paymentId: Long               │
│ - createdAt: LocalDateTime      │
│ - expiresAt: LocalDateTime      │
├─────────────────────────────────┤
│ + confirm()                     │
│ + cancel()                      │
│ + isExpired(): boolean          │
└──────────┬──────────────────────┘
           │ 1
           │ contains
           │ *
┌──────────▼──────────────────────┐
│       BookingSeat               │
├─────────────────────────────────┤
│ - id: Long                      │
│ - bookingId: Long               │
│ - seatId: Long                  │
│ - seatNumber: String            │
│ - seatPrice: BigDecimal         │
└─────────────────────────────────┘
```

---

## 10. Kafka Topics & Events

### 10.1 Kafka Topics

| Topic Name          | Partitions | Replication | Producer           | Consumer            |
|---------------------|------------|-------------|--------------------|---------------------|
| booking.created     | 10         | 3           | Booking Service    | Analytics           |
| booking.confirmed   | 10         | 3           | Booking Service    | Notification        |
| booking.cancelled   | 10         | 3           | Booking Service    | Notification        |
| payment.initiated   | 10         | 3           | Payment Service    | Analytics           |
| payment.success     | 10         | 3           | Payment Service    | Notification, Analytics |
| payment.failed      | 10         | 3           | Payment Service    | Notification        |

### 10.2 Event Schemas

#### BookingConfirmedEvent
```json
{
  "eventId": "evt_1699876543_abc123",
  "eventType": "BOOKING_CONFIRMED",
  "timestamp": "2024-11-16T10:15:30Z",
  "data": {
    "bookingId": 5001,
    "bookingReference": "BMS1699876543ABCD12",
    "userId": 1001,
    "userEmail": "user@example.com",
    "userPhone": "+919876543210",
    "showId": 101,
    "movieTitle": "Inception",
    "theaterName": "PVR Phoenix",
    "showDateTime": "2024-11-16T18:00:00",
    "seats": ["A1", "A2", "A3"],
    "totalAmount": 900.00,
    "paymentId": 7001
  }
}
```

#### PaymentSuccessEvent
```json
{
  "eventId": "evt_1699876544_xyz789",
  "eventType": "PAYMENT_SUCCESS",
  "timestamp": "2024-11-16T10:15:25Z",
  "data": {
    "paymentId": 7001,
    "paymentReference": "PAY1699876543XYZ12345",
    "bookingId": 5001,
    "userId": 1001,
    "amount": 900.00,
    "currency": "INR",
    "paymentMethod": "CARD",
    "gatewayTransactionId": "razorpay_xyz123"
  }
}
```

---

## Conclusion

This Low-Level Design provides comprehensive implementation details for building the BookMyShow clone. Each microservice is designed with:

- **Clear separation of concerns**: Controllers, Services, Repositories
- **Database schemas**: Optimized with proper indexing
- **Distributed locking**: Redis-based seat locking mechanism
- **Event-driven architecture**: Kafka for async communication
- **Idempotency**: Preventing duplicate payments
- **Scalability**: Caching, connection pooling, partitioning
- **Observability**: Structured logging, metrics

The design ensures high availability, consistency, and scalability while maintaining clean architecture principles.
