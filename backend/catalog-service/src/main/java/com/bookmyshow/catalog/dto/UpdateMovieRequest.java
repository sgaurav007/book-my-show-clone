package com.bookmyshow.catalog.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateMovieRequest {
    private String title;
    private String description;
    private Integer durationMinutes;
    private String language;
    private LocalDate releaseDate;
    private String rating;
    private List<String> genre;
    private String posterUrl;
    private String trailerUrl;
    private Boolean isActive;
}
