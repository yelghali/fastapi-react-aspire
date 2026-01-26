/**
 * Root loader - provides configuration to the client.
 *
 * This loader runs on the server and exposes:
 * - OpenTelemetry configuration for browser tracing
 * - Environment flags
 */

export function loader() {
  // Get OTLP endpoint from Aspire-provided environment variables
  let otlpHttpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT;
  const otlpHeaders = process.env.OTEL_EXPORTER_OTLP_HEADERS;

  // Aspire uses :19140 for gRPC, but browsers need :19141 for HTTP
  if (otlpHttpEndpoint?.includes(":19140")) {
    otlpHttpEndpoint = otlpHttpEndpoint.replace(":19140", ":19141");
  }

  // Ensure we use the /v1/traces path for OTLP HTTP
  if (otlpHttpEndpoint && !otlpHttpEndpoint.endsWith("/v1/traces")) {
    otlpHttpEndpoint = `${otlpHttpEndpoint}/v1/traces`;
  }

  const otelConfig = {
    serviceName: process.env.OTEL_SERVICE_NAME || "starter-web",
    resourceAttributes: process.env.OTEL_RESOURCE_ATTRIBUTES || undefined,
    tracesSampler: process.env.OTEL_TRACES_SAMPLER || undefined,
    otlpHttpEndpoint,
    otlpHeaders,
  };

  return {
    otelConfig,
    env: {
      DEV: process.env.NODE_ENV === "development",
    },
    buildVersion: typeof __BUILD_VERSION__ !== "undefined" ? __BUILD_VERSION__ : "unknown",
  };
}
