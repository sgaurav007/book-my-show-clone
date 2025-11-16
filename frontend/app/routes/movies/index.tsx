import { useState } from "react";
import type { MetaFunction } from "@remix-run/node";
import { Container, Typography, Box, Grid, TextField, MenuItem, Select, FormControl, InputLabel } from "@mui/material";
import { MainLayout } from "~/components/shared/MainLayout";
import { MovieCard } from "~/components/shared/MovieCard";
import { Loader } from "~/components/shared/Loader";
import { useMovies } from "~/hooks/shared/useMovies";
import { MOVIE_GENRE, MOVIE_LANGUAGE, MOVIE_RATING, APP_NAME } from "~/utils/shared/constants";
import type { MovieFilter } from "~/utils/shared/types";

export const meta: MetaFunction = () => {
  return [
    { title: `Movies - ${APP_NAME}` },
    { name: "description", content: "Browse and book tickets for your favorite movies" },
  ];
};

export default function MoviesPage() {
  const [filters, setFilters] = useState<MovieFilter>({});
  const { data: movies, isLoading } = useMovies(filters);

  const handleFilterChange = (key: keyof MovieFilter, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  return (
    <MainLayout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight={600} sx={{ mb: 4 }}>
          Browse Movies
        </Typography>

        <Box sx={{ mb: 4 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Search"
                variant="outlined"
                value={filters.search || ""}
                onChange={(e) => handleFilterChange("search", e.target.value)}
                placeholder="Search movies..."
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Genre</InputLabel>
                <Select
                  value={filters.genre || ""}
                  label="Genre"
                  onChange={(e) => handleFilterChange("genre", e.target.value)}
                >
                  <MenuItem value="">All Genres</MenuItem>
                  {Object.values(MOVIE_GENRE).map((genre) => (
                    <MenuItem key={genre} value={genre}>
                      {genre}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Language</InputLabel>
                <Select
                  value={filters.language || ""}
                  label="Language"
                  onChange={(e) => handleFilterChange("language", e.target.value)}
                >
                  <MenuItem value="">All Languages</MenuItem>
                  {Object.values(MOVIE_LANGUAGE).map((language) => (
                    <MenuItem key={language} value={language}>
                      {language}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Rating</InputLabel>
                <Select
                  value={filters.rating || ""}
                  label="Rating"
                  onChange={(e) => handleFilterChange("rating", e.target.value)}
                >
                  <MenuItem value="">All Ratings</MenuItem>
                  {Object.values(MOVIE_RATING).map((rating) => (
                    <MenuItem key={rating} value={rating}>
                      {rating}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </Box>

        {isLoading ? (
          <Loader />
        ) : movies && movies.length > 0 ? (
          <Grid container spacing={3}>
            {movies.map((movie) => (
              <Grid item key={movie.id} xs={12} sm={6} md={4} lg={3}>
                <MovieCard movie={movie} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <Typography variant="h6" color="text.secondary">
              No movies found matching your criteria
            </Typography>
          </Box>
        )}
      </Container>
    </MainLayout>
  );
}
