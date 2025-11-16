package com.bookmyshow.payment.repository;

import com.bookmyshow.payment.model.Refund;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface RefundRepository extends JpaRepository<Refund, Long> {
    List<Refund> findByPaymentId(Long paymentId);

    @Query("SELECT COALESCE(SUM(r.refundAmount), 0) FROM Refund r WHERE r.paymentId = :paymentId AND r.refundStatus = 'SUCCESS'")
    BigDecimal getTotalRefundedAmount(Long paymentId);
}
