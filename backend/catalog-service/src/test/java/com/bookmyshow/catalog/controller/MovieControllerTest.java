package com.bookmyshow.catalog.controller;

import com.bookmyshow.catalog.dto.CreateMovieRequest;
import com.bookmyshow.catalog.entity.Movie;
import com.bookmyshow.catalog.service.MovieService;
import io.restassured.http.ContentType;
import io.restassured.module.mockmvc.RestAssuredMockMvc;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

import static io.restassured.module.mockmvc.RestAssuredMockMvc.given;
import static org.hamcrest.Matchers.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@WebMvcTest(MovieController.class)
class MovieControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private MovieService movieService;

    private Movie movie;

    @BeforeEach
    void setUp() {
        RestAssuredMockMvc.mockMvc(mockMvc);

        movie = new Movie();
        movie.setId(1L);
        movie.setTitle("Inception");
        movie.setDescription("A mind-bending thriller");
        movie.setDurationMinutes(148);
        movie.setLanguage("English");
        movie.setReleaseDate(LocalDate.of(2010, 7, 16));
        movie.setRating("PG-13");
        movie.setGenre(Arrays.asList("Action", "Sci-Fi"));
        movie.setPosterUrl("http://poster.url");
        movie.setTrailerUrl("http://trailer.url");
        movie.setIsActive(true);
    }

    @Test
    void createMovie_ShouldReturnCreatedMovie() {
        CreateMovieRequest request = new CreateMovieRequest(
                "Inception",
                "A mind-bending thriller",
                148,
                "English",
                LocalDate.of(2010, 7, 16),
                "PG-13",
                Arrays.asList("Action", "Sci-Fi"),
                "http://poster.url",
                "http://trailer.url"
        );

        when(movieService.createMovie(any(CreateMovieRequest.class))).thenReturn(movie);

        given()
                .contentType(ContentType.JSON)
                .body(request)
        .when()
                .post("/api/catalog/movies")
        .then()
                .statusCode(201)
                .body("data.title", equalTo("Inception"))
                .body("data.language", equalTo("English"))
                .body("success", equalTo(true));
    }

    @Test
    void getMovieById_WhenMovieExists_ShouldReturnMovie() {
        when(movieService.getMovieById(1L)).thenReturn(movie);

        given()
        .when()
                .get("/api/catalog/movies/1")
        .then()
                .statusCode(200)
                .body("data.id", equalTo(1))
                .body("data.title", equalTo("Inception"))
                .body("success", equalTo(true));
    }

    @Test
    void getAllMovies_ShouldReturnPageOfMovies() {
        when(movieService.getAllMovies(any(PageRequest.class)))
                .thenReturn(new PageImpl<>(Arrays.asList(movie)));

        given()
                .param("page", 0)
                .param("size", 10)
        .when()
                .get("/api/catalog/movies")
        .then()
                .statusCode(200)
                .body("data.content", hasSize(1))
                .body("data.content[0].title", equalTo("Inception"))
                .body("success", equalTo(true));
    }

    @Test
    void searchMovies_ShouldReturnMatchingMovies() {
        when(movieService.searchMovies("Inception")).thenReturn(Arrays.asList(movie));

        given()
                .param("q", "Inception")
        .when()
                .get("/api/catalog/movies/search")
        .then()
                .statusCode(200)
                .body("data", hasSize(1))
                .body("data[0].title", equalTo("Inception"))
                .body("success", equalTo(true));
    }

    @Test
    void deleteMovie_ShouldReturnNoContent() {
        given()
        .when()
                .delete("/api/catalog/movies/1")
        .then()
                .statusCode(200)
                .body("success", equalTo(true));
    }
}
