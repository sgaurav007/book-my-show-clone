package com.bookmyshow.gateway.filter;

import com.bookmyshow.gateway.util.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.gateway.filter.GatewayFilter;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.http.HttpStatus;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.function.Predicate;

@Component
public class AuthenticationFilter implements GatewayFilter {

    @Autowired
    private JwtUtil jwtUtil;

    private static final List<String> OPEN_API_ENDPOINTS = List.of(
            "/api/users/register",
            "/api/users/login",
            "/api/users/refresh-token",
            "/api/catalog/movies",
            "/api/catalog/theaters",
            "/api/catalog/shows",
            "/actuator/health"
    );

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();

        if (isSecured.test(request)) {
            if (!request.getHeaders().containsKey("Authorization")) {
                return onError(exchange, "Missing authorization header", HttpStatus.UNAUTHORIZED);
            }

            String authHeader = request.getHeaders().getFirst("Authorization");
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                return onError(exchange, "Invalid authorization header", HttpStatus.UNAUTHORIZED);
            }

            String token = authHeader.substring(7);

            try {
                if (!jwtUtil.validateToken(token)) {
                    return onError(exchange, "Invalid or expired token", HttpStatus.UNAUTHORIZED);
                }

                String userId = jwtUtil.getUserIdFromToken(token).toString();
                String username = jwtUtil.getUsernameFromToken(token);
                String role = jwtUtil.getRoleFromToken(token);

                exchange.getRequest()
                        .mutate()
                        .header("X-User-Id", userId)
                        .header("X-Username", username)
                        .header("X-User-Role", role)
                        .build();

            } catch (Exception e) {
                return onError(exchange, "Token validation failed: " + e.getMessage(), HttpStatus.UNAUTHORIZED);
            }
        }

        return chain.filter(exchange);
    }

    private final Predicate<ServerHttpRequest> isSecured = request -> {
        String path = request.getURI().getPath();
        return OPEN_API_ENDPOINTS.stream().noneMatch(path::startsWith);
    };

    private Mono<Void> onError(ServerWebExchange exchange, String err, HttpStatus httpStatus) {
        ServerHttpResponse response = exchange.getResponse();
        response.setStatusCode(httpStatus);
        return response.setComplete();
    }
}
