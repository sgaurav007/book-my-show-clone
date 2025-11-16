package com.bookmyshow.catalog.service;

import com.bookmyshow.catalog.dto.CreateMovieRequest;
import com.bookmyshow.catalog.dto.UpdateMovieRequest;
import com.bookmyshow.catalog.entity.Movie;
import com.bookmyshow.catalog.repository.MovieRepository;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
@RequiredArgsConstructor
public class MovieService {

    private final MovieRepository movieRepository;

    public Movie createMovie(CreateMovieRequest request) {
        Movie movie = new Movie();
        movie.setTitle(request.getTitle());
        movie.setDescription(request.getDescription());
        movie.setDurationMinutes(request.getDurationMinutes());
        movie.setLanguage(request.getLanguage());
        movie.setReleaseDate(request.getReleaseDate());
        movie.setRating(request.getRating());
        movie.setGenre(request.getGenre());
        movie.setPosterUrl(request.getPosterUrl());
        movie.setTrailerUrl(request.getTrailerUrl());
        movie.setIsActive(true);

        return movieRepository.save(movie);
    }

    public Movie getMovieById(Long id) {
        return movieRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Movie", "id", id));
    }

    public Page<Movie> getAllMovies(Pageable pageable) {
        return movieRepository.findAll(pageable);
    }

    public List<Movie> getActiveMovies() {
        return movieRepository.findByIsActiveTrue();
    }

    public Movie updateMovie(Long id, UpdateMovieRequest request) {
        Movie movie = getMovieById(id);

        if (request.getTitle() != null) {
            movie.setTitle(request.getTitle());
        }
        if (request.getDescription() != null) {
            movie.setDescription(request.getDescription());
        }
        if (request.getDurationMinutes() != null) {
            movie.setDurationMinutes(request.getDurationMinutes());
        }
        if (request.getLanguage() != null) {
            movie.setLanguage(request.getLanguage());
        }
        if (request.getReleaseDate() != null) {
            movie.setReleaseDate(request.getReleaseDate());
        }
        if (request.getRating() != null) {
            movie.setRating(request.getRating());
        }
        if (request.getGenre() != null) {
            movie.setGenre(request.getGenre());
        }
        if (request.getPosterUrl() != null) {
            movie.setPosterUrl(request.getPosterUrl());
        }
        if (request.getTrailerUrl() != null) {
            movie.setTrailerUrl(request.getTrailerUrl());
        }
        if (request.getIsActive() != null) {
            movie.setIsActive(request.getIsActive());
        }

        return movieRepository.save(movie);
    }

    public void deleteMovie(Long id) {
        Movie movie = getMovieById(id);
        movieRepository.delete(movie);
    }

    public List<Movie> searchMovies(String query) {
        return movieRepository.searchByTitleOrGenre(query);
    }
}
