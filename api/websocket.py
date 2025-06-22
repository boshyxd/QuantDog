import json

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        message_text = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except:
                # Connection might be closed
                pass

    async def broadcast_threat_update(self, threat_level: float, status: dict):
        await self.broadcast({
            "type": "threat_update",
            "data": {
                "threat_level": threat_level,
                "timestamp": status.get("timestamp"),
                "status": status.get("status"),
                "active_crypto": status.get("active_crypto"),
                "threshold": status.get("threshold")
            }
        })
