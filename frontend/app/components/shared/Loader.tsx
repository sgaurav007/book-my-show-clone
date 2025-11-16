import { Box, CircularProgress } from "@mui/material";

interface LoaderProps {
  size?: number;
  fullScreen?: boolean;
}

export function Loader({ size = 40, fullScreen = false }: LoaderProps) {
  if (fullScreen) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "100vh",
          width: "100%",
        }}
      >
        <CircularProgress size={size} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: 4,
      }}
    >
      <CircularProgress size={size} />
    </Box>
  );
}
