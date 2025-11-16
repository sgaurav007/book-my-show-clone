import type { MetaFunction } from "@remix-run/node";
import { useNavigate } from "@remix-run/react";
import { Container, Typography, Box, Paper, Chip, Button, Grid } from "@mui/material";
import { MainLayout } from "~/components/shared/MainLayout";
import { Loader } from "~/components/shared/Loader";
import { useAuth } from "~/hooks/shared/useAuth";
import { useUserBookings, useCancelBooking } from "~/hooks/shared/useBooking";
import { formatCurrency, formatTime, formatDate } from "~/utils/shared/formatters";
import { APP_NAME } from "~/utils/shared/constants";
import { useEffect } from "react";

export const meta: MetaFunction = () => {
  return [
    { title: `My Bookings - ${APP_NAME}` },
    { name: "description", content: "View your booking history" },
  ];
};

export default function MyBookingsPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  const { data: bookings, isLoading } = useUserBookings(user?.id);
  const cancelBookingMutation = useCancelBooking();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/auth/login");
    }
  }, [isAuthenticated, navigate]);

  const handleCancelBooking = async (bookingId: string) => {
    if (window.confirm("Are you sure you want to cancel this booking?")) {
      try {
        await cancelBookingMutation.mutateAsync(bookingId);
      } catch (err) {
        alert("Failed to cancel booking");
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "CONFIRMED":
        return "success";
      case "PENDING":
        return "warning";
      case "CANCELLED":
        return "error";
      case "EXPIRED":
        return "default";
      default:
        return "default";
    }
  };

  if (isLoading) {
    return (
      <MainLayout>
        <Loader fullScreen />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight={600} sx={{ mb: 4 }}>
          My Bookings
        </Typography>

        {bookings && bookings.length > 0 ? (
          <Grid container spacing={3}>
            {bookings.map((booking) => (
              <Grid item key={booking.id} xs={12}>
                <Paper sx={{ p: 3 }}>
                  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 2 }}>
                    <Box>
                      <Typography variant="h6" fontWeight={600}>
                        {booking.show.movie.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {booking.show.theater.name}
                      </Typography>
                    </Box>
                    <Chip
                      label={booking.status}
                      color={getStatusColor(booking.status) as "default" | "success" | "warning" | "error"}
                      sx={{ fontWeight: 600 }}
                    />
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        Booking ID
                      </Typography>
                      <Typography variant="body1" fontWeight={600}>
                        {booking.id}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        Show Date & Time
                      </Typography>
                      <Typography variant="body1">
                        {formatDate(booking.show.date)}<br />
                        {formatTime(booking.show.startTime)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        Seats
                      </Typography>
                      <Typography variant="body1">
                        {booking.seats.map((s) => s.seat.seatNumber).join(", ")}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Typography variant="body2" color="text.secondary">
                        Total Amount
                      </Typography>
                      <Typography variant="body1" fontWeight={600} color="primary">
                        {formatCurrency(booking.totalAmount)}
                      </Typography>
                    </Grid>
                  </Grid>

                  {booking.status === "CONFIRMED" && (
                    <Box sx={{ mt: 2, display: "flex", gap: 2 }}>
                      <Button
                        variant="outlined"
                        color="error"
                        size="small"
                        onClick={() => handleCancelBooking(booking.id)}
                        disabled={cancelBookingMutation.isPending}
                      >
                        Cancel Booking
                      </Button>
                    </Box>
                  )}
                </Paper>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No bookings found
            </Typography>
            <Button variant="contained" onClick={() => navigate("/movies")} sx={{ mt: 2 }}>
              Browse Movies
            </Button>
          </Box>
        )}
      </Container>
    </MainLayout>
  );
}
