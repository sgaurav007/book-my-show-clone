import { useState, useEffect } from "react";
import type { MetaFunction } from "@remix-run/node";
import { useParams, useNavigate } from "@remix-run/react";
import { Container, Typography, Box, Button, Paper, Grid, Alert, Snackbar } from "@mui/material";
import { MainLayout } from "~/components/shared/MainLayout";
import { SeatLayout } from "~/components/shared/SeatLayout";
import { Loader } from "~/components/shared/Loader";
import { useShow, useShowSeats } from "~/hooks/shared/useMovies";
import { useLockSeats, useCreateBooking } from "~/hooks/shared/useBooking";
import { useAuth } from "~/hooks/shared/useAuth";
import { formatCurrency, formatTime, formatDate } from "~/utils/shared/formatters";
import { APP_NAME, SEAT_LOCK_DURATION } from "~/utils/shared/constants";

export const meta: MetaFunction = () => {
  return [
    { title: `Select Seats - ${APP_NAME}` },
    { name: "description", content: "Select your seats and book tickets" },
  ];
};

export default function BookingPage() {
  const { showId } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [selectedSeats, setSelectedSeats] = useState<string[]>([]);
  const [lockId, setLockId] = useState<string | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const { data: show, isLoading: isLoadingShow } = useShow(showId);
  const { data: seatsData, isLoading: isLoadingSeats } = useShowSeats(showId);
  const lockSeatsMutation = useLockSeats();
  const createBookingMutation = useCreateBooking();

  useEffect(() => {
    if (timeRemaining > 0) {
      const timer = setTimeout(() => {
        setTimeRemaining(timeRemaining - 1000);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0 && lockId) {
      setLockId(null);
      setSelectedSeats([]);
      setError("Seat lock expired. Please select seats again.");
    }
  }, [timeRemaining, lockId]);

  const handleSeatSelect = (seatId: string) => {
    if (selectedSeats.includes(seatId)) {
      setSelectedSeats(selectedSeats.filter((id) => id !== seatId));
    } else {
      setSelectedSeats([...selectedSeats, seatId]);
    }
  };

  const handleLockSeats = async () => {
    if (!isAuthenticated) {
      navigate("/auth/login");
      return;
    }

    if (selectedSeats.length === 0) {
      setError("Please select at least one seat");
      return;
    }

    try {
      const result = await lockSeatsMutation.mutateAsync({
        showId: showId!,
        seatIds: selectedSeats,
      });
      setLockId(result.lockId);
      setTimeRemaining(SEAT_LOCK_DURATION);
      setError(null);
    } catch (err) {
      setError("Failed to lock seats. Please try again.");
    }
  };

  const handleProceedToPayment = async () => {
    if (!showId) return;

    try {
      const booking = await createBookingMutation.mutateAsync({
        showId,
        seatIds: selectedSeats,
      });
      navigate(`/payment?bookingId=${booking.id}`);
    } catch (err) {
      setError("Failed to create booking. Please try again.");
    }
  };

  if (isLoadingShow || isLoadingSeats) {
    return (
      <MainLayout>
        <Loader fullScreen />
      </MainLayout>
    );
  }

  if (!show || !seatsData) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ py: 8, textAlign: "center" }}>
          <Typography variant="h5">Show not found</Typography>
        </Container>
      </MainLayout>
    );
  }

  const selectedSeatsData = seatsData.filter((seat: { id: string }) => selectedSeats.includes(seat.id));
  const totalAmount = selectedSeatsData.reduce((sum: number, seat: { price: number }) => sum + seat.price, 0);

  return (
    <MainLayout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom fontWeight={600}>
            {show.movie.title}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {show.theater.name} - {show.screen.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {formatDate(show.date)} at {formatTime(show.startTime)}
          </Typography>
        </Paper>

        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Select Seats
              </Typography>
              <SeatLayout
                seats={seatsData}
                selectedSeats={selectedSeats}
                onSeatSelect={handleSeatSelect}
              />
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, position: "sticky", top: 20 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Booking Summary
              </Typography>

              {lockId && timeRemaining > 0 && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  Seats locked for {Math.floor(timeRemaining / 60000)} min {Math.floor((timeRemaining % 60000) / 1000)} sec
                </Alert>
              )}

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Selected Seats ({selectedSeats.length})
                </Typography>
                <Typography variant="body1" fontWeight={600}>
                  {selectedSeatsData.map((seat: { seatNumber: string }) => seat.seatNumber).join(", ") || "None"}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Total Amount
                </Typography>
                <Typography variant="h5" fontWeight={700} color="primary">
                  {formatCurrency(totalAmount)}
                </Typography>
              </Box>

              {!lockId ? (
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handleLockSeats}
                  disabled={selectedSeats.length === 0 || lockSeatsMutation.isPending}
                >
                  {lockSeatsMutation.isPending ? "Locking Seats..." : "Lock Seats"}
                </Button>
              ) : (
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handleProceedToPayment}
                  disabled={createBookingMutation.isPending}
                >
                  {createBookingMutation.isPending ? "Processing..." : "Proceed to Payment"}
                </Button>
              )}
            </Paper>
          </Grid>
        </Grid>

        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError(null)}
          message={error}
        />
      </Container>
    </MainLayout>
  );
}
