CREATE TABLE shows (
    id BIGSERIAL PRIMARY KEY,
    movie_id BIGINT NOT NULL,
    screen_id BIGINT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (screen_id) REFERENCES screens(id) ON DELETE CASCADE
);

CREATE INDEX idx_shows_movie_id ON shows(movie_id);
CREATE INDEX idx_shows_screen_id ON shows(screen_id);
CREATE INDEX idx_shows_start_time ON shows(start_time);
