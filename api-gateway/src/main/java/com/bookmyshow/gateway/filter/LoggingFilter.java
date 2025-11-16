package com.bookmyshow.gateway.filter;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Component
public class LoggingFilter implements GlobalFilter, Ordered {

    private static final Logger logger = LoggerFactory.getLogger(LoggingFilter.class);
    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        ServerHttpRequest request = exchange.getRequest();

        String timestamp = LocalDateTime.now().format(formatter);
        String method = request.getMethod().toString();
        String path = request.getURI().getPath();
        String queryParams = request.getURI().getQuery();
        String clientIp = getClientIp(request);

        logger.info("[{}] Incoming Request - Method: {}, Path: {}, Query: {}, IP: {}",
                    timestamp, method, path, queryParams != null ? queryParams : "none", clientIp);

        long startTime = System.currentTimeMillis();

        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            ServerHttpResponse response = exchange.getResponse();
            long duration = System.currentTimeMillis() - startTime;

            logger.info("[{}] Outgoing Response - Method: {}, Path: {}, Status: {}, Duration: {}ms",
                        LocalDateTime.now().format(formatter), method, path,
                        response.getStatusCode(), duration);
        }));
    }

    private String getClientIp(ServerHttpRequest request) {
        String ip = request.getHeaders().getFirst("X-Forwarded-For");
        if (ip == null || ip.isEmpty()) {
            ip = request.getHeaders().getFirst("X-Real-IP");
        }
        if (ip == null || ip.isEmpty()) {
            ip = request.getRemoteAddress() != null ?
                  request.getRemoteAddress().getAddress().getHostAddress() : "unknown";
        }
        return ip;
    }

    @Override
    public int getOrder() {
        return Ordered.HIGHEST_PRECEDENCE;
    }
}
