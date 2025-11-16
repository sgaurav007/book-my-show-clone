package com.bookmyshow.catalog.repository;

import com.bookmyshow.catalog.entity.Movie;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MovieRepository extends JpaRepository<Movie, Long> {

    List<Movie> findByIsActiveTrue();

    @Query("SELECT m FROM Movie m WHERE LOWER(m.title) LIKE LOWER(CONCAT('%', :searchTerm, '%')) " +
           "OR EXISTS (SELECT g FROM m.genre g WHERE LOWER(g) LIKE LOWER(CONCAT('%', :searchTerm, '%')))")
    List<Movie> searchByTitleOrGenre(@Param("searchTerm") String searchTerm);
}
