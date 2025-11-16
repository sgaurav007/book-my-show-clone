import { Card, CardMedia, CardContent, Typography, Box, Chip } from "@mui/material";
import { Link } from "@remix-run/react";
import StarIcon from "@mui/icons-material/Star";
import type { Movie } from "~/utils/shared/types";
import { formatDuration } from "~/utils/shared/formatters";

interface MovieCardProps {
  movie: Movie;
}

export function MovieCard({ movie }: MovieCardProps) {
  return (
    <Card
      component={Link}
      to={`/movies/${movie.id}`}
      sx={{
        textDecoration: "none",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        transition: "transform 0.2s, box-shadow 0.2s",
        "&:hover": {
          transform: "translateY(-4px)",
          boxShadow: "0 8px 16px rgba(0,0,0,0.2)",
        },
      }}
    >
      <CardMedia
        component="img"
        height="400"
        image={movie.posterUrl}
        alt={movie.title}
        sx={{
          objectFit: "cover",
        }}
      />
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography
          gutterBottom
          variant="h6"
          component="h3"
          sx={{
            fontWeight: 600,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {movie.title}
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}>
          {movie.averageRating > 0 && (
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <StarIcon sx={{ color: "warning.main", fontSize: 18 }} />
              <Typography variant="body2" fontWeight={600}>
                {movie.averageRating.toFixed(1)}
              </Typography>
            </Box>
          )}
          <Chip
            label={movie.rating}
            size="small"
            sx={{
              bgcolor: "secondary.main",
              color: "white",
              fontWeight: 600,
            }}
          />
        </Box>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 1 }}>
          {movie.genre.slice(0, 2).map((genre) => (
            <Chip
              key={genre}
              label={genre}
              size="small"
              variant="outlined"
              sx={{ fontSize: "0.75rem" }}
            />
          ))}
        </Box>
        <Typography variant="body2" color="text.secondary">
          {movie.language} • {formatDuration(movie.duration)}
        </Typography>
      </CardContent>
    </Card>
  );
}
