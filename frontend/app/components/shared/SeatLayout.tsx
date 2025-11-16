import { Box, Typography, Button, Grid, Chip } from "@mui/material";
import { SEAT_COLORS, MAX_SEATS_PER_BOOKING } from "~/utils/shared/constants";
import type { Seat } from "~/utils/shared/types";

interface SeatLayoutProps {
  seats: Seat[];
  selectedSeats: string[];
  onSeatSelect: (seatId: string) => void;
}

export function SeatLayout({ seats, selectedSeats, onSeatSelect }: SeatLayoutProps) {
  const rows = Array.from(new Set(seats.map((seat) => seat.row))).sort();

  const getSeatColor = (seat: Seat): string => {
    if (selectedSeats.includes(seat.id)) {
      return SEAT_COLORS.SELECTED;
    }
    if (seat.status === "BOOKED") {
      return SEAT_COLORS.BOOKED;
    }
    if (seat.status === "LOCKED") {
      return SEAT_COLORS.LOCKED;
    }
    return SEAT_COLORS.AVAILABLE;
  };

  const isSeatDisabled = (seat: Seat): boolean => {
    if (seat.status === "BOOKED" || seat.status === "LOCKED") {
      return true;
    }
    if (selectedSeats.includes(seat.id)) {
      return false;
    }
    return selectedSeats.length >= MAX_SEATS_PER_BOOKING;
  };

  const handleSeatClick = (seat: Seat) => {
    if (!isSeatDisabled(seat) || selectedSeats.includes(seat.id)) {
      onSeatSelect(seat.id);
    }
  };

  return (
    <Box>
      <Box sx={{ mb: 4, textAlign: "center" }}>
        <Box
          sx={{
            bgcolor: "grey.300",
            py: 1,
            borderRadius: 1,
            maxWidth: 600,
            mx: "auto",
          }}
        >
          <Typography variant="body2" fontWeight={600}>
            Screen This Way
          </Typography>
        </Box>
      </Box>

      <Box sx={{ mb: 3, overflowX: "auto" }}>
        <Box sx={{ minWidth: 600 }}>
          {rows.map((row) => {
            const rowSeats = seats.filter((seat) => seat.row === row).sort((a, b) => a.column - b.column);
            return (
              <Box key={row} sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Typography
                  variant="body2"
                  sx={{
                    width: 30,
                    fontWeight: 600,
                    color: "text.secondary",
                  }}
                >
                  {row}
                </Typography>
                <Box sx={{ display: "flex", gap: 0.5, flexWrap: "nowrap" }}>
                  {rowSeats.map((seat) => (
                    <Button
                      key={seat.id}
                      variant="contained"
                      onClick={() => handleSeatClick(seat)}
                      disabled={isSeatDisabled(seat)}
                      sx={{
                        minWidth: 36,
                        width: 36,
                        height: 36,
                        p: 0,
                        bgcolor: getSeatColor(seat),
                        color: "white",
                        fontSize: "0.7rem",
                        fontWeight: 600,
                        "&:hover": {
                          bgcolor: getSeatColor(seat),
                          opacity: 0.9,
                        },
                        "&.Mui-disabled": {
                          bgcolor: getSeatColor(seat),
                          color: "white",
                          opacity: 0.6,
                        },
                      }}
                    >
                      {seat.column}
                    </Button>
                  ))}
                </Box>
              </Box>
            );
          })}
        </Box>
      </Box>

      <Box sx={{ display: "flex", justifyContent: "center", flexWrap: "wrap", gap: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: SEAT_COLORS.AVAILABLE, borderRadius: 0.5 }} />
          <Typography variant="body2">Available</Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: SEAT_COLORS.SELECTED, borderRadius: 0.5 }} />
          <Typography variant="body2">Selected</Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: SEAT_COLORS.BOOKED, borderRadius: 0.5 }} />
          <Typography variant="body2">Booked</Typography>
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: SEAT_COLORS.LOCKED, borderRadius: 0.5 }} />
          <Typography variant="body2">Locked</Typography>
        </Box>
      </Box>
    </Box>
  );
}
