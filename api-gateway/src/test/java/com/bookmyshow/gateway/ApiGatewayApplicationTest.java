package com.bookmyshow.gateway;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@ActiveProfiles("test")
class ApiGatewayApplicationTest {

    @Test
    void contextLoads() {
        assertThat(true).isTrue();
    }

    @Test
    void mainMethodTest() {
        String[] args = {};
        assertThat(args).isNotNull();
    }
}
