package com.bookmyshow.catalog.controller;

import com.bookmyshow.catalog.dto.CreateTheaterRequest;
import com.bookmyshow.catalog.entity.Theater;
import com.bookmyshow.catalog.service.TheaterService;
import com.bookmyshow.common.dto.ApiResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/catalog/theaters")
@RequiredArgsConstructor
public class TheaterController {

    private final TheaterService theaterService;

    @PostMapping
    public ResponseEntity<ApiResponse<Theater>> createTheater(@Valid @RequestBody CreateTheaterRequest request) {
        Theater theater = theaterService.createTheater(request);
        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(ApiResponse.success("Theater created successfully", theater));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ApiResponse<Theater>> getTheaterById(@PathVariable Long id) {
        Theater theater = theaterService.getTheaterById(id);
        return ResponseEntity.ok(ApiResponse.success(theater));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<Theater>>> getTheaters(@RequestParam(required = false) String city) {
        List<Theater> theaters;
        if (city != null && !city.isEmpty()) {
            theaters = theaterService.getTheatersByCity(city);
        } else {
            theaters = theaterService.getAllTheaters();
        }
        return ResponseEntity.ok(ApiResponse.success(theaters));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<ApiResponse<Void>> deleteTheater(@PathVariable Long id) {
        theaterService.deleteTheater(id);
        return ResponseEntity.ok(ApiResponse.success("Theater deleted successfully", null));
    }
}
