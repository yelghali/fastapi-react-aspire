# Copilot Instructions

This repository is set up to use **Aspire**. Aspire is an orchestrator for the entire application and takes care of configuring dependencies, building, and running the application. The resources that make up the application are defined in `apphost.cs` including application code and external dependencies.

## General Recommendations for Working with Aspire

1. Before making any changes, always run the apphost using `aspire run` and inspect the state of resources to make sure you are building from a known state.
2. Changes to the `apphost.cs` file will require a restart of the application to take effect.
3. Make changes incrementally and run the aspire application using the `aspire run` command to validate changes.
4. Use the Aspire dashboard to check the status of resources and debug issues via traces and logs.

## Running the Application

```bash
aspire run
```

If there is already an instance of the application running it will prompt to stop the existing instance. You only need to restart the application if code in `apphost.cs` is changed, but if you experience problems it can be useful to reset everything to the starting state.

## Checking Resources

Use the Aspire dashboard (<http://localhost:15888> by default) to:

- View all running resources
- Check resource health status
- View structured logs
- Inspect distributed traces

## Debugging Issues

The Aspire dashboard captures rich logs and telemetry for all resources. Use these diagnostic tools when debugging issues:

1. **Structured logs** — View logs from all services in one place
2. **Console logs** — Raw console output from each service
3. **Traces** — Distributed tracing across frontend and backend
4. **Metrics** — Application performance metrics

---

## Extending the Template

### Adding Azure Cosmos DB

To add Azure Cosmos DB for data persistence:

1. **Update `apphost.cs`**:

```csharp
#:package Aspire.Hosting.Azure.CosmosDB@13.1.0

// Add after builder creation
var cosmos = builder.AddAzureCosmosDB("cosmos");
var database = cosmos.AddCosmosDatabase("starterdb", "StarterDB");
var items = database.AddContainer("items", "/id");

// Update API resource
var api = builder.AddUvicornApp("api", "./api", "app.main:app")
    .WithUv()
    .WaitFor(cosmos)
    .WithEnvironment("APP_DATABASE_CONNECTION", cosmos.Resource.ConnectionStringExpression)
    .WithEnvironment("APP_DATABASE_NAME", database.Resource.DatabaseName)
    // ... rest of configuration
```

1. **Update `api/pyproject.toml`**:

```toml
dependencies = [
    # ... existing deps
    "azure-cosmos>=4.9.0",
    "azure-identity>=1.19.0",
]
```

1. **Create `api/app/common/cosmos.py`**:

```python
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential
from .settings import get_settings

class CosmosService:
    def __init__(self, container_name: str):
        settings = get_settings()
        self.client = CosmosClient(
            settings.database_connection,
            credential=DefaultAzureCredential(),
        )
        self.database = self.client.get_database_client(settings.database_name)
        self.container = self.database.get_container_client(container_name)
```

1. **Update `ItemService`** to use `CosmosService` instead of in-memory storage.

### Adding Azure Blob Storage

To add Azure Blob Storage for file uploads:

1. **Update `apphost.cs`**:

```csharp
#:package Aspire.Hosting.Azure.Storage@13.1.0

var storage = builder.AddAzureStorage("storage");
var blobs = storage.AddBlobContainer("uploads");

var api = builder.AddUvicornApp("api", "./api", "app.main:app")
    .WaitFor(blobs)
    .WithEnvironment("APP_STORAGE_CONNECTION", storage.Resource.BlobEndpoint)
    .WithEnvironment("APP_STORAGE_CONTAINER", blobs.Resource.Name)
    // ...
```

1. **Update `api/pyproject.toml`**:

```toml
dependencies = [
    # ... existing deps
    "azure-storage-blob>=12.24.0",
    "azure-identity>=1.19.0",
]
```

1. **Create `api/app/common/storage.py`** with `StorageService` class.

### Adding Azure AI Foundry

To add Azure AI capabilities:

1. **Create `infra/foundry.bicep`** with Azure AI Foundry resource definition.

2. **Update `apphost.cs`**:

```csharp
var foundry = builder.AddResource(
    new MicrosoftFoundryResource("foundry", "./infra/foundry.bicep"))
    .WithParameter("aiFoundryName", "myproject");

var api = builder.AddUvicornApp("api", "./api", "app.main:app")
    .WaitFor(foundry)
    .WithEnvironment("APP_FOUNDRY_ENDPOINT", foundry.Resource.AiProjectUrl)
    .WithEnvironment("APP_AZURE_OPENAI_ENDPOINT", foundry.Resource.OpenAIEndpoint)
    // ...
```

1. **Add `azure-ai-projects` to dependencies** and create `api/app/common/foundry.py`.

### Adding Authentication

For production authentication:

1. **Azure Easy Auth** — Configure Azure Container Apps with Microsoft Entra ID authentication
2. **API Key Auth** — Add middleware to validate API keys
3. **JWT Auth** — Use `python-jose` for JWT token validation

Example middleware pattern:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key
```

---

## Module Pattern

When adding new API modules, follow this structure:

```text
api/app/modules/newmodule/
├── __init__.py      # Export router and classes
├── schemas.py       # Pydantic models
├── service.py       # Business logic with @trace decorator
└── routes.py        # FastAPI endpoints
```

Register the router in `api/app/main.py`:

```python
from .modules.newmodule import newmodule_router
app.include_router(newmodule_router, prefix="/api")
```

---

## Adding Playwright E2E Testing

For end-to-end browser testing, add Playwright to the web project:

1. **Install Playwright**:

```bash
cd web
npm install -D @playwright/test
npx playwright install
```

1. **Create `web/playwright.config.ts`**:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.WEB_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

1. **Create `web/e2e/example.spec.ts`**:

```typescript
import { test, expect } from '@playwright/test';

test('home page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/FastAPI React Aspire/);
});

test('items page shows items from API', async ({ page }) => {
  await page.goto('/items');
  // Wait for items to load from API
  await expect(page.locator('text=Welcome Item')).toBeVisible();
});

test('can create a new item', async ({ page }) => {
  await page.goto('/items');
  await page.fill('input[placeholder="Item name"]', 'Test Item');
  await page.click('button:has-text("Add")');
  await expect(page.locator('text=Test Item')).toBeVisible();
});
```

1. **Add scripts to `web/package.json`**:

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```

1. **Update CI workflow** (`.github/workflows/ci.yml`):

```yaml
  e2e:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: [api, web]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - name: Install dependencies
        run: cd web && npm ci
      - name: Install Playwright browsers
        run: cd web && npx playwright install --with-deps
      - name: Run Playwright tests
        run: cd web && npm run test:e2e
```

**Note**: For full e2e testing with the API, run `aspire run` first, then use the Aspire-provided URLs.

---

## Official Documentation

Always prefer official documentation when available:

1. <https://aspire.dev>
2. <https://learn.microsoft.com/dotnet/aspire>
3. <https://nuget.org> (for specific integration package details)
4. <https://fastapi.tiangolo.com>
5. <https://reactrouter.com>
6. <https://playwright.dev>
