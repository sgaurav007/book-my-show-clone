package com.bookmyshow.booking.model;

import com.bookmyshow.common.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Entity
@Table(name = "booking_seats")
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = false)
public class BookingSeat extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "booking_id", nullable = false)
    private Booking booking;

    @Column(name = "seat_id", nullable = false)
    private Long seatId;

    @Column(name = "seat_number", nullable = false)
    private String seatNumber;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;
}
