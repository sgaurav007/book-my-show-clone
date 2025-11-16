CREATE TABLE bookings (
    id BIGSERIAL PRIMARY KEY,
    booking_reference VARCHAR(100) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    show_id BIGINT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    booking_status VARCHAR(50) NOT NULL,
    payment_id BIGINT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_booking_reference ON bookings(booking_reference);
CREATE INDEX idx_user_id ON bookings(user_id);
CREATE INDEX idx_show_id ON bookings(show_id);
CREATE INDEX idx_booking_status ON bookings(booking_status);
CREATE INDEX idx_expires_at ON bookings(expires_at);
