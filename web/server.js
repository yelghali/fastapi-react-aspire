/**
 * Production server for React Router v7 with API proxy.
 *
 * This server:
 * 1. Proxies /api requests to the FastAPI backend
 * 2. Serves the React Router SSR application
 *
 * Environment variables:
 * - API_ENDPOINT_HTTP: Backend API URL (default: http://localhost:8000)
 * - PORT: Server port (default: 3000)
 */

import { createRequestHandler } from "@react-router/express";
import express from "express";
import { createProxyMiddleware, fixRequestBody } from "http-proxy-middleware";

const app = express();

// Parse JSON for API proxy
app.use("/api", express.json());

// API proxy configuration
const apiTarget = process.env.API_ENDPOINT_HTTP || "http://localhost:8000";
console.log(`Proxying /api requests to: ${apiTarget}`);

const apiProxy = createProxyMiddleware({
  target: apiTarget,
  changeOrigin: true,
  pathFilter: (path) => path.startsWith("/api"),
  ws: true, // Enable WebSocket proxying
  on: {
    proxyReq: (proxyReq, req) => {
      // Fix request body for JSON requests
      fixRequestBody(proxyReq, req);
    },
    error: (err, req, res) => {
      console.error("Proxy error:", err.message);
      if (res.writeHead) {
        res.writeHead(502, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Bad Gateway", message: err.message }));
      }
    },
  },
});

// Mount API proxy
app.use("/api", apiProxy);

// Serve static assets from the build
app.use(express.static("build/client"));

// Handle all other requests with React Router
const build = await import("./build/server/index.js");
app.all("*", createRequestHandler({ build }));

// Start server
const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
