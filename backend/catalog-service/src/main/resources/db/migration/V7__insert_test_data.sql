-- Insert test movies
INSERT INTO movies (title, description, duration_minutes, language, release_date, rating, poster_url, trailer_url, is_active)
VALUES
    ('Inception', 'A mind-bending thriller about dream manipulation', 148, 'English', '2010-07-16', 'PG-13', 'https://example.com/inception.jpg', 'https://example.com/inception-trailer.mp4', true),
    ('The Dark Knight', 'Batman faces the Joker in this epic crime thriller', 152, 'English', '2008-07-18', 'PG-13', 'https://example.com/dark-knight.jpg', 'https://example.com/dark-knight-trailer.mp4', true),
    ('Interstellar', 'A team of explorers travel through a wormhole in space', 169, 'English', '2014-11-07', 'PG-13', 'https://example.com/interstellar.jpg', 'https://example.com/interstellar-trailer.mp4', true),
    ('Dangal', 'A former wrestler trains his daughters to become wrestling champions', 161, 'Hindi', '2016-12-23', 'PG', 'https://example.com/dangal.jpg', 'https://example.com/dangal-trailer.mp4', true),
    ('3 Idiots', 'Three friends navigate college life and pursue their dreams', 170, 'Hindi', '2009-12-25', 'PG-13', 'https://example.com/3-idiots.jpg', 'https://example.com/3-idiots-trailer.mp4', true);

-- Insert movie genres
INSERT INTO movie_genres (movie_id, genre)
VALUES
    (1, 'Action'),
    (1, 'Sci-Fi'),
    (1, 'Thriller'),
    (2, 'Action'),
    (2, 'Crime'),
    (2, 'Drama'),
    (3, 'Adventure'),
    (3, 'Drama'),
    (3, 'Sci-Fi'),
    (4, 'Biography'),
    (4, 'Drama'),
    (4, 'Sport'),
    (5, 'Comedy'),
    (5, 'Drama');

-- Insert test theaters
INSERT INTO theaters (name, city, address, latitude, longitude, is_active)
VALUES
    ('PVR Cinemas Phoenix', 'Mumbai', 'High Street Phoenix, Lower Parel', 19.0176, 72.8278, true),
    ('INOX Megaplex', 'Mumbai', 'Inorbit Mall, Malad', 19.1762, 72.8351, true),
    ('PVR Select City Walk', 'Delhi', 'Saket District Centre', 28.5244, 77.2066, true),
    ('Cinepolis DLF Place', 'Delhi', 'DLF Place, Saket', 28.5212, 77.2155, true),
    ('PVR VR Mall', 'Bangalore', 'VR Bengaluru, Whitefield', 12.9990, 77.7500, true);

-- Insert screens for each theater
INSERT INTO screens (name, total_seats, theater_id)
VALUES
    ('Screen 1', 150, 1),
    ('Screen 2', 120, 1),
    ('Screen 1', 180, 2),
    ('Screen 2', 140, 2),
    ('Screen 1', 200, 3),
    ('Screen 2', 160, 3),
    ('Screen 1', 170, 4),
    ('Screen 1', 190, 5);

-- Insert seats for Screen 1 of PVR Cinemas Phoenix (screen_id = 1)
-- Rows A-E with 10 seats each (REGULAR)
INSERT INTO seats (row_label, seat_number, seat_type, screen_id)
SELECT
    chr(64 + row_num) as row_label,
    seat_num,
    'REGULAR' as seat_type,
    1 as screen_id
FROM
    generate_series(1, 5) as row_num,
    generate_series(1, 10) as seat_num;

-- Rows F-J with 10 seats each (PREMIUM)
INSERT INTO seats (row_label, seat_number, seat_type, screen_id)
SELECT
    chr(64 + row_num) as row_label,
    seat_num,
    'PREMIUM' as seat_type,
    1 as screen_id
FROM
    generate_series(6, 10) as row_num,
    generate_series(1, 10) as seat_num;

-- Rows K-L with 10 seats each (VIP)
INSERT INTO seats (row_label, seat_number, seat_type, screen_id)
SELECT
    chr(64 + row_num) as row_label,
    seat_num,
    'VIP' as seat_type,
    1 as screen_id
FROM
    generate_series(11, 12) as row_num,
    generate_series(1, 10) as seat_num;

-- Insert shows (next 7 days)
INSERT INTO shows (movie_id, screen_id, start_time, end_time, base_price)
VALUES
    -- Inception shows in Mumbai
    (1, 1, CURRENT_DATE + INTERVAL '1 day' + INTERVAL '10 hours', CURRENT_DATE + INTERVAL '1 day' + INTERVAL '12 hours 30 minutes', 250.00),
    (1, 1, CURRENT_DATE + INTERVAL '1 day' + INTERVAL '15 hours', CURRENT_DATE + INTERVAL '1 day' + INTERVAL '17 hours 30 minutes', 300.00),
    (1, 1, CURRENT_DATE + INTERVAL '1 day' + INTERVAL '20 hours', CURRENT_DATE + INTERVAL '1 day' + INTERVAL '22 hours 30 minutes', 350.00),

    -- The Dark Knight shows in Mumbai
    (2, 2, CURRENT_DATE + INTERVAL '1 day' + INTERVAL '11 hours', CURRENT_DATE + INTERVAL '1 day' + INTERVAL '13 hours 35 minutes', 280.00),
    (2, 2, CURRENT_DATE + INTERVAL '1 day' + INTERVAL '16 hours', CURRENT_DATE + INTERVAL '1 day' + INTERVAL '18 hours 35 minutes', 320.00),

    -- Dangal shows in Delhi
    (4, 5, CURRENT_DATE + INTERVAL '2 days' + INTERVAL '12 hours', CURRENT_DATE + INTERVAL '2 days' + INTERVAL '14 hours 45 minutes', 200.00),
    (4, 5, CURRENT_DATE + INTERVAL '2 days' + INTERVAL '18 hours', CURRENT_DATE + INTERVAL '2 days' + INTERVAL '20 hours 45 minutes', 250.00),

    -- 3 Idiots shows in Delhi
    (5, 6, CURRENT_DATE + INTERVAL '2 days' + INTERVAL '13 hours', CURRENT_DATE + INTERVAL '2 days' + INTERVAL '15 hours 50 minutes', 220.00),

    -- Interstellar shows in Bangalore
    (3, 8, CURRENT_DATE + INTERVAL '3 days' + INTERVAL '14 hours', CURRENT_DATE + INTERVAL '3 days' + INTERVAL '16 hours 50 minutes', 300.00),
    (3, 8, CURRENT_DATE + INTERVAL '3 days' + INTERVAL '19 hours', CURRENT_DATE + INTERVAL '3 days' + INTERVAL '21 hours 50 minutes', 350.00);
