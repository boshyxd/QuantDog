# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

QuantDog uses a microservices architecture:
- **Backend**: FastAPI for async API and WebSocket support
- **Frontend**: React with TypeScript for responsive UI
- **Real-time**: WebSocket for live threat monitoring

## Essential Commands

This project uses UV for ultra-fast Python package management and npm for frontend.

### Backend Commands (Python/FastAPI)
```bash
# Development setup
make dev          # Full setup: UV, dependencies, .env file
make install      # Install dependencies with UV

# Running the backend
make run-api      # Start FastAPI (http://localhost:8000)
make run-api-prod # Production mode
uv run uvicorn api:app --reload  # Direct command

# Code quality
make lint         # Run ruff linter with auto-fix
make format       # Format code with ruff (Black-compatible)
make pre-commit   # Run lint and tests before committing

# Testing
make test         # Run pytest with coverage
uv run pytest tests/ -v  # Run tests with verbose output

# Dependency management
make update       # Update all dependencies
make deps         # Show dependency tree
make lock         # Create production lockfile
uv sync           # Sync dependencies from pyproject.toml

# Cleanup
make clean        # Remove cache, logs, coverage reports
make clean-all    # Clean + remove UV cache
```

### Frontend Commands (React/TypeScript)
```bash
# Navigate to frontend
cd frontend

# Development
npm install       # Install dependencies
npm start         # Start dev server (http://localhost:3000)
npm test          # Run tests
npm run lint      # Run linter

# Production
npm run build     # Build for production
npm run preview   # Preview production build
```

### Running Both Services
```bash
# Option 1: Two terminals
# Terminal 1:
make run-api

# Terminal 2:
make run-frontend

# Option 2: Single command (background process)
make run-all
```

## API Architecture

### Core Endpoints (api/routes.py)
- `GET /api/v1/status` - Current threat level and crypto method
- `POST /api/v1/simulate/attack` - Simulate quantum attack
- `POST /api/v1/simulate/reduce-threat` - Reduce threat level
- `GET /api/v1/transactions` - Recent transactions
- `GET /api/v1/honeypots` - Honeypot status
- `GET /api/v1/metrics` - System metrics
- `WebSocket /ws` - Real-time threat updates

### WebSocket Events
```javascript
// Frontend connection example
const ws = new WebSocket('ws://localhost:8000/ws');

// Message types:
{
  type: "threat_update",
  data: {
    threat_level: 45.2,
    status: "medium",
    active_crypto: "classical",
    threshold: 50.0,
    timestamp: "2025-06-21T12:00:00Z"
  }
}
```

## Project Structure

```
QuantDog/
├── api/                    # FastAPI specific
│   ├── __init__.py
│   ├── routes.py          # API endpoints
│   ├── websocket.py       # WebSocket manager
│   └── models.py          # Pydantic models
├── core/                   # Business logic (shared)
│   ├── __init__.py
│   ├── threat_detector.py # Threat detection logic
│   ├── router.py          # Crypto routing engine
│   └── monitoring.py      # Threat monitoring + WebSocket
├── services/              # External integrations (placeholders)
│   ├── __init__.py
│   ├── blockchain.py      # Blockchain integration
│   ├── crypto.py          # Cryptography implementation
│   └── quantum.py         # Quantum computing integration
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks (WebSocket, etc)
│   │   ├── services/      # API clients
│   │   └── types/         # TypeScript types
│   └── package.json
├── api.py                 # FastAPI entry point
├── app.py                 # Streamlit app (legacy)
└── Makefile               # Development commands
```

## Development Workflow

1. **Before Making Changes**:
   - Check current git status and branch
   - Run `make lint` to ensure clean baseline
   - Ensure both backend and frontend are running

2. **Backend Development**:
   - Follow existing patterns in api/, core/, services/
   - Use type hints and Pydantic models
   - Test endpoints at http://localhost:8000/docs

3. **Frontend Development**:
   - Follow React best practices
   - Use TypeScript for type safety
   - Component structure in src/components/
   - API calls through src/services/

4. **Code Style**:
   - Backend: Ruff enforces Black-compatible formatting
   - Frontend: ESLint + Prettier
   - No comments in code generation

## Configuration

Primary configuration through environment variables (see `.env.example`):
- `QUANTUM_THREAT_LOW/MEDIUM/HIGH`: Threat thresholds (default: 30/50/70)
- `HONEYPOT_CHECK_INTERVAL`: Monitoring frequency in seconds
- Blockchain RPC endpoints for mainnet/testnet

Frontend configuration in `frontend/.env`:
- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000)
- `REACT_APP_WS_URL`: WebSocket URL (default: ws://localhost:8000/ws)

## Important Notes

- Services layer contains skeleton implementations that need development
- The current implementation simulates threat levels for demo purposes
- Quantum frameworks (Qiskit) are installed but not yet integrated
- Post-quantum cryptography is placeholder text only

## Claude Code Guidelines

- **Code Generation**:
  - Never generate comments with code
  - Focus on clean, self-documenting code
  - Use type hints and docstrings for documentation
  - Do not use emojis with code or in any documentation