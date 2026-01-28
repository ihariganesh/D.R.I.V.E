from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    """
    WebSocket connection manager for real-time updates
    Used to push AI decisions, traffic events, and Green Wave activations to the dashboard
    """
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        import json
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()
