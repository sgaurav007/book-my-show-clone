import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/{**,.client,.server}/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          main: "#C31E2E",
          light: "#E53945",
          dark: "#8E1620",
          contrastText: "#FFFFFF",
        },
        secondary: {
          main: "#2B3148",
          light: "#505469",
          dark: "#1E2233",
          contrastText: "#FFFFFF",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
