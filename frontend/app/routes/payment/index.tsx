import { useState } from "react";
import type { MetaFunction } from "@remix-run/node";
import { useSearchParams, useNavigate } from "@remix-run/react";
import { Container, Typography, Box, Button, Paper, Grid, TextField, RadioGroup, FormControlLabel, Radio, FormControl, FormLabel, Alert } from "@mui/material";
import { MainLayout } from "~/components/shared/MainLayout";
import { Loader } from "~/components/shared/Loader";
import { useBooking } from "~/hooks/shared/useBooking";
import { useInitiatePayment } from "~/hooks/shared/usePayment";
import { formatCurrency, formatTime, formatDate } from "~/utils/shared/formatters";
import { APP_NAME, PAYMENT_METHOD } from "~/utils/shared/constants";
import type { PaymentRequest } from "~/utils/shared/types";

export const meta: MetaFunction = () => {
  return [
    { title: `Payment - ${APP_NAME}` },
    { name: "description", content: "Complete your booking payment" },
  ];
};

export default function PaymentPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const bookingId = searchParams.get("bookingId");

  const [paymentMethod, setPaymentMethod] = useState<keyof typeof PAYMENT_METHOD>("UPI");
  const [cardNumber, setCardNumber] = useState("");
  const [cardName, setCardName] = useState("");
  const [cardExpiry, setCardExpiry] = useState("");
  const [cardCvv, setCardCvv] = useState("");
  const [upiId, setUpiId] = useState("");
  const [error, setError] = useState<string | null>(null);

  const { data: booking, isLoading } = useBooking(bookingId || undefined);
  const initiatePaymentMutation = useInitiatePayment();

  const handlePayment = async () => {
    if (!bookingId) return;

    const paymentData: PaymentRequest = {
      bookingId,
      method: paymentMethod,
    };

    if (paymentMethod === "CREDIT_CARD" || paymentMethod === "DEBIT_CARD") {
      if (!cardNumber || !cardName || !cardExpiry || !cardCvv) {
        setError("Please fill in all card details");
        return;
      }
      paymentData.cardNumber = cardNumber;
      paymentData.cardName = cardName;
      paymentData.cardExpiry = cardExpiry;
      paymentData.cardCvv = cardCvv;
    }

    if (paymentMethod === "UPI") {
      if (!upiId) {
        setError("Please enter your UPI ID");
        return;
      }
      paymentData.upiId = upiId;
    }

    try {
      await initiatePaymentMutation.mutateAsync(paymentData);
      navigate("/payment/success");
    } catch (err) {
      setError("Payment failed. Please try again.");
    }
  };

  if (isLoading) {
    return (
      <MainLayout>
        <Loader fullScreen />
      </MainLayout>
    );
  }

  if (!booking) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ py: 8, textAlign: "center" }}>
          <Typography variant="h5">Booking not found</Typography>
        </Container>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight={600} sx={{ mb: 4 }}>
          Complete Payment
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={7}>
            <Paper sx={{ p: 3 }}>
              <FormControl component="fieldset" fullWidth>
                <FormLabel component="legend" sx={{ mb: 2, fontWeight: 600 }}>
                  Select Payment Method
                </FormLabel>
                <RadioGroup
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value as keyof typeof PAYMENT_METHOD)}
                >
                  <FormControlLabel value="UPI" control={<Radio />} label="UPI" />
                  <FormControlLabel value="CREDIT_CARD" control={<Radio />} label="Credit Card" />
                  <FormControlLabel value="DEBIT_CARD" control={<Radio />} label="Debit Card" />
                  <FormControlLabel value="NET_BANKING" control={<Radio />} label="Net Banking" />
                  <FormControlLabel value="WALLET" control={<Radio />} label="Wallet" />
                </RadioGroup>
              </FormControl>

              <Box sx={{ mt: 3 }}>
                {(paymentMethod === "CREDIT_CARD" || paymentMethod === "DEBIT_CARD") && (
                  <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                    <TextField
                      fullWidth
                      label="Card Number"
                      value={cardNumber}
                      onChange={(e) => setCardNumber(e.target.value)}
                      placeholder="1234 5678 9012 3456"
                    />
                    <TextField
                      fullWidth
                      label="Cardholder Name"
                      value={cardName}
                      onChange={(e) => setCardName(e.target.value)}
                      placeholder="John Doe"
                    />
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          label="Expiry Date"
                          value={cardExpiry}
                          onChange={(e) => setCardExpiry(e.target.value)}
                          placeholder="MM/YY"
                        />
                      </Grid>
                      <Grid item xs={6}>
                        <TextField
                          fullWidth
                          label="CVV"
                          value={cardCvv}
                          onChange={(e) => setCardCvv(e.target.value)}
                          placeholder="123"
                          type="password"
                        />
                      </Grid>
                    </Grid>
                  </Box>
                )}

                {paymentMethod === "UPI" && (
                  <TextField
                    fullWidth
                    label="UPI ID"
                    value={upiId}
                    onChange={(e) => setUpiId(e.target.value)}
                    placeholder="yourname@upi"
                  />
                )}

                {paymentMethod === "NET_BANKING" && (
                  <Alert severity="info">
                    You will be redirected to your bank's website to complete the payment.
                  </Alert>
                )}

                {paymentMethod === "WALLET" && (
                  <Alert severity="info">
                    Select your preferred wallet to complete the payment.
                  </Alert>
                )}
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={5}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Booking Details
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Movie
                </Typography>
                <Typography variant="body1" fontWeight={600}>
                  {booking.show.movie.title}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Theater
                </Typography>
                <Typography variant="body1">
                  {booking.show.theater.name}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Date & Time
                </Typography>
                <Typography variant="body1">
                  {formatDate(booking.show.date)} at {formatTime(booking.show.startTime)}
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Seats ({booking.seats.length})
                </Typography>
                <Typography variant="body1">
                  {booking.seats.map((s) => s.seat.seatNumber).join(", ")}
                </Typography>
              </Box>

              <Box sx={{ mb: 3, pt: 2, borderTop: "1px solid #e0e0e0" }}>
                <Typography variant="body2" color="text.secondary">
                  Total Amount
                </Typography>
                <Typography variant="h5" fontWeight={700} color="primary">
                  {formatCurrency(booking.totalAmount)}
                </Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handlePayment}
                disabled={initiatePaymentMutation.isPending}
              >
                {initiatePaymentMutation.isPending ? "Processing..." : "Pay Now"}
              </Button>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </MainLayout>
  );
}
