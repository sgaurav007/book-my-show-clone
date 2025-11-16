package com.bookmyshow.catalog.repository;

import com.bookmyshow.catalog.entity.Show;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface ShowRepository extends JpaRepository<Show, Long> {

    List<Show> findByMovieId(Long movieId);

    @Query("SELECT s FROM Show s WHERE s.movie.id = :movieId AND s.screen.theater.city = :city")
    List<Show> findByMovieIdAndCity(@Param("movieId") Long movieId, @Param("city") String city);

    @Query("SELECT s FROM Show s WHERE DATE(s.startTime) = :date")
    List<Show> findByDate(@Param("date") LocalDate date);

    @Query("SELECT s FROM Show s WHERE s.movie.id = :movieId AND s.screen.theater.city = :city AND DATE(s.startTime) = :date")
    List<Show> findByMovieIdAndCityAndDate(@Param("movieId") Long movieId, @Param("city") String city, @Param("date") LocalDate date);
}
