import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
    globals: true,
    watch: {
      clearScreen: false,
    },
    pool: "threads",
    poolOptions: {
      threads: {
        minThreads: 1,
        maxThreads: 4,
      }
    }
  },
  esbuild: {
    jsx: "automatic",
  },
});
