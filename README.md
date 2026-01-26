# FastAPI React Aspire Starter

A minimal, production-ready starter template featuring **FastAPI** backend with OpenTelemetry tracing, **React Router v7** frontend with Vite and Tailwind CSS, orchestrated by **.NET Aspire** for seamless local development and Azure deployment.

![CI](https://github.com/sethjuarez/fastapi-react-aspire/actions/workflows/ci.yml/badge.svg)

## ✨ Features

- **FastAPI Backend** — Python 3.13, async support, automatic API docs, Pydantic validation
- **OpenTelemetry Tracing** — Distributed tracing across frontend and backend, visible in Aspire dashboard
- **React Router v7** — Modern React with SSR, file-based routing, TypeScript
- **Tailwind CSS** — Utility-first CSS with dark mode support
- **Vite** — Fast dev server with HMR and optimized production builds
- **.NET Aspire** — Local orchestration with dashboard, environment management, and Azure deployment
- **GitHub Actions** — CI workflow for testing, linting, and Docker builds

## 📋 Prerequisites

- [.NET SDK 10.0+](https://dotnet.microsoft.com/download)
- [Node.js 22+](https://nodejs.org/)
- [Python 3.13+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — Fast Python package manager
- [Aspire CLI](https://aspire.dev/get-started/install-cli/)

```bash
# Install Aspire CLI (choose one)
curl -sSL https://aspire.dev/install.sh | bash    # Linux/macOS
irm https://aspire.dev/install.ps1 | iex          # Windows PowerShell
```

## 🚀 Quick Start

```bash
# Clone the template
git clone https://github.com/sethjuarez/fastapi-react-aspire
cd fastapi-react-aspire

# Run with Aspire (installs dependencies automatically)
aspire run
```

This will:

1. Install Python dependencies via `uv`
2. Install Node.js dependencies via `npm`
3. Start the FastAPI backend
4. Start the React frontend with API proxy
5. Open the Aspire dashboard for tracing and logs

**Access points:**

- **Web App**: <http://localhost:5173> (or port shown in Aspire)
- **API Docs**: <http://localhost:8000/docs>
- **Aspire Dashboard**: <http://localhost:15888>

## 📁 Project Structure

```text
fastapi-react-aspire/
├── apphost.cs              # Aspire orchestration
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── telemetry.py    # OpenTelemetry setup
│   │   ├── common/         # Shared utilities
│   │   │   ├── settings.py # Pydantic configuration
│   │   │   └── tracer.py   # @trace decorator
│   │   └── modules/
│   │       └── items/      # Example CRUD module
│   │           ├── schemas.py
│   │           ├── service.py
│   │           └── routes.py
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── web/                    # React frontend
│   ├── app/
│   │   ├── root.tsx        # Root layout + telemetry
│   │   ├── routes.ts       # Route definitions
│   │   └── routes/
│   │       ├── home.tsx    # Landing page
│   │       └── items.tsx   # API demo page
│   ├── lib/
│   │   └── telemetry.ts    # Browser OpenTelemetry
│   ├── vite.config.ts      # Vite + proxy config
│   ├── server.js           # Production server
│   ├── package.json
│   └── Dockerfile
└── .github/workflows/
    └── ci.yml              # CI pipeline
```

## 🛠️ Development

### Running Standalone

**API only:**

```bash
cd api
uv sync
uv run uvicorn app.main:app --reload
```

**Web only** (requires API running):

```bash
cd web
npm install
npm run dev
```

### Testing

```bash
# API tests
cd api
uv run pytest

# Web type checking
cd web
npm run typecheck
```

### Linting

```bash
# API
cd api
uv run ruff check app/
uv run mypy app/

# Web
cd web
npm run lint
```

## 🚢 Deployment

### Deploy to Azure

```bash
# One-command deployment to Azure Container Apps
aspire deploy
```

This will:

1. Build Docker images for both API and Web
2. Push to Azure Container Registry
3. Deploy to Azure Container Apps
4. Configure environment variables and networking

### Manual Docker Build

```bash
# Build API
docker build -t my-api ./api

# Build Web with version
docker build --build-arg BUILD_VERSION=$(git rev-parse --short HEAD) -t my-web ./web
```

## 🔧 Configuration

### Environment Variables

The API uses `APP_` prefixed environment variables (managed by Aspire):

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `APP_DATABASE_CONNECTION` | Database connection string | `""` |
| `APP_DATABASE_NAME` | Database name | `"StarterDB"` |
| `APP_STORAGE_CONNECTION` | Azure Storage connection | `""` |
| `APP_FOUNDRY_ENDPOINT` | Azure AI Foundry endpoint | `""` |

### Adding Azure Services

See [AGENTS.md](AGENTS.md) for instructions on adding:

- Azure Cosmos DB
- Azure Blob Storage
- Azure AI Foundry

## 📚 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Router v7](https://reactrouter.com/)
- [.NET Aspire](https://learn.microsoft.com/dotnet/aspire/)
- [OpenTelemetry](https://opentelemetry.io/)
- [Tailwind CSS](https://tailwindcss.com/)

## 📄 License

MIT
