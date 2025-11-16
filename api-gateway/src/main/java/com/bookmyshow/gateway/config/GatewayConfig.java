package com.bookmyshow.gateway.config;

import com.bookmyshow.gateway.filter.AuthenticationFilter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.ratelimit.KeyResolver;
import org.springframework.cloud.gateway.filter.ratelimit.RedisRateLimiter;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import reactor.core.publisher.Mono;

@Configuration
public class GatewayConfig {

    @Autowired
    private AuthenticationFilter authenticationFilter;

    @Value("${services.user-service.url}")
    private String userServiceUrl;

    @Value("${services.catalog-service.url}")
    private String catalogServiceUrl;

    @Value("${services.booking-service.url}")
    private String bookingServiceUrl;

    @Value("${services.payment-service.url}")
    private String paymentServiceUrl;

    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
                .route("user-service", r -> r.path("/api/users/**")
                        .filters(f -> f
                                .filter(authenticationFilter)
                                .requestRateLimiter(c -> c
                                        .setRateLimiter(redisRateLimiter())
                                        .setKeyResolver(userKeyResolver()))
                                .circuitBreaker(config -> config
                                        .setName("userServiceCircuitBreaker")
                                        .setFallbackUri("forward:/fallback/user-service"))
                                .retry(config -> config
                                        .setRetries(3)
                                        .setBackoff(null, null, null, false)))
                        .uri(userServiceUrl))

                .route("catalog-service", r -> r.path("/api/catalog/**")
                        .filters(f -> f
                                .filter(authenticationFilter)
                                .requestRateLimiter(c -> c
                                        .setRateLimiter(redisRateLimiter())
                                        .setKeyResolver(userKeyResolver()))
                                .circuitBreaker(config -> config
                                        .setName("catalogServiceCircuitBreaker")
                                        .setFallbackUri("forward:/fallback/catalog-service"))
                                .retry(config -> config
                                        .setRetries(3)
                                        .setBackoff(null, null, null, false)))
                        .uri(catalogServiceUrl))

                .route("booking-service", r -> r.path("/api/bookings/**")
                        .filters(f -> f
                                .filter(authenticationFilter)
                                .requestRateLimiter(c -> c
                                        .setRateLimiter(redisRateLimiter())
                                        .setKeyResolver(userKeyResolver()))
                                .circuitBreaker(config -> config
                                        .setName("bookingServiceCircuitBreaker")
                                        .setFallbackUri("forward:/fallback/booking-service"))
                                .retry(config -> config
                                        .setRetries(3)
                                        .setBackoff(null, null, null, false)))
                        .uri(bookingServiceUrl))

                .route("payment-service", r -> r.path("/api/payments/**")
                        .filters(f -> f
                                .filter(authenticationFilter)
                                .requestRateLimiter(c -> c
                                        .setRateLimiter(redisRateLimiter())
                                        .setKeyResolver(userKeyResolver()))
                                .circuitBreaker(config -> config
                                        .setName("paymentServiceCircuitBreaker")
                                        .setFallbackUri("forward:/fallback/payment-service"))
                                .retry(config -> config
                                        .setRetries(3)
                                        .setBackoff(null, null, null, false)))
                        .uri(paymentServiceUrl))

                .build();
    }

    @Bean
    public RedisRateLimiter redisRateLimiter() {
        return new RedisRateLimiter(100, 100, 1);
    }

    @Bean
    public KeyResolver userKeyResolver() {
        return exchange -> {
            String userId = exchange.getRequest().getHeaders().getFirst("X-User-Id");
            if (userId != null) {
                return Mono.just(userId);
            }
            String clientIp = exchange.getRequest().getRemoteAddress() != null ?
                    exchange.getRequest().getRemoteAddress().getAddress().getHostAddress() : "unknown";
            return Mono.just(clientIp);
        };
    }
}
