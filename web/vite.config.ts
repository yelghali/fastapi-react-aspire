import { reactRouter } from "@react-router/dev/vite";
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";

// Build version from environment or generate from timestamp
const now = new Date();
const buildVersion =
  process.env.BUILD_VERSION ||
  `dev-${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}-${String(now.getHours()).padStart(2, "0")}${String(now.getMinutes()).padStart(2, "0")}`;

export default defineConfig({
  define: {
    __BUILD_VERSION__: JSON.stringify(buildVersion),
    __IS_DEV__: JSON.stringify(!process.env.BUILD_VERSION),
  },
  plugins: [tailwindcss(), reactRouter(), tsconfigPaths()],
  server: {
    proxy: {
      // Proxy API requests to the FastAPI backend during development
      "/api": {
        target: process.env.API_ENDPOINT_HTTP || "http://localhost:8000",
        changeOrigin: true,
        secure: false,
        ws: true, // Enable WebSocket proxying
      },
    },
  },
});
