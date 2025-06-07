"""
WebSocket connection manager for real-time features.
"""

import json
import asyncio
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

from ..config.logging import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time features."""
    
    def __init__(self):
        # Store active connections by type
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "dashboard": set(),
            "payments": set(),
            "alerts": set(),
            "compliance": set(),
            "analytics": set()
        }
        
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, connection_type: str = "dashboard"):
        """Accept a new WebSocket connection."""
        try:
            await websocket.accept()
            
            if connection_type not in self.active_connections:
                self.active_connections[connection_type] = set()
                
            self.active_connections[connection_type].add(websocket)
            self.connection_metadata[websocket] = {
                "type": connection_type,
                "connected_at": datetime.utcnow(),
                "user_id": None  # Can be set after authentication
            }
            
            logger.info(f"WebSocket connected: {connection_type}, total: {len(self.active_connections[connection_type])}")
            
            # Send welcome message
            await self.send_personal_message(websocket, {
                "type": "connection_established",
                "connection_type": connection_type,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Connected to {connection_type} stream"
            })
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        try:
            # Find and remove from all connection types
            for connection_type, connections in self.active_connections.items():
                if websocket in connections:
                    connections.remove(websocket)
                    logger.info(f"WebSocket disconnected: {connection_type}, remaining: {len(connections)}")
                    break
                    
            # Remove metadata
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
                
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
            
    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
            
    async def broadcast_to_type(self, connection_type: str, message: Dict[str, Any]):
        """Broadcast a message to all connections of a specific type."""
        if connection_type not in self.active_connections:
            return
            
        disconnected = []
        connections = self.active_connections[connection_type].copy()
        
        for websocket in connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_type}: {e}")
                disconnected.append(websocket)
                
        # Clean up disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket)
            
    async def broadcast_dashboard_metrics(self, metrics: Dict[str, Any]):
        """Broadcast real-time metrics to dashboard connections."""
        message = {
            "type": "dashboard_metrics",
            "timestamp": datetime.utcnow().isoformat(),
            "data": metrics
        }
        await self.broadcast_to_type("dashboard", message)
        
    async def broadcast_payment_update(self, payment_data: Dict[str, Any]):
        """Broadcast payment updates to payment connections."""
        message = {
            "type": "payment_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": payment_data
        }
        await self.broadcast_to_type("payments", message)
        
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast alerts to alert connections."""
        message = {
            "type": "system_alert",
            "timestamp": datetime.utcnow().isoformat(),
            "data": alert_data
        }
        await self.broadcast_to_type("alerts", message)
        
    async def broadcast_compliance_event(self, compliance_data: Dict[str, Any]):
        """Broadcast compliance events to compliance connections."""
        message = {
            "type": "compliance_event",
            "timestamp": datetime.utcnow().isoformat(),
            "data": compliance_data
        }
        await self.broadcast_to_type("compliance", message)
        
    async def broadcast_analytics_update(self, analytics_data: Dict[str, Any]):
        """Broadcast analytics updates to analytics connections."""
        message = {
            "type": "analytics_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": analytics_data
        }
        await self.broadcast_to_type("analytics", message)
        
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections."""
        return {
            "total_connections": sum(len(connections) for connections in self.active_connections.values()),
            "connections_by_type": {
                conn_type: len(connections) 
                for conn_type, connections in self.active_connections.items()
            },
            "uptime": datetime.utcnow().isoformat()
        }


# Global WebSocket manager instance
websocket_manager = WebSocketManager() 