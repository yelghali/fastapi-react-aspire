---
description: "Run Playwright MCP browser tests on the web UI. Use to test pages, forms, navigation, and verify frontend behavior."
agent: "e2e-tester"
tools: [microsoft/playwright-mcp/*, execute, read, search, todo]
argument-hint: "Page or feature to test (e.g. 'items page form submission')"
---

Test the following in the running web app using Playwright MCP browser tools:

**Target**: $input

## Instructions

1. Verify the app is running at `http://localhost:5173` (check with `lsof -i :5173`). If not, start it with `aspire run` and wait for readiness.
2. Use `browser_navigate` → `browser_snapshot` → interact → `browser_snapshot` to test.
3. Use refs from snapshots to target clicks and form fills.
4. Track each test scenario in the todo list.
5. Produce a summary table at the end:

| # | Test | Page | Result | Notes |
|---|------|------|--------|-------|

Follow the [playwright-mcp-testing skill](.github/skills/playwright-mcp-testing/SKILL.md) for patterns and tool reference.
