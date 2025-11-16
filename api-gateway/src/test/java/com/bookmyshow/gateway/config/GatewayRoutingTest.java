package com.bookmyshow.gateway.config;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.cloud.gateway.route.Route;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.test.context.ActiveProfiles;
import reactor.core.publisher.Flux;
import reactor.test.StepVerifier;

import java.util.List;
import java.util.stream.Collectors;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@ActiveProfiles("test")
class GatewayRoutingTest {

    @Autowired
    private RouteLocator routeLocator;

    @Test
    void testRouteLocatorIsNotNull() {
        assertThat(routeLocator).isNotNull();
    }

    @Test
    void testUserServiceRouteExists() {
        Flux<Route> routes = routeLocator.getRoutes();

        StepVerifier.create(routes)
                .expectNextMatches(route -> route.getId().equals("user-service"))
                .thenCancel()
                .verify();
    }

    @Test
    void testCatalogServiceRouteExists() {
        Flux<Route> routes = routeLocator.getRoutes();

        List<Route> routeList = routes.collectList().block();
        assertThat(routeList).isNotNull();

        boolean catalogRouteExists = routeList.stream()
                .anyMatch(route -> route.getId().equals("catalog-service"));

        assertThat(catalogRouteExists).isTrue();
    }

    @Test
    void testBookingServiceRouteExists() {
        Flux<Route> routes = routeLocator.getRoutes();

        List<Route> routeList = routes.collectList().block();
        assertThat(routeList).isNotNull();

        boolean bookingRouteExists = routeList.stream()
                .anyMatch(route -> route.getId().equals("booking-service"));

        assertThat(bookingRouteExists).isTrue();
    }

    @Test
    void testPaymentServiceRouteExists() {
        Flux<Route> routes = routeLocator.getRoutes();

        List<Route> routeList = routes.collectList().block();
        assertThat(routeList).isNotNull();

        boolean paymentRouteExists = routeList.stream()
                .anyMatch(route -> route.getId().equals("payment-service"));

        assertThat(paymentRouteExists).isTrue();
    }

    @Test
    void testAllRequiredRoutesExist() {
        Flux<Route> routes = routeLocator.getRoutes();

        List<String> routeIds = routes.map(Route::getId).collectList().block();
        assertThat(routeIds).isNotNull();

        assertThat(routeIds).contains("user-service", "catalog-service", "booking-service", "payment-service");
    }

    @Test
    void testUserServiceRouteHasCorrectPath() {
        Flux<Route> routes = routeLocator.getRoutes();

        List<Route> routeList = routes.collectList().block();
        assertThat(routeList).isNotNull();

        Route userRoute = routeList.stream()
                .filter(route -> route.getId().equals("user-service"))
                .findFirst()
                .orElse(null);

        assertThat(userRoute).isNotNull();
        assertThat(userRoute.getPredicate().toString()).contains("/api/users/**");
    }
}
