import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // In dev, /api calls go to the FastAPI server.
    // 127.0.0.1, not localhost: Node resolves localhost to IPv6 but uvicorn listens on IPv4.
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
});
