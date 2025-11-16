CREATE TABLE seats (
    id BIGSERIAL PRIMARY KEY,
    row_label VARCHAR(10) NOT NULL,
    seat_number INT NOT NULL,
    seat_type VARCHAR(20) NOT NULL,
    screen_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (screen_id) REFERENCES screens(id) ON DELETE CASCADE,
    UNIQUE (screen_id, row_label, seat_number)
);

CREATE INDEX idx_seats_screen_id ON seats(screen_id);
CREATE INDEX idx_seats_row_label ON seats(row_label);
