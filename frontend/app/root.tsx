import {
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useRouteError,
  isRouteErrorResponse,
} from "@remix-run/react";
import type { LinksFunction } from "@remix-run/node";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { theme } from "./theme";
import { Box, Container, Typography, Button } from "@mui/material";
import { useState } from "react";

export const links: LinksFunction = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  {
    rel: "preconnect",
    href: "https://fonts.gstatic.com",
    crossOrigin: "anonymous",
  },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700&display=swap",
  },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryClientProvider client={queryClient}>
        <Outlet />
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ThemeProvider>
  );
}

export function ErrorBoundary() {
  const error = useRouteError();

  let errorMessage = "An unexpected error occurred";
  let errorStatus = 500;

  if (isRouteErrorResponse(error)) {
    errorMessage = error.data.message || error.statusText;
    errorStatus = error.status;
  } else if (error instanceof Error) {
    errorMessage = error.message;
  }

  return (
    <html lang="en">
      <head>
        <title>Error - BookMyShow</title>
        <Meta />
        <Links />
      </head>
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Container maxWidth="md">
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                minHeight: "100vh",
                textAlign: "center",
                gap: 3,
              }}
            >
              <Typography variant="h1" color="error">
                {errorStatus}
              </Typography>
              <Typography variant="h5" color="text.secondary">
                Oops! Something went wrong
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {errorMessage}
              </Typography>
              <Button
                variant="contained"
                color="primary"
                href="/"
                sx={{ mt: 2 }}
              >
                Go Home
              </Button>
            </Box>
          </Container>
        </ThemeProvider>
        <Scripts />
      </body>
    </html>
  );
}
