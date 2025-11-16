import { useState } from "react";
import type { MetaFunction } from "@remix-run/node";
import { useNavigate, Link } from "@remix-run/react";
import { Container, Typography, Box, Button, Paper, TextField, Alert } from "@mui/material";
import { MainLayout } from "~/components/shared/MainLayout";
import { useAuth } from "~/hooks/shared/useAuth";
import { APP_NAME } from "~/utils/shared/constants";

export const meta: MetaFunction = () => {
  return [
    { title: `Login - ${APP_NAME}` },
    { name: "description", content: "Login to your account" },
  ];
};

export default function LoginPage() {
  const navigate = useNavigate();
  const { login, isLoggingIn, loginError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    try {
      await login({ email, password });
      navigate("/");
    } catch (err) {
      setError("Invalid email or password");
    }
  };

  return (
    <MainLayout>
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom fontWeight={600} textAlign="center">
            Login
          </Typography>
          <Typography variant="body2" color="text.secondary" textAlign="center" sx={{ mb: 4 }}>
            Welcome back to {APP_NAME}
          </Typography>

          <Box component="form" onSubmit={handleSubmit} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {(error || loginError) && (
              <Alert severity="error">
                {error || loginError?.message}
              </Alert>
            )}

            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />

            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isLoggingIn}
              sx={{ mt: 2 }}
            >
              {isLoggingIn ? "Logging in..." : "Login"}
            </Button>

            <Typography variant="body2" textAlign="center" sx={{ mt: 2 }}>
              Don't have an account?{" "}
              <Link to="/auth/register" style={{ color: "#C31E2E", textDecoration: "none", fontWeight: 600 }}>
                Register here
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Container>
    </MainLayout>
  );
}
