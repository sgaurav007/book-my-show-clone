package com.bookmyshow.catalog.entity;

import com.bookmyshow.common.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.List;

@Entity
@Table(name = "movies")
@Data
@EqualsAndHashCode(callSuper = true)
@NoArgsConstructor
@AllArgsConstructor
public class Movie extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Column(name = "duration_minutes", nullable = false)
    private Integer durationMinutes;

    @Column(nullable = false, length = 50)
    private String language;

    @Column(name = "release_date", nullable = false)
    private LocalDate releaseDate;

    @Column(length = 10)
    private String rating;

    @ElementCollection
    @CollectionTable(name = "movie_genres", joinColumns = @JoinColumn(name = "movie_id"))
    @Column(name = "genre")
    private List<String> genre;

    @Column(name = "poster_url", length = 512)
    private String posterUrl;

    @Column(name = "trailer_url", length = 512)
    private String trailerUrl;

    @Column(name = "is_active")
    private Boolean isActive = true;
}
