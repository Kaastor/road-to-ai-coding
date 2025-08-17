import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
    // optional: globals: true,
  },
  esbuild: {
    jsx: "automatic",
  },
});
