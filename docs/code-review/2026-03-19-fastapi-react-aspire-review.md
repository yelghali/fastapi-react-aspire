# Code Review: fastapi-react-aspire
**Ready for Production**: No
**Critical Issues**: 2

## Priority 1 (Must Fix) ⛔

- **Broken Access Control on write endpoints (A01)**
  - Endpoints creating/updating/deleting data are publicly accessible without authentication/authorization checks.
  - Affected:
    - `POST /api/items/`, `PATCH /api/items/{item_id}`, `DELETE /api/items/{item_id}`
    - `POST /api/projects/issues`, `PATCH /api/projects/issues/{issue_number}`
  - Risk: Any unauthenticated caller can modify local items and create/update GitHub issues when a token is configured on the backend.
  - Recommended fix:
    - Add authentication dependency on all mutating routes.
    - Enforce role/scope checks (e.g., `items:write`, `github:issues:write`).
    - Add tests proving 401/403 for unauthenticated/unauthorized callers.

- **Sensitive config leakage to browser (A02/LLM06-style info disclosure)**
  - `root.loader.ts` forwards `OTEL_EXPORTER_OTLP_HEADERS` to client code.
  - OTLP headers often contain API keys/bearer tokens, which would expose credentials to any user opening devtools.
  - Recommended fix:
    - Never expose collector headers to the browser.
    - Keep exporter auth server-side only, or use a dedicated public ingestion endpoint with scoped, non-secret credentials.

## Priority 2 (Should Fix Soon)

- **CORS misconfiguration (A05 Security Misconfiguration)**
  - API sets `allow_origins=["*"]` with `allow_credentials=True`.
  - Risk: Insecure default policy; with future cookie/session auth this can create cross-origin trust issues.
  - Recommended fix:
    - Restrict origins to explicit frontend domains.
    - Keep `allow_credentials` only if required and with strict origin list.

- **Internal error details returned to clients**
  - In projects routes, broad `except Exception` returns `detail=str(exc)`.
  - Risk: Upstream/internal details can leak operational information (tokens are unlikely but error context can still aid attackers).
  - Recommended fix:
    - Map known upstream statuses explicitly.
    - Return sanitized generic messages.
    - Log detailed error server-side only.

## Priority 3 (Recommended)

- **No anti-abuse controls on externally reachable API**
  - No rate limiting/throttling on endpoints that call GitHub API.
  - Risk: abuse, quota exhaustion, and degraded availability.
  - Recommended fix:
    - Add per-IP/user rate limits, burst controls, and request budget metrics.

## Testing Gaps

- Current API tests validate happy paths but do not verify authz boundaries on mutating endpoints.
- No tests asserting secret redaction/non-exposure in loader responses.

## Suggested Minimal Remediation Order

1. Add auth + authorization to mutating routes.
2. Remove OTLP header exposure from browser loader.
3. Tighten CORS policy to explicit origins.
4. Sanitize client-facing error responses.
5. Add rate limiting and corresponding tests.
