package com.bookmyshow.catalog.controller;

import com.bookmyshow.catalog.dto.CreateTheaterRequest;
import com.bookmyshow.catalog.entity.Theater;
import com.bookmyshow.catalog.service.TheaterService;
import io.restassured.http.ContentType;
import io.restassured.module.mockmvc.RestAssuredMockMvc;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Arrays;

import static io.restassured.module.mockmvc.RestAssuredMockMvc.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@WebMvcTest(TheaterController.class)
class TheaterControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private TheaterService theaterService;

    private Theater theater;

    @BeforeEach
    void setUp() {
        RestAssuredMockMvc.mockMvc(mockMvc);

        theater = new Theater();
        theater.setId(1L);
        theater.setName("PVR Cinemas");
        theater.setCity("Mumbai");
        theater.setAddress("123 Main St, Mumbai");
        theater.setLatitude(19.0760);
        theater.setLongitude(72.8777);
        theater.setIsActive(true);
    }

    @Test
    void createTheater_ShouldReturnCreatedTheater() {
        CreateTheaterRequest request = new CreateTheaterRequest(
                "PVR Cinemas",
                "Mumbai",
                "123 Main St, Mumbai",
                19.0760,
                72.8777
        );

        when(theaterService.createTheater(any(CreateTheaterRequest.class))).thenReturn(theater);

        given()
                .contentType(ContentType.JSON)
                .body(request)
        .when()
                .post("/api/catalog/theaters")
        .then()
                .statusCode(201)
                .body("data.name", equalTo("PVR Cinemas"))
                .body("data.city", equalTo("Mumbai"))
                .body("success", equalTo(true));
    }

    @Test
    void getTheatersByCity_ShouldReturnTheatersInCity() {
        when(theaterService.getTheatersByCity("Mumbai")).thenReturn(Arrays.asList(theater));

        given()
                .param("city", "Mumbai")
        .when()
                .get("/api/catalog/theaters")
        .then()
                .statusCode(200)
                .body("data", hasSize(1))
                .body("data[0].city", equalTo("Mumbai"))
                .body("success", equalTo(true));
    }
}
