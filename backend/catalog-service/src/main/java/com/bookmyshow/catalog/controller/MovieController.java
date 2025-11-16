package com.bookmyshow.catalog.controller;

import com.bookmyshow.catalog.dto.CreateMovieRequest;
import com.bookmyshow.catalog.dto.UpdateMovieRequest;
import com.bookmyshow.catalog.entity.Movie;
import com.bookmyshow.catalog.service.MovieService;
import com.bookmyshow.common.dto.ApiResponse;
import com.bookmyshow.common.dto.PageResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/catalog/movies")
@RequiredArgsConstructor
public class MovieController {

    private final MovieService movieService;

    @PostMapping
    public ResponseEntity<ApiResponse<Movie>> createMovie(@Valid @RequestBody CreateMovieRequest request) {
        Movie movie = movieService.createMovie(request);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.success("Movie created successfully", movie));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<Movie>> getMovieById(@PathVariable Long id) {
        Movie movie = movieService.getMovieById(id);
        return ResponseEntity.ok(ApiResponse.success(movie));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<PageResponse<Movie>>> getAllMovies(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size
    ) {
        Page<Movie> moviePage = movieService.getAllMovies(PageRequest.of(page, size));
        PageResponse<Movie> pageResponse = new PageResponse<>(
                moviePage.getContent(),
                moviePage.getNumber(),
                moviePage.getSize(),
                moviePage.getTotalElements(),
                moviePage.getTotalPages(),
                moviePage.isLast()
        );
        return ResponseEntity.ok(ApiResponse.success(pageResponse));
    }

    @GetMapping("/search")
    public ResponseEntity<ApiResponse<List<Movie>>> searchMovies(@RequestParam String q) {
        List<Movie> movies = movieService.searchMovies(q);
        return ResponseEntity.ok(ApiResponse.success(movies));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ApiResponse<Movie>> updateMovie(
            @PathVariable Long id,
            @RequestBody UpdateMovieRequest request
    ) {
        Movie movie = movieService.updateMovie(id, request);
        return ResponseEntity.ok(ApiResponse.success("Movie updated successfully", movie));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteMovie(@PathVariable Long id) {
        movieService.deleteMovie(id);
        return ResponseEntity.ok(ApiResponse.success("Movie deleted successfully", null));
    }
}
