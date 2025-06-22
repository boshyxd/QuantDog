# QuantDog

QuantDog is an intelligent quantum threat detection and adaptive cryptographic routing platform that protects cryptocurrency transactions from quantum computer attacks.

## Architecture

QuantDog now uses a modern microservices architecture:
- **Backend**: FastAPI for high-performance async API
- **Frontend**: React with TypeScript for responsive UI
- **Real-time**: WebSocket connections for live threat monitoring

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/boshyxd/QuantDog.git
   cd QuantDog
   ```

2. **Backend Setup**
   ```bash
   # Install UV (ultra-fast Python package manager)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install Python dependencies
   make install
   
   # Copy environment variables
   cp .env.example .env
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

#### Option 1: Run both services (recommended)
```bash
# Terminal 1 - Backend API
make run-api

# Terminal 2 - Frontend
make run-frontend
```

#### Option 2: Run services individually
```bash
# Backend API (http://localhost:8000)
uv run uvicorn api:app --reload

# Frontend (http://localhost:3000)
cd frontend && npm start
```

## API Documentation

Once the backend is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **API schema**: http://localhost:8000/openapi.json

## Development

### Backend Commands
```bash
make install    # Install dependencies with UV
make run-api    # Run FastAPI backend
make lint       # Run linter (auto-fix enabled)
make format     # Format code
make test       # Run tests with coverage
make update     # Update all dependencies
make clean      # Clean cache files
```

### Frontend Commands
```bash
cd frontend
npm start       # Start development server
npm test        # Run tests
npm run build   # Build for production
npm run lint    # Run linter
```

### Project Structure
```
QuantDog/
├── api/                # FastAPI specific modules
│   ├── routes.py       # API endpoints
│   ├── websocket.py    # WebSocket handlers
│   └── models.py       # Pydantic models
├── core/               # Business logic (shared)
│   ├── threat_detector.py
│   ├── router.py
│   └── monitoring.py
├── services/           # External integrations
│   ├── blockchain.py
│   ├── crypto.py
│   └── quantum.py
├── frontend/           # React application
│   ├── src/
│   ├── public/
│   └── package.json
├── main.py             # FastAPI entry point
└── Makefile            # Development commands
```

## Configuration

Key environment variables in `.env`:
- `QUANTUM_THREAT_LOW/MEDIUM/HIGH`: Threat level thresholds
- `HONEYPOT_CHECK_INTERVAL`: How often to check honeypots (seconds)
- `ETHEREUM_RPC_URL`: Ethereum RPC endpoint
- `BITCOIN_RPC_URL`: Bitcoin RPC endpoint

## WebSocket Events

The API broadcasts real-time threat updates via WebSocket:
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Listen for threat updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'threat_update') {
    console.log('Threat level:', data.data.threat_level);
    console.log('Active crypto:', data.data.active_crypto);
  }
};
```

## Testing

### Backend Tests
```bash
make test
# Or: uv run pytest tests/ -v --cov=core --cov=services --cov=utils
```

### Frontend Tests
```bash
cd frontend && npm test
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### Module Not Found
```bash
# Reinstall backend dependencies
uv sync --reinstall

# Reinstall frontend dependencies
cd frontend && rm -rf node_modules && npm install
```

### CORS Issues
Ensure the backend is running before starting the frontend. The API is configured to accept requests from localhost:3000 and localhost:5173.