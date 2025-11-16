package com.bookmyshow.catalog.controller;

import com.bookmyshow.catalog.dto.CreateShowRequest;
import com.bookmyshow.catalog.entity.Seat;
import com.bookmyshow.catalog.entity.Show;
import com.bookmyshow.catalog.service.SeatService;
import com.bookmyshow.catalog.service.ShowService;
import com.bookmyshow.common.dto.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/catalog/shows")
@RequiredArgsConstructor
public class ShowController {

    private final ShowService showService;
    private final SeatService seatService;

    @PostMapping
    public ResponseEntity<ApiResponse<Show>> createShow(@Valid @RequestBody CreateShowRequest request) {
        Show show = showService.createShow(request);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.success("Show created successfully", show));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<Show>> getShowById(@PathVariable Long id) {
        Show show = showService.getShowById(id);
        return ResponseEntity.ok(ApiResponse.success(show));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<Show>>> getShows(
            @RequestParam(required = false) Long movieId,
            @RequestParam(required = false) String city,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        List<Show> shows;

        if (movieId != null && city != null && date != null) {
            shows = showService.getShowsByMovieAndCityAndDate(movieId, city, date);
        } else if (movieId != null && city != null) {
            shows = showService.getShowsByMovieAndCity(movieId, city);
        } else if (movieId != null) {
            shows = showService.getShowsByMovie(movieId);
        } else if (date != null) {
            shows = showService.getShowsByDate(date);
        } else {
            shows = List.of();
        }

        return ResponseEntity.ok(ApiResponse.success(shows));
    }

    @GetMapping("/{id}/seats")
    public ResponseEntity<ApiResponse<List<Seat>>> getShowSeats(@PathVariable Long id) {
        Show show = showService.getShowById(id);
        List<Seat> seats = seatService.getSeatsByScreen(show.getScreen().getId());
        return ResponseEntity.ok(ApiResponse.success(seats));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteShow(@PathVariable Long id) {
        showService.deleteShow(id);
        return ResponseEntity.ok(ApiResponse.success("Show deleted successfully", null));
    }
}
