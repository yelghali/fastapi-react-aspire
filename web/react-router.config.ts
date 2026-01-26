import type { Config } from "@react-router/dev/config";

export default {
  // Enable server-side rendering
  ssr: true,
  // Prerender the home page for better initial load
  prerender: ["/"],
} satisfies Config;
