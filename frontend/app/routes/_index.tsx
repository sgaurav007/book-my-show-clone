import type { MetaFunction } from "@remix-run/node";
import { Container, Typography, Box, Grid, Button } from "@mui/material";
import { Link } from "@remix-run/react";
import { MainLayout } from "~/components/shared/MainLayout";
import { MovieCard } from "~/components/shared/MovieCard";
import { Loader } from "~/components/shared/Loader";
import { useMovies } from "~/hooks/shared/useMovies";
import { APP_NAME } from "~/utils/shared/constants";

export const meta: MetaFunction = () => {
  return [
    { title: `${APP_NAME} - Book Movie Tickets Online` },
    { name: "description", content: "Book movie tickets online with ease. Browse movies, select seats, and enjoy your show!" },
  ];
};

export default function Index() {
  const { data: nowShowingMovies, isLoading: isLoadingNowShowing } = useMovies({ search: "" });
  const nowShowing = nowShowingMovies?.filter((m) => m.nowShowing) || [];
  const comingSoon = nowShowingMovies?.filter((m) => m.comingSoon) || [];

  return (
    <MainLayout>
      <Box
        sx={{
          bgcolor: "primary.main",
          color: "white",
          py: 8,
          textAlign: "center",
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h2" component="h1" gutterBottom fontWeight={700}>
            Book Your Movie Tickets
          </Typography>
          <Typography variant="h6" sx={{ mb: 4 }}>
            Browse movies, select your seats, and enjoy the show!
          </Typography>
          <Button
            variant="contained"
            size="large"
            component={Link}
            to="/movies"
            sx={{
              bgcolor: "white",
              color: "primary.main",
              fontWeight: 600,
              px: 4,
              py: 1.5,
              "&:hover": {
                bgcolor: "grey.100",
              },
            }}
          >
            Explore Movies
          </Button>
        </Container>
      </Box>

      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Typography variant="h4" component="h2" gutterBottom fontWeight={600} sx={{ mb: 4 }}>
          Now Showing
        </Typography>
        {isLoadingNowShowing ? (
          <Loader />
        ) : nowShowing.length > 0 ? (
          <Grid container spacing={3}>
            {nowShowing.slice(0, 8).map((movie) => (
              <Grid item key={movie.id} xs={12} sm={6} md={4} lg={3}>
                <MovieCard movie={movie} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Typography variant="body1" color="text.secondary">
            No movies are currently showing.
          </Typography>
        )}

        {nowShowing.length > 8 && (
          <Box sx={{ textAlign: "center", mt: 4 }}>
            <Button variant="outlined" component={Link} to="/movies" size="large">
              View All Movies
            </Button>
          </Box>
        )}
      </Container>

      {comingSoon.length > 0 && (
        <Box sx={{ bgcolor: "background.default", py: 6 }}>
          <Container maxWidth="lg">
            <Typography variant="h4" component="h2" gutterBottom fontWeight={600} sx={{ mb: 4 }}>
              Coming Soon
            </Typography>
            <Grid container spacing={3}>
              {comingSoon.slice(0, 4).map((movie) => (
                <Grid item key={movie.id} xs={12} sm={6} md={4} lg={3}>
                  <MovieCard movie={movie} />
                </Grid>
              ))}
            </Grid>
          </Container>
        </Box>
      )}
    </MainLayout>
  );
}
