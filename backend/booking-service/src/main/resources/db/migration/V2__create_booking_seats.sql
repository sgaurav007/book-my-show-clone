CREATE TABLE booking_seats (
    id BIGSERIAL PRIMARY KEY,
    booking_id BIGINT NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    seat_id BIGINT NOT NULL,
    seat_number VARCHAR(20) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_booking_id ON booking_seats(booking_id);
CREATE INDEX idx_seat_id ON booking_seats(seat_id);
CREATE UNIQUE INDEX idx_booking_seat_unique ON booking_seats(booking_id, seat_id);
