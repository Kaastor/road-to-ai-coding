// vitest.config.js
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js"
  },
  esbuild: {
    jsx: "automatic" // ensures JSX works without extra plugins
  }
});
