from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from api.routes import router, start_honeypot_monitoring, stop_honeypot_monitoring
from api.websocket import ConnectionManager
from core.monitoring import ThreatMonitor


manager = ConnectionManager()
threat_monitor = ThreatMonitor()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting QuantDog API...")
    threat_task = asyncio.create_task(threat_monitor.start_monitoring(manager))
    honeypot_task = await start_honeypot_monitoring()
    print("✅ All systems online!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down QuantDog API...")
    threat_monitor.stop_monitoring()
    await stop_honeypot_monitoring()
    
    threat_task.cancel()
    try:
        await threat_task
    except asyncio.CancelledError:
        pass
    print("✅ Shutdown complete!")


app = FastAPI(
    title="QuantDog API",
    description="Quantum Threat Detection and Cryptographic Routing System",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "QuantDog API is running",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Process commands if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)