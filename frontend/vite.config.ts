import { vitePlugin as remix } from "@remix-run/dev";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [
    remix({
      future: {
        v3_fetcherPersist: true,
        v3_relativeSplatPath: true,
        v3_throwAbortReason: true,
      },
    }),
    tsconfigPaths(),
  ],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./app/test/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html", "lcov"],
      include: ["app/**/*.{ts,tsx}"],
      exclude: [
        "app/test/**",
        "app/**/*.test.{ts,tsx}",
        "app/**/*.spec.{ts,tsx}",
        "app/entry.client.tsx",
        "app/entry.server.tsx",
        "app/root.tsx",
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
  server: {
    port: 3000,
  },
});
