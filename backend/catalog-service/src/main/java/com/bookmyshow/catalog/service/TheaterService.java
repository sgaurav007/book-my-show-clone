package com.bookmyshow.catalog.service;

import com.bookmyshow.catalog.dto.CreateTheaterRequest;
import com.bookmyshow.catalog.entity.Theater;
import com.bookmyshow.catalog.repository.TheaterRepository;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
@RequiredArgsConstructor
public class TheaterService {

    private final TheaterRepository theaterRepository;

    public Theater createTheater(CreateTheaterRequest request) {
        Theater theater = new Theater();
        theater.setName(request.getName());
        theater.setCity(request.getCity());
        theater.setAddress(request.getAddress());
        theater.setLatitude(request.getLatitude());
        theater.setLongitude(request.getLongitude());
        theater.setIsActive(true);

        return theaterRepository.save(theater);
    }

    public Theater getTheaterById(Long id) {
        return theaterRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Theater", "id", id));
    }

    public List<Theater> getAllTheaters() {
        return theaterRepository.findAll();
    }

    public List<Theater> getTheatersByCity(String city) {
        return theaterRepository.findByCityAndIsActiveTrue(city);
    }

    public void deleteTheater(Long id) {
        Theater theater = getTheaterById(id);
        theaterRepository.delete(theater);
    }
}
