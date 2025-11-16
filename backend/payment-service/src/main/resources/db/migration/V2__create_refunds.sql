CREATE TABLE refunds (
    id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT NOT NULL,
    refund_amount DECIMAL(10, 2) NOT NULL,
    refund_status VARCHAR(50) NOT NULL,
    refund_reference VARCHAR(100) UNIQUE,
    gateway_refund_id VARCHAR(255),
    reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_refund_payment FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE
);

CREATE INDEX idx_refunds_payment_id ON refunds(payment_id);
CREATE INDEX idx_refunds_refund_status ON refunds(refund_status);
