import { useState } from "react";
import type { MetaFunction } from "@remix-run/node";
import { useNavigate, Link } from "@remix-run/react";
import { Container, Typography, Box, Button, Paper, TextField, Alert, Grid } from "@mui/material";
import { MainLayout } from "~/components/shared/MainLayout";
import { useAuth } from "~/hooks/shared/useAuth";
import { APP_NAME } from "~/utils/shared/constants";

export const meta: MetaFunction = () => {
  return [
    { title: `Register - ${APP_NAME}` },
    { name: "description", content: "Create your account" },
  ];
};

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register, isRegistering, registerError } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    phone: "",
  });
  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.email || !formData.password || !formData.firstName || !formData.lastName || !formData.phone) {
      setError("Please fill in all fields");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    try {
      await register({
        email: formData.email,
        password: formData.password,
        firstName: formData.firstName,
        lastName: formData.lastName,
        phone: formData.phone,
      });
      navigate("/");
    } catch (err) {
      setError("Registration failed. Please try again.");
    }
  };

  return (
    <MainLayout>
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom fontWeight={600} textAlign="center">
            Register
          </Typography>
          <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
            Create your {APP_NAME} account
          </Typography>

          <Box component="form" onSubmit={handleSubmit} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {(error || registerError) && (
              <Alert severity="error">
                {error || registerError?.message}
              </Alert>
            )}

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="First Name"
                  value={formData.firstName}
                  onChange={handleChange("firstName")}
                  required
                  autoComplete="given-name"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Last Name"
                  value={formData.lastName}
                  onChange={handleChange("lastName")}
                  required
                  autoComplete="family-name"
                />
              </Grid>
            </Grid>

            <TextField
              fullWidth
              label="Email"
              type="email"
              value={formData.email}
              onChange={handleChange("email")}
              required
              autoComplete="email"
            />

            <TextField
              fullWidth
              label="Phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange("phone")}
              required
              autoComplete="tel"
            />

            <TextField
              fullWidth
              label="Password"
              type="password"
              value={formData.password}
              onChange={handleChange("password")}
              required
              autoComplete="new-password"
              helperText="Minimum 8 characters"
            />

            <TextField
              fullWidth
              label="Confirm Password"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange("confirmPassword")}
              required
              autoComplete="new-password"
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isRegistering}
              sx={{ mt: 2 }}
            >
              {isRegistering ? "Creating account..." : "Register"}
            </Button>

            <Typography variant="body2" textAlign="center" sx={{ mt: 2 }}>
              Already have an account?{" "}
              <Link to="/auth/login" style={{ color: "#C31E2E", textDecoration: "none", fontWeight: 600 }}>
                Login here
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Container>
    </MainLayout>
  );
}
