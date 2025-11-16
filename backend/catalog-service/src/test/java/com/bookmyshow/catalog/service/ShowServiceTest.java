package com.bookmyshow.catalog.service;

import com.bookmyshow.catalog.dto.CreateShowRequest;
import com.bookmyshow.catalog.entity.Movie;
import com.bookmyshow.catalog.entity.Screen;
import com.bookmyshow.catalog.entity.Show;
import com.bookmyshow.catalog.repository.MovieRepository;
import com.bookmyshow.catalog.repository.ScreenRepository;
import com.bookmyshow.catalog.repository.ShowRepository;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ShowServiceTest {

    @Mock
    private ShowRepository showRepository;

    @Mock
    private MovieRepository movieRepository;

    @Mock
    private ScreenRepository screenRepository;

    @InjectMocks
    private ShowService showService;

    private CreateShowRequest createRequest;
    private Show show;
    private Movie movie;
    private Screen screen;

    @BeforeEach
    void setUp() {
        LocalDateTime startTime = LocalDateTime.of(2024, 1, 15, 18, 0);
        LocalDateTime endTime = LocalDateTime.of(2024, 1, 15, 20, 30);

        createRequest = new CreateShowRequest(
                1L,
                1L,
                startTime,
                endTime,
                new BigDecimal("250.00")
        );

        movie = new Movie();
        movie.setId(1L);
        movie.setTitle("Inception");

        screen = new Screen();
        screen.setId(1L);
        screen.setName("Screen 1");

        show = new Show();
        show.setId(1L);
        show.setMovie(movie);
        show.setScreen(screen);
        show.setStartTime(startTime);
        show.setEndTime(endTime);
        show.setBasePrice(new BigDecimal("250.00"));
    }

    @Test
    void createShow_WhenMovieAndScreenExist_ShouldReturnSavedShow() {
        when(movieRepository.findById(1L)).thenReturn(Optional.of(movie));
        when(screenRepository.findById(1L)).thenReturn(Optional.of(screen));
        when(showRepository.save(any(Show.class))).thenReturn(show);

        Show result = showService.createShow(createRequest);

        assertThat(result).isNotNull();
        assertThat(result.getMovie().getTitle()).isEqualTo("Inception");
        assertThat(result.getBasePrice()).isEqualByComparingTo(new BigDecimal("250.00"));
        verify(showRepository, times(1)).save(any(Show.class));
    }

    @Test
    void createShow_WhenMovieNotFound_ShouldThrowException() {
        when(movieRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> showService.createShow(createRequest))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Movie not found with id: '1'");
    }

    @Test
    void createShow_WhenScreenNotFound_ShouldThrowException() {
        when(movieRepository.findById(1L)).thenReturn(Optional.of(movie));
        when(screenRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> showService.createShow(createRequest))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Screen not found with id: '1'");
    }

    @Test
    void getShowById_WhenShowExists_ShouldReturnShow() {
        when(showRepository.findById(1L)).thenReturn(Optional.of(show));

        Show result = showService.getShowById(1L);

        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
        verify(showRepository, times(1)).findById(1L);
    }

    @Test
    void getShowById_WhenShowNotFound_ShouldThrowException() {
        when(showRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> showService.getShowById(1L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Show not found with id: '1'");
    }

    @Test
    void getShowsByMovie_ShouldReturnShowsForMovie() {
        when(showRepository.findByMovieId(1L)).thenReturn(Arrays.asList(show));

        List<Show> result = showService.getShowsByMovie(1L);

        assertThat(result).isNotNull();
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getMovie().getId()).isEqualTo(1L);
        verify(showRepository, times(1)).findByMovieId(1L);
    }

    @Test
    void getShowsByMovieAndCity_ShouldReturnFilteredShows() {
        when(showRepository.findByMovieIdAndCity(1L, "Mumbai")).thenReturn(Arrays.asList(show));

        List<Show> result = showService.getShowsByMovieAndCity(1L, "Mumbai");

        assertThat(result).isNotNull();
        assertThat(result).hasSize(1);
        verify(showRepository, times(1)).findByMovieIdAndCity(1L, "Mumbai");
    }

    @Test
    void getShowsByDate_ShouldReturnShowsOnDate() {
        LocalDate date = LocalDate.of(2024, 1, 15);
        when(showRepository.findByDate(date)).thenReturn(Arrays.asList(show));

        List<Show> result = showService.getShowsByDate(date);

        assertThat(result).isNotNull();
        assertThat(result).hasSize(1);
        verify(showRepository, times(1)).findByDate(date);
    }

    @Test
    void deleteShow_WhenShowExists_ShouldDeleteShow() {
        when(showRepository.findById(1L)).thenReturn(Optional.of(show));

        showService.deleteShow(1L);

        verify(showRepository, times(1)).findById(1L);
        verify(showRepository, times(1)).delete(show);
    }
}
