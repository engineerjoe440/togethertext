################################################################################
"""
WordWall - Simple, Self-Hosted Collaborative Word Cloud Generator.

(c) 2025 | Stanley Solutions | Joe Stanley
License: MIT
"""
################################################################################

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from . import walls, words
from ..session import Manager, WebSocketManager

router = APIRouter(prefix="/api/v1")

router.include_router(router=walls.router)
router.include_router(router=words.router)

manager = Manager()
sockets = WebSocketManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Song Info Streaming Endpoint."""
    await sockets.connect(websocket)
    try:
        await websocket.send_json(
            {"message": "Status Channel Open."}
        )
        while True:
            # Listen for Incoming Data from Socket
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        # Drop the Connection
        sockets.disconnect(websocket)
