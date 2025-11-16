package com.bookmyshow.catalog.service;

import com.bookmyshow.catalog.dto.CreateMovieRequest;
import com.bookmyshow.catalog.dto.UpdateMovieRequest;
import com.bookmyshow.catalog.entity.Movie;
import com.bookmyshow.catalog.repository.MovieRepository;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MovieServiceTest {

    @Mock
    private MovieRepository movieRepository;

    @InjectMocks
    private MovieService movieService;

    private CreateMovieRequest createRequest;
    private Movie movie;

    @BeforeEach
    void setUp() {
        createRequest = new CreateMovieRequest(
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
    void createMovie_ShouldReturnSavedMovie() {
        when(movieRepository.save(any(Movie.class))).thenReturn(movie);

        Movie result = movieService.createMovie(createRequest);

        assertThat(result).isNotNull();
        assertThat(result.getTitle()).isEqualTo("Inception");
        assertThat(result.getLanguage()).isEqualTo("English");
        verify(movieRepository, times(1)).save(any(Movie.class));
    }

    @Test
    void getMovieById_WhenMovieExists_ShouldReturnMovie() {
        when(movieRepository.findById(1L)).thenReturn(Optional.of(movie));

        Movie result = movieService.getMovieById(1L);

        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getTitle()).isEqualTo("Inception");
        verify(movieRepository, times(1)).findById(1L);
    }

    @Test
    void getMovieById_WhenMovieNotFound_ShouldThrowException() {
        when(movieRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> movieService.getMovieById(1L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Movie not found with id: '1'");
    }

    @Test
    void getAllMovies_ShouldReturnPageOfMovies() {
        Pageable pageable = PageRequest.of(0, 10);
        Page<Movie> moviePage = new PageImpl<>(Arrays.asList(movie));
        when(movieRepository.findAll(pageable)).thenReturn(moviePage);

        Page<Movie> result = movieService.getAllMovies(pageable);

        assertThat(result).isNotNull();
        assertThat(result.getContent()).hasSize(1);
        assertThat(result.getContent().get(0).getTitle()).isEqualTo("Inception");
        verify(movieRepository, times(1)).findAll(pageable);
    }

    @Test
    void updateMovie_WhenMovieExists_ShouldReturnUpdatedMovie() {
        UpdateMovieRequest updateRequest = new UpdateMovieRequest();
        updateRequest.setTitle("Inception Updated");
        updateRequest.setIsActive(false);

        when(movieRepository.findById(1L)).thenReturn(Optional.of(movie));
        when(movieRepository.save(any(Movie.class))).thenReturn(movie);

        Movie result = movieService.updateMovie(1L, updateRequest);

        assertThat(result).isNotNull();
        verify(movieRepository, times(1)).findById(1L);
        verify(movieRepository, times(1)).save(any(Movie.class));
    }

    @Test
    void updateMovie_WhenMovieNotFound_ShouldThrowException() {
        UpdateMovieRequest updateRequest = new UpdateMovieRequest();
        when(movieRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> movieService.updateMovie(1L, updateRequest))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    void deleteMovie_WhenMovieExists_ShouldDeleteMovie() {
        when(movieRepository.findById(1L)).thenReturn(Optional.of(movie));

        movieService.deleteMovie(1L);

        verify(movieRepository, times(1)).findById(1L);
        verify(movieRepository, times(1)).delete(movie);
    }

    @Test
    void searchMovies_ShouldReturnMatchingMovies() {
        when(movieRepository.searchByTitleOrGenre("Inception")).thenReturn(Arrays.asList(movie));

        List<Movie> result = movieService.searchMovies("Inception");

        assertThat(result).isNotNull();
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getTitle()).isEqualTo("Inception");
        verify(movieRepository, times(1)).searchByTitleOrGenre("Inception");
    }

    @Test
    void getActiveMovies_ShouldReturnOnlyActiveMovies() {
        when(movieRepository.findByIsActiveTrue()).thenReturn(Arrays.asList(movie));

        List<Movie> result = movieService.getActiveMovies();

        assertThat(result).isNotNull();
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getIsActive()).isTrue();
        verify(movieRepository, times(1)).findByIsActiveTrue();
    }
}
