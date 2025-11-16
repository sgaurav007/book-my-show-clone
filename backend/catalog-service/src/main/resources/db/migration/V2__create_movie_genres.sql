CREATE TABLE movie_genres (
    movie_id BIGINT NOT NULL,
    genre VARCHAR(50) NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
);

CREATE INDEX idx_movie_genres_movie_id ON movie_genres(movie_id);
CREATE INDEX idx_movie_genres_genre ON movie_genres(genre);
