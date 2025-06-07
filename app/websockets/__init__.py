"""
WebSocket support for real-time features.
"""

from .manager import websocket_manager
from .endpoints import router as websocket_router

__all__ = ["websocket_manager", "websocket_router"] 