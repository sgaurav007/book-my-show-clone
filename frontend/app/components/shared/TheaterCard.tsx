import { Card, CardContent, Typography, Box, Chip } from "@mui/material";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import type { Theater } from "~/utils/shared/types";

interface TheaterCardProps {
  theater: Theater;
  showTimes?: string[];
  onShowTimeClick?: (showTime: string) => void;
}

export function TheaterCard({ theater, showTimes, onShowTimeClick }: TheaterCardProps) {
  return (
    <Card
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <CardContent>
        <Typography variant="h6" component="h3" gutterBottom fontWeight={600}>
          {theater.name}
        </Typography>
        <Box sx={{ display: "flex", alignItems: "flex-start", gap: 0.5, mb: 2 }}>
          <LocationOnIcon sx={{ fontSize: 18, color: "text.secondary", mt: 0.3 }} />
          <Typography variant="body2" color="text.secondary">
            {theater.address}, {theater.city}, {theater.state} - {theater.zipCode}
          </Typography>
        </Box>
        {theater.amenities && theater.amenities.length > 0 && (
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 2 }}>
            {theater.amenities.map((amenity) => (
              <Chip
                key={amenity}
                label={amenity}
                size="small"
                variant="outlined"
                sx={{ fontSize: "0.7rem" }}
              />
            ))}
          </Box>
        )}
        {showTimes && showTimes.length > 0 && (
          <Box>
            <Typography variant="subtitle2" gutterBottom fontWeight={600}>
              Show Times
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
              {showTimes.map((time) => (
                <Chip
                  key={time}
                  label={time}
                  clickable
                  onClick={() => onShowTimeClick?.(time)}
                  sx={{
                    bgcolor: "primary.main",
                    color: "white",
                    fontWeight: 600,
                    "&:hover": {
                      bgcolor: "primary.dark",
                    },
                  }}
                />
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
