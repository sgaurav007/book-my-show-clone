package com.bookmyshow.payment.repository;

import com.bookmyshow.payment.model.Payment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PaymentRepository extends JpaRepository<Payment, Long> {
    Optional<Payment> findByPaymentReference(String paymentReference);
    Optional<Payment> findByBookingId(Long bookingId);
    boolean existsByBookingId(Long bookingId);
}
