package com.bookmyshow.catalog.service;

import com.bookmyshow.catalog.dto.CreateTheaterRequest;
import com.bookmyshow.catalog.entity.Theater;
import com.bookmyshow.catalog.repository.TheaterRepository;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class TheaterServiceTest {

    @Mock
    private TheaterRepository theaterRepository;

    @InjectMocks
    private TheaterService theaterService;

    private CreateTheaterRequest createRequest;
    private Theater theater;

    @BeforeEach
    void setUp() {
        createRequest = new CreateTheaterRequest(
                "PVR Cinemas",
                "Mumbai",
                "123 Main St, Mumbai",
                19.0760,
                72.8777
        );

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
    void createTheater_ShouldReturnSavedTheater() {
        when(theaterRepository.save(any(Theater.class))).thenReturn(theater);

        Theater result = theaterService.createTheater(createRequest);

        assertThat(result).isNotNull();
        assertThat(result.getName()).isEqualTo("PVR Cinemas");
        assertThat(result.getCity()).isEqualTo("Mumbai");
        verify(theaterRepository, times(1)).save(any(Theater.class));
    }

    @Test
    void getTheaterById_WhenTheaterExists_ShouldReturnTheater() {
        when(theaterRepository.findById(1L)).thenReturn(Optional.of(theater));

        Theater result = theaterService.getTheaterById(1L);

        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getName()).isEqualTo("PVR Cinemas");
        verify(theaterRepository, times(1)).findById(1L);
    }

    @Test
    void getTheaterById_WhenTheaterNotFound_ShouldThrowException() {
        when(theaterRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> theaterService.getTheaterById(1L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("Theater not found with id: '1'");
    }

    @Test
    void getAllTheaters_ShouldReturnListOfTheaters() {
        when(theaterRepository.findAll()).thenReturn(Arrays.asList(theater));

        List<Theater> result = theaterService.getAllTheaters();

        assertThat(result).isNotNull();
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getName()).isEqualTo("PVR Cinemas");
        verify(theaterRepository, times(1)).findAll();
    }

    @Test
    void getTheatersByCity_ShouldReturnTheatersInCity() {
        when(theaterRepository.findByCityAndIsActiveTrue("Mumbai")).thenReturn(Arrays.asList(theater));

        List<Theater> result = theaterService.getTheatersByCity("Mumbai");

        assertThat(result).isNotNull();
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getCity()).isEqualTo("Mumbai");
        verify(theaterRepository, times(1)).findByCityAndIsActiveTrue("Mumbai");
    }

    @Test
    void deleteTheater_WhenTheaterExists_ShouldDeleteTheater() {
        when(theaterRepository.findById(1L)).thenReturn(Optional.of(theater));

        theaterService.deleteTheater(1L);

        verify(theaterRepository, times(1)).findById(1L);
        verify(theaterRepository, times(1)).delete(theater);
    }

    @Test
    void deleteTheater_WhenTheaterNotFound_ShouldThrowException() {
        when(theaterRepository.findById(1L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> theaterService.deleteTheater(1L))
                .isInstanceOf(ResourceNotFoundException.class);
    }
}
