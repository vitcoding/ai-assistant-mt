from fastapi import WebSocket


class ConnectionManager:
    """Web socket connection manager."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Creates a connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Removes the connection."""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Sends a personal message."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Sends messages using the existing connections."""
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()
