CREATE TABLE screens (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    total_seats INT NOT NULL,
    theater_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (theater_id) REFERENCES theaters(id) ON DELETE CASCADE
);

CREATE INDEX idx_screens_theater_id ON screens(theater_id);
