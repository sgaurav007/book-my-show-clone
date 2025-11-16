CREATE TABLE payments (
    id BIGSERIAL PRIMARY KEY,
    payment_reference VARCHAR(100) UNIQUE NOT NULL,
    booking_id BIGINT UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) NOT NULL,
    gateway_transaction_id VARCHAR(255),
    gateway_name VARCHAR(50),
    failure_reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_booking_id ON payments(booking_id);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_payment_status ON payments(payment_status);
CREATE INDEX idx_payments_payment_reference ON payments(payment_reference);
