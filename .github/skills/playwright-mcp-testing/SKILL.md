---
name: playwright-mcp-testing
description: 'Write and run Playwright MCP browser tests against the running web UI. Use when: adding UI tests, verifying frontend behavior, testing page interactions, checking visual elements, running e2e browser tests with Playwright MCP tools.'
argument-hint: 'Describe the page or feature to test (e.g. "test the items page create form")'
---

# Playwright MCP UI Testing

Write concise, interaction-based browser tests using the Playwright MCP server tools — no test files needed.

## Prerequisites

The Playwright MCP server must be configured in `.vscode/mcp.json` (already present in this repo).

## Procedure

### 1. Start the Application

Run the full stack with Aspire so both API and web are up:

```bash
aspire run
```

Wait until the Aspire dashboard (`http://localhost:15888`) shows all resources healthy.
The web app runs at **`http://localhost:5173`** by default.

> If `aspire run` is already running, skip this step. Check with `lsof -i :5173`.

### 2. Open the Page Under Test

Use `browser_navigate` to go to the target page:

- Home: `http://localhost:5173/`
- Items: `http://localhost:5173/items`
- Projects: `http://localhost:5173/projects`

### 3. Take a Snapshot

Use `browser_snapshot` to capture the current accessibility tree. This is the primary way to understand what's on the page — use it instead of screenshots for assertions.

### 4. Write Assertions via Interactions

Test by interacting and observing. Use this loop:

1. **`browser_snapshot`** — read current state
2. **`browser_click`** / **`browser_fill_form`** / **`browser_press_key`** — interact
3. **`browser_snapshot`** — verify result

### 5. Common Test Patterns

#### Verify page loads correctly
```
→ browser_navigate to the page URL
→ browser_snapshot
→ Assert: heading, key elements present in snapshot
```

#### Fill and submit a form
```
→ browser_navigate to the page with the form
→ browser_fill_form with field values (use CSS selectors or labels)
→ browser_click the submit button (use text= or role= ref from snapshot)
→ browser_snapshot
→ Assert: success message or new item visible
```

#### Navigate between pages
```
→ browser_navigate to starting page
→ browser_click a navigation link (ref from snapshot)
→ browser_snapshot
→ Assert: new page content visible
```

#### Check element visibility
```
→ browser_snapshot
→ Look for the element text/role in the accessibility tree output
```

### 6. Report Results

After each test sequence, summarize:
- **Page tested**: URL
- **Actions performed**: list of interactions
- **Result**: PASS / FAIL with details

## Tool Quick Reference

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Go to a URL |
| `browser_snapshot` | Get accessibility tree (use for assertions) |
| `browser_click` | Click an element (by ref from snapshot) |
| `browser_fill_form` | Fill form fields |
| `browser_press_key` | Press keyboard keys (Enter, Tab, etc.) |
| `browser_hover` | Hover over an element |
| `browser_select_option` | Select dropdown option |
| `browser_take_screenshot` | Visual screenshot (use sparingly) |
| `browser_navigate_back` | Go back |
| `browser_wait_for` | Wait for text/element to appear |

## App Pages & Key Elements

| Page | URL | Key Elements |
|------|-----|-------------|
| Home | `/` | Heading "FastAPI + React + Aspire", nav links (Items Demo, Projects, API Docs), feature cards |
| Items | `/items` | Heading "Items", form (name input, description input, Add button), Refresh button, item list |
| Projects | `/projects` | Heading, Refresh button, project list |

## Guidelines

- **Prefer `browser_snapshot`** over `browser_take_screenshot` — snapshots are machine-readable and faster.
- **Use refs from snapshots** to target clicks — the snapshot output includes `ref="N"` attributes.
- **One test scenario per interaction sequence** — keep tests focused.
- **Always start with `browser_navigate`** — don't assume a prior page state.
- **Close the browser** with `browser_close` when done with all tests.
