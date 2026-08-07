import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Behind Nginx in dev; allow the container host and enable HMR over the proxy.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // The E2E browser reaches the dev server through the "nginx" hostname;
    // Vite's host check only allows localhost by default.
    allowedHosts: ["localhost", "nginx"],
    watch: { usePolling: true }, // reliable file-watching inside Docker on Windows
  },
});
