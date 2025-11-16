package com.bookmyshow.gateway.filter;

import com.bookmyshow.gateway.util.JwtUtil;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.mock.http.server.reactive.MockServerHttpRequest;
import org.springframework.mock.web.server.MockServerWebExchange;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthFilterTest {

    @Mock
    private JwtUtil jwtUtil;

    @Mock
    private GatewayFilterChain filterChain;

    @InjectMocks
    private AuthenticationFilter authenticationFilter;

    private ServerWebExchange exchange;

    @BeforeEach
    void setUp() {
        when(filterChain.filter(any(ServerWebExchange.class))).thenReturn(Mono.empty());
    }

    @Test
    void testOpenEndpointAllowedWithoutToken() {
        MockServerHttpRequest request = MockServerHttpRequest
                .get("/api/users/login")
                .build();
        exchange = MockServerWebExchange.from(request);

        Mono<Void> result = authenticationFilter.filter(exchange, filterChain);

        StepVerifier.create(result)
                .verifyComplete();

        verify(filterChain, times(1)).filter(exchange);
    }

    @Test
    void testSecuredEndpointWithoutAuthorizationHeader() {
        MockServerHttpRequest request = MockServerHttpRequest
                .get("/api/bookings")
                .build();
        exchange = MockServerWebExchange.from(request);

        Mono<Void> result = authenticationFilter.filter(exchange, filterChain);

        StepVerifier.create(result)
                .verifyComplete();

        ServerHttpResponse response = exchange.getResponse();
        assert response.getStatusCode() == HttpStatus.UNAUTHORIZED;

        verify(filterChain, never()).filter(any());
    }

    @Test
    void testSecuredEndpointWithInvalidAuthorizationHeader() {
        MockServerHttpRequest request = MockServerHttpRequest
                .get("/api/bookings")
                .header(HttpHeaders.AUTHORIZATION, "InvalidHeader")
                .build();
        exchange = MockServerWebExchange.from(request);

        Mono<Void> result = authenticationFilter.filter(exchange, filterChain);

        StepVerifier.create(result)
                .verifyComplete();

        ServerHttpResponse response = exchange.getResponse();
        assert response.getStatusCode() == HttpStatus.UNAUTHORIZED;

        verify(filterChain, never()).filter(any());
    }

    @Test
    void testSecuredEndpointWithValidToken() {
        String validToken = "valid.jwt.token";

        when(jwtUtil.validateToken(validToken)).thenReturn(true);
        when(jwtUtil.getUserIdFromToken(validToken)).thenReturn(1L);
        when(jwtUtil.getUsernameFromToken(validToken)).thenReturn("testuser@example.com");
        when(jwtUtil.getRoleFromToken(validToken)).thenReturn("CUSTOMER");

        MockServerHttpRequest request = MockServerHttpRequest
                .get("/api/bookings")
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + validToken)
                .build();
        exchange = MockServerWebExchange.from(request);

        Mono<Void> result = authenticationFilter.filter(exchange, filterChain);

        StepVerifier.create(result)
                .verifyComplete();

        verify(jwtUtil, times(1)).validateToken(validToken);
        verify(jwtUtil, times(1)).getUserIdFromToken(validToken);
        verify(jwtUtil, times(1)).getUsernameFromToken(validToken);
        verify(jwtUtil, times(1)).getRoleFromToken(validToken);
        verify(filterChain, times(1)).filter(any());
    }

    @Test
    void testSecuredEndpointWithExpiredToken() {
        String expiredToken = "expired.jwt.token";

        when(jwtUtil.validateToken(expiredToken)).thenReturn(false);

        MockServerHttpRequest request = MockServerHttpRequest
                .get("/api/bookings")
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + expiredToken)
                .build();
        exchange = MockServerWebExchange.from(request);

        Mono<Void> result = authenticationFilter.filter(exchange, filterChain);

        StepVerifier.create(result)
                .verifyComplete();

        ServerHttpResponse response = exchange.getResponse();
        assert response.getStatusCode() == HttpStatus.UNAUTHORIZED;

        verify(jwtUtil, times(1)).validateToken(expiredToken);
        verify(filterChain, never()).filter(any());
    }

    @Test
    void testCatalogEndpointPublicAccess() {
        MockServerHttpRequest request = MockServerHttpRequest
                .get("/api/catalog/movies")
                .build();
        exchange = MockServerWebExchange.from(request);

        Mono<Void> result = authenticationFilter.filter(exchange, filterChain);

        StepVerifier.create(result)
                .verifyComplete();

        verify(filterChain, times(1)).filter(exchange);
        verify(jwtUtil, never()).validateToken(anyString());
    }

    @Test
    void testActuatorHealthEndpointPublicAccess() {
        MockServerHttpRequest request = MockServerHttpRequest
                .get("/actuator/health")
                .build();
        exchange = MockServerWebExchange.from(request);

        Mono<Void> result = authenticationFilter.filter(exchange, filterChain);

        StepVerifier.create(result)
                .verifyComplete();

        verify(filterChain, times(1)).filter(exchange);
        verify(jwtUtil, never()).validateToken(anyString());
    }
}
