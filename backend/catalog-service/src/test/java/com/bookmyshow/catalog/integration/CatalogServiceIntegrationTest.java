package com.bookmyshow.catalog.integration;

import com.bookmyshow.catalog.dto.CreateMovieRequest;
import com.bookmyshow.catalog.dto.CreateTheaterRequest;
import com.bookmyshow.catalog.entity.Movie;
import com.bookmyshow.catalog.entity.Theater;
import com.bookmyshow.catalog.repository.MovieRepository;
import com.bookmyshow.catalog.repository.TheaterRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Testcontainers
class CatalogServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("catalog_test_db")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private MovieRepository movieRepository;

    @Autowired
    private TheaterRepository theaterRepository;

    @Test
    void createMovie_ShouldPersistToDatabase() throws Exception {
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

        mockMvc.perform(post("/api/catalog/movies")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.title").value("Inception"))
                .andExpect(jsonPath("$.data.language").value("English"));

        List<Movie> movies = movieRepository.findAll();
        assertThat(movies).hasSize(1);
        assertThat(movies.get(0).getTitle()).isEqualTo("Inception");
    }

    @Test
    void createTheater_ShouldPersistToDatabase() throws Exception {
        CreateTheaterRequest request = new CreateTheaterRequest(
                "PVR Cinemas",
                "Mumbai",
                "123 Main St, Mumbai",
                19.0760,
                72.8777
        );

        mockMvc.perform(post("/api/catalog/theaters")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.name").value("PVR Cinemas"))
                .andExpect(jsonPath("$.data.city").value("Mumbai"));

        List<Theater> theaters = theaterRepository.findAll();
        assertThat(theaters).hasSize(1);
        assertThat(theaters.get(0).getName()).isEqualTo("PVR Cinemas");
    }

    @Test
    void getTheatersByCity_ShouldReturnFilteredTheaters() throws Exception {
        Theater theater = new Theater();
        theater.setName("PVR Cinemas");
        theater.setCity("Mumbai");
        theater.setAddress("123 Main St");
        theater.setIsActive(true);
        theaterRepository.save(theater);

        mockMvc.perform(get("/api/catalog/theaters")
                        .param("city", "Mumbai"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data").isArray())
                .andExpect(jsonPath("$.data[0].city").value("Mumbai"));
    }
}
