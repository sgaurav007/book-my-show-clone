package com.bookmyshow.catalog.service;

import com.bookmyshow.catalog.entity.Seat;
import com.bookmyshow.catalog.repository.SeatRepository;
import com.bookmyshow.common.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
@RequiredArgsConstructor
public class SeatService {

    private final SeatRepository seatRepository;

    public Seat getSeatById(Long id) {
        return seatRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Seat", "id", id));
    }

    public List<Seat> getSeatsByScreen(Long screenId) {
        return seatRepository.findByScreenIdOrderByRowLabelAscSeatNumberAsc(screenId);
    }
}
