/**
 * Route definitions for React Router v7.
 */

import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  // Home page
  index("routes/home.tsx"),
  // Items page - demonstrates API integration
  route("items", "routes/items.tsx"),
  // Projects page - GitHub-integrated project management
  route("projects", "routes/projects.tsx"),
] satisfies RouteConfig;
