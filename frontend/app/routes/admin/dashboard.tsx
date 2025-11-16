import type { MetaFunction } from "@remix-run/node";
import { useNavigate } from "@remix-run/react";
import { Container, Typography, Box, Paper, Grid, Card, CardContent } from "@mui/material";
import MovieIcon from "@mui/icons-material/Movie";
import TheatersIcon from "@mui/icons-material/Theaters";
import ConfirmationNumberIcon from "@mui/icons-material/ConfirmationNumber";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import { MainLayout } from "~/components/shared/MainLayout";
import { useAuth } from "~/hooks/shared/useAuth";
import { APP_NAME } from "~/utils/shared/constants";
import { useEffect } from "react";

export const meta: MetaFunction = () => {
  return [
    { title: `Admin Dashboard - ${APP_NAME}` },
    { name: "description", content: "Admin dashboard for managing the platform" },
  ];
};

export default function AdminDashboardPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated || user?.role !== "ADMIN") {
      navigate("/");
    }
  }, [isAuthenticated, user, navigate]);

  const stats = [
    { label: "Total Movies", value: "150", icon: MovieIcon, color: "#C31E2E" },
    { label: "Total Theaters", value: "45", icon: TheatersIcon, color: "#2B3148" },
    { label: "Total Bookings", value: "12,450", icon: ConfirmationNumberIcon, color: "#4CAF50" },
    { label: "Revenue", value: "₹2,45,000", icon: AttachMoneyIcon, color: "#FF9800" },
  ];

  return (
    <MainLayout>
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight={600} sx={{ mb: 4 }}>
          Admin Dashboard
        </Typography>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Grid item key={stat.label} xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                      <Box
                        sx={{
                          bgcolor: stat.color,
                          color: "white",
                          p: 1.5,
                          borderRadius: 2,
                          display: "flex",
                        }}
                      >
                        <Icon />
                      </Box>
                      <Box>
                        <Typography variant="h4" fontWeight={700}>
                          {stat.value}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {stat.label}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Recent Activities
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Activity feed will be displayed here
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Quick Actions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Quick action buttons will be displayed here
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </MainLayout>
  );
}
