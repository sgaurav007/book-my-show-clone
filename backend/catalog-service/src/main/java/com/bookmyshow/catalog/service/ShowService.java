package com.bookmyshow.catalog.service;

import com.bookmyshow.catalog.dto.CreateShowRequest;
import com.bookmyshow.catalog.entity.Movie;
import com.bookmyshow.catalog.entity.Screen;
import com.bookmyshow.catalog.entity.Show;
import com.bookmyshow.catalog.repository.MovieRepository;
import com.bookmyshow.catalog.repository.ScreenRepository;
import com.bookmyshow.catalog.repository.ShowRepository;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;

@Service
@Transactional
@RequiredArgsConstructor
public class ShowService {

    private final ShowRepository showRepository;
    private final MovieRepository movieRepository;
    private final ScreenRepository screenRepository;

    public Show createShow(CreateShowRequest request) {
        Movie movie = movieRepository.findById(request.getMovieId())
                .orElseThrow(() -> new ResourceNotFoundException("Movie", "id", request.getMovieId()));

        Screen screen = screenRepository.findById(request.getScreenId())
                .orElseThrow(() -> new ResourceNotFoundException("Screen", "id", request.getScreenId()));

        Show show = new Show();
        show.setMovie(movie);
        show.setScreen(screen);
        show.setStartTime(request.getStartTime());
        show.setEndTime(request.getEndTime());
        show.setBasePrice(request.getBasePrice());

        return showRepository.save(show);
    }

    public Show getShowById(Long id) {
        return showRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Show", "id", id));
    }

    public List<Show> getShowsByMovie(Long movieId) {
        return showRepository.findByMovieId(movieId);
    }

    public List<Show> getShowsByMovieAndCity(Long movieId, String city) {
        return showRepository.findByMovieIdAndCity(movieId, city);
    }

    public List<Show> getShowsByDate(LocalDate date) {
        return showRepository.findByDate(date);
    }

    public List<Show> getShowsByMovieAndCityAndDate(Long movieId, String city, LocalDate date) {
        return showRepository.findByMovieIdAndCityAndDate(movieId, city, date);
    }

    public void deleteShow(Long id) {
        Show show = getShowById(id);
        showRepository.delete(show);
    }
}
