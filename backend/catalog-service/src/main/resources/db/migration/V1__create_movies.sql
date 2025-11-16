CREATE TABLE movies (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL,
    language VARCHAR(50) NOT NULL,
    release_date DATE NOT NULL,
    rating VARCHAR(10),
    poster_url VARCHAR(512),
    trailer_url VARCHAR(512),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_language ON movies(language);
CREATE INDEX idx_movies_release_date ON movies(release_date);
CREATE INDEX idx_movies_is_active ON movies(is_active);
