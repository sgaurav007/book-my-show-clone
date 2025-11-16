package com.bookmyshow.catalog.repository;

import com.bookmyshow.catalog.entity.Theater;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TheaterRepository extends JpaRepository<Theater, Long> {

    List<Theater> findByCityAndIsActiveTrue(String city);

    List<Theater> findByIsActiveTrue();
}
