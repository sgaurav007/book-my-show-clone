import type { MetaFunction } from "@remix-run/node";
import { useParams, useNavigate } from "@remix-run/react";
import { Container, Typography, Box, Grid, Button, Chip, Divider } from "@mui/material";
import StarIcon from "@mui/icons-material/Star";
import CalendarTodayIcon from "@mui/icons-material/CalendarToday";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import { MainLayout } from "~/components/shared/MainLayout";
import { TheaterCard } from "~/components/shared/TheaterCard";
import { Loader } from "~/components/shared/Loader";
import { useMovie, useShows } from "~/hooks/shared/useMovies";
import { formatDate, formatDuration, formatTime } from "~/utils/shared/formatters";
import { APP_NAME } from "~/utils/shared/constants";
import { useState } from "react";
import { format } from "date-fns";

export const meta: MetaFunction = () => {
  return [
    { title: `Movie Details - ${APP_NAME}` },
    { name: "description", content: "View movie details and book tickets" },
  ];
};

export default function MovieDetailPage() {
  const { movieId } = useParams();
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState(format(new Date(), "yyyy-MM-dd"));

  const { data: movie, isLoading: isLoadingMovie } = useMovie(movieId);
  const { data: shows, isLoading: isLoadingShows } = useShows({
    movieId,
    date: selectedDate,
  });

  const handleShowTimeClick = (showId: string) => {
    navigate(`/booking/${showId}`);
  };

  if (isLoadingMovie) {
    return (
      <MainLayout>
        <Loader fullScreen />
      </MainLayout>
    );
  }

  if (!movie) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ py: 8, textAlign: "center" }}>
          <Typography variant="h5">Movie not found</Typography>
        </Container>
      </MainLayout>
    );
  }

  const theaterShows = shows?.reduce((acc, show) => {
    const theaterId = show.theater.id;
    if (!acc[theaterId]) {
      acc[theaterId] = {
        theater: show.theater,
        showTimes: [],
      };
    }
    acc[theaterId].showTimes.push({
      time: formatTime(show.startTime),
      showId: show.id,
    });
    return acc;
  }, {} as Record<string, { theater: typeof shows[0]["theater"]; showTimes: { time: string; showId: string }[] }>);

  return (
    <MainLayout>
      <Box
        sx={{
          bgcolor: "secondary.main",
          color: "white",
          py: 4,
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={3}>
              <Box
                component="img"
                src={movie.posterUrl}
                alt={movie.title}
                sx={{
                  width: "100%",
                  borderRadius: 2,
                  boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                }}
              />
            </Grid>
            <Grid item xs={12} md={9}>
              <Typography variant="h3" component="h1" gutterBottom fontWeight={700}>
                {movie.title}
              </Typography>
              <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
                {movie.averageRating > 0 && (
                  <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                    <StarIcon sx={{ color: "warning.main" }} />
                    <Typography variant="h6" fontWeight={600}>
                      {movie.averageRating.toFixed(1)}/10
                    </Typography>
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      ({movie.totalReviews} reviews)
                    </Typography>
                  </Box>
                )}
                <Chip label={movie.rating} sx={{ bgcolor: "primary.main", color: "white", fontWeight: 600 }} />
              </Box>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2 }}>
                {movie.genre.map((genre) => (
                  <Chip key={genre} label={genre} variant="outlined" sx={{ color: "white", borderColor: "white" }} />
                ))}
              </Box>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 3, mb: 3 }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <AccessTimeIcon />
                  <Typography>{formatDuration(movie.duration)}</Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <CalendarTodayIcon />
                  <Typography>{formatDate(movie.releaseDate)}</Typography>
                </Box>
                <Typography>{movie.language}</Typography>
              </Box>
              <Typography variant="body1" sx={{ mb: 2 }}>
                {movie.description}
              </Typography>
              <Typography variant="body2">
                <strong>Director:</strong> {movie.director}
              </Typography>
              <Typography variant="body2">
                <strong>Cast:</strong> {movie.cast.join(", ")}
              </Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom fontWeight={600} sx={{ mb: 3 }}>
          Book Tickets
        </Typography>

        <Box sx={{ mb: 3 }}>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            style={{
              padding: "12px",
              fontSize: "16px",
              borderRadius: "8px",
              border: "1px solid #ccc",
            }}
          />
        </Box>

        {isLoadingShows ? (
          <Loader />
        ) : theaterShows && Object.keys(theaterShows).length > 0 ? (
          <Grid container spacing={3}>
            {Object.values(theaterShows).map(({ theater, showTimes }) => (
              <Grid item key={theater.id} xs={12}>
                <TheaterCard
                  theater={theater}
                  showTimes={showTimes.map((st) => st.time)}
                  onShowTimeClick={(time) => {
                    const show = showTimes.find((st) => st.time === time);
                    if (show) {
                      handleShowTimeClick(show.showId);
                    }
                  }}
                />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <Typography variant="h6" color="text.secondary">
              No shows available for the selected date
            </Typography>
          </Box>
        )}
      </Container>
    </MainLayout>
  );
}
