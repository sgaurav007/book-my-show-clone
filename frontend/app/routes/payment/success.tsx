import type { MetaFunction } from "@remix-run/node";
import { Container, Typography, Box, Button, Paper } from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { Link } from "@remix-run/react";
import { MainLayout } from "~/components/shared/MainLayout";
import { APP_NAME } from "~/utils/shared/constants";

export const meta: MetaFunction = () => {
  return [
    { title: `Payment Successful - ${APP_NAME}` },
    { name: "description", content: "Your booking has been confirmed" },
  ];
};

export default function PaymentSuccessPage() {
  return (
    <MainLayout>
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper sx={{ p: 4, textAlign: "center" }}>
          <CheckCircleIcon sx={{ fontSize: 80, color: "success.main", mb: 2 }} />
          <Typography variant="h4" gutterBottom fontWeight={600}>
            Payment Successful!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            Your booking has been confirmed. You will receive a confirmation email shortly.
          </Typography>
          <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
            <Button variant="contained" component={Link} to="/profile/bookings">
              View My Bookings
            </Button>
            <Button variant="outlined" component={Link} to="/">
              Go Home
            </Button>
          </Box>
        </Paper>
      </Container>
    </MainLayout>
  );
}
