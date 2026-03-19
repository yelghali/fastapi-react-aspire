#!/usr/bin/env bash
# Check if the web app is running and accessible.
# Usage: ./check-app.sh [url]
# Returns exit 0 if reachable, exit 1 if not.

set -euo pipefail

URL="${1:-http://localhost:5173}"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "Checking if app is accessible at $URL ..."

for i in $(seq 1 "$MAX_RETRIES"); do
  if curl -sf -o /dev/null "$URL"; then
    echo "✓ App is running at $URL"
    exit 0
  fi
  echo "  Attempt $i/$MAX_RETRIES — waiting ${RETRY_INTERVAL}s..."
  sleep "$RETRY_INTERVAL"
done

echo "✗ App not reachable at $URL after $((MAX_RETRIES * RETRY_INTERVAL))s"
echo "  Run 'aspire run' to start the application."
exit 1
