package com.bookmyshow.catalog.controller;

import com.bookmyshow.catalog.dto.CreateShowRequest;
import com.bookmyshow.catalog.entity.Movie;
import com.bookmyshow.catalog.entity.Screen;
import com.bookmyshow.catalog.entity.Seat;
import com.bookmyshow.catalog.entity.Show;
import com.bookmyshow.catalog.service.SeatService;
import com.bookmyshow.catalog.service.ShowService;
import io.restassured.http.ContentType;
import io.restassured.module.mockmvc.RestAssuredMockMvc;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Arrays;

import static io.restassured.module.mockmvc.RestAssuredMockMvc.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@WebMvcTest(ShowController.class)
class ShowControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ShowService showService;

    @MockBean
    private SeatService seatService;

    private Show show;
    private Seat seat;

    @BeforeEach
    void setUp() {
        RestAssuredMockMvc.mockMvc(mockMvc);

        Movie movie = new Movie();
        movie.setId(1L);
        movie.setTitle("Inception");

        Screen screen = new Screen();
        screen.setId(1L);
        screen.setName("Screen 1");

        show = new Show();
        show.setId(1L);
        show.setMovie(movie);
        show.setScreen(screen);
        show.setStartTime(LocalDateTime.of(2024, 1, 15, 18, 0));
        show.setEndTime(LocalDateTime.of(2024, 1, 15, 20, 30));
        show.setBasePrice(new BigDecimal("250.00"));

        seat = new Seat();
        seat.setId(1L);
        seat.setRowLabel("A");
        seat.setSeatNumber(1);
        seat.setSeatType(Seat.SeatType.REGULAR);
        seat.setScreen(screen);
    }

    @Test
    void createShow_ShouldReturnCreatedShow() {
        CreateShowRequest request = new CreateShowRequest(
                1L,
                1L,
                LocalDateTime.of(2024, 1, 15, 18, 0),
                LocalDateTime.of(2024, 1, 15, 20, 30),
                new BigDecimal("250.00")
        );

        when(showService.createShow(any(CreateShowRequest.class))).thenReturn(show);

        given()
                .contentType(ContentType.JSON)
                .body(request)
        .when()
                .post("/api/catalog/shows")
        .then()
                .statusCode(201)
                .body("data.movie.title", equalTo("Inception"))
                .body("success", equalTo(true));
    }

    @Test
    void getShows_WithMovieIdAndCity_ShouldReturnFilteredShows() {
        when(showService.getShowsByMovieAndCity(1L, "Mumbai")).thenReturn(Arrays.asList(show));

        given()
                .param("movieId", 1L)
                .param("city", "Mumbai")
        .when()
                .get("/api/catalog/shows")
        .then()
                .statusCode(200)
                .body("data", hasSize(1))
                .body("success", equalTo(true));
    }

    @Test
    void getShowSeats_ShouldReturnSeatsForShow() {
        when(showService.getShowById(1L)).thenReturn(show);
        when(seatService.getSeatsByScreen(1L)).thenReturn(Arrays.asList(seat));

        given()
        .when()
                .get("/api/catalog/shows/1/seats")
        .then()
                .statusCode(200)
                .body("data", hasSize(1))
                .body("data[0].rowLabel", equalTo("A"))
                .body("success", equalTo(true));
    }
}
