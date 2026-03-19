---
description: Generate focused FastAPI unit tests with meaningful coverage scope
agent: "FastAPI Unit Test Specialist"
argument-hint: "Describe the FastAPI module, selected code, expected behavior, and edge cases to cover."
---/

# Generate FastAPI Unit Tests

Use the selected FastAPI code, current file, or module context to generate or improve unit tests.

## Scope

Create tests that cover the most important behavior for the target FastAPI module:

- Route success paths and response shape
- Validation failures and 422 responses
- Not-found paths and 404 responses
- Query parameter handling and pagination when present
- Dependency injection and dependency overrides
- Service behavior with mocked external calls
- Authorization failures when the module already has auth or permission checks

Keep the scope focused on unit-level coverage. Do not add end-to-end or broad integration tests unless the request explicitly asks for them.

## Expectations

- Follow the existing test style in the repository
- Prefer async tests for async routes and services
- Use mocks for external APIs, storage, databases, and other side effects
- Keep each test small, deterministic, and focused on one behavior
- Add or improve fixtures only when they reduce duplication or clarify the tests
- If production code needs a tiny testability adjustment, keep it minimal and explain why

## What to Produce

1. Add or update the relevant test file(s)
2. Include meaningful edge cases, not just the happy path
3. Run the narrowest useful test command first
4. Summarize what was covered and call out any remaining gaps

## Good Coverage Targets

Use these as guidance when the code supports them:

- Route: success, validation error, missing resource, dependency failure
- Service: create, read, update, delete, filtering, empty result, external error
- API contracts: required fields, optional fields, default values, response ordering
- External calls: mocked response, timeout/error path, retry-safe behavior if applicable

## Output Format

Return a concise summary with:

- Files changed
- Tests added or updated
- Scenarios covered
- Commands run and results
- Any test gaps that still remain
