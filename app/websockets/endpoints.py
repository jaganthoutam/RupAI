"""
WebSocket endpoints for real-time communication.
"""

import asyncio
import json
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from datetime import datetime

from .manager import websocket_manager
from ..config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates."""
    await websocket_manager.connect(websocket, "dashboard")
    
    try:
        # Start sending periodic dashboard updates
        dashboard_task = asyncio.create_task(send_dashboard_updates(websocket))
        
        # Listen for client messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle client requests
                if message.get("type") == "request_metrics":
                    await send_current_metrics(websocket)
                elif message.get("type") == "ping":
                    await websocket_manager.send_personal_message(websocket, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message(websocket, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error in dashboard WebSocket: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        dashboard_task.cancel()
        websocket_manager.disconnect(websocket)


@router.websocket("/ws/payments")
async def websocket_payments(websocket: WebSocket):
    """WebSocket endpoint for real-time payment updates."""
    await websocket_manager.connect(websocket, "payments")
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle payment-specific requests
                if message.get("type") == "subscribe_payment":
                    payment_id = message.get("payment_id")
                    if payment_id:
                        await websocket_manager.send_personal_message(websocket, {
                            "type": "subscription_confirmed",
                            "payment_id": payment_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in payments WebSocket: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket)


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time system alerts."""
    await websocket_manager.connect(websocket, "alerts")
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle alert-specific requests
                if message.get("type") == "subscribe_alerts":
                    severity = message.get("severity", "all")
                    await websocket_manager.send_personal_message(websocket, {
                        "type": "alert_subscription_confirmed",
                        "severity_filter": severity,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in alerts WebSocket: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket)


@router.websocket("/ws/compliance")
async def websocket_compliance(websocket: WebSocket):
    """WebSocket endpoint for real-time compliance events."""
    await websocket_manager.connect(websocket, "compliance")
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle compliance-specific requests
                if message.get("type") == "subscribe_compliance":
                    event_types = message.get("event_types", ["all"])
                    await websocket_manager.send_personal_message(websocket, {
                        "type": "compliance_subscription_confirmed",
                        "event_types": event_types,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in compliance WebSocket: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket)


@router.websocket("/ws/analytics")
async def websocket_analytics(websocket: WebSocket):
    """WebSocket endpoint for real-time analytics updates."""
    await websocket_manager.connect(websocket, "analytics")
    
    try:
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle analytics-specific requests
                if message.get("type") == "subscribe_analytics":
                    metrics = message.get("metrics", ["revenue", "transactions"])
                    await websocket_manager.send_personal_message(websocket, {
                        "type": "analytics_subscription_confirmed",
                        "metrics": metrics,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in analytics WebSocket: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        websocket_manager.disconnect(websocket)


async def send_dashboard_updates(websocket: WebSocket):
    """Send periodic dashboard updates to a WebSocket connection."""
    try:
        while True:
            await asyncio.sleep(5)  # Send updates every 5 seconds
            
            # Generate mock real-time metrics
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_health": {
                    "cpu_usage": 45.2,
                    "memory_usage": 67.8,
                    "disk_usage": 34.1,
                    "network_io": {"in": 1024, "out": 2048}
                },
                "payment_metrics": {
                    "transactions_per_minute": 127,
                    "success_rate": 99.2,
                    "average_response_time": 145,
                    "active_sessions": 1847
                },
                "financial_metrics": {
                    "revenue_today": 45678.90,
                    "transactions_today": 2341,
                    "pending_payments": 23,
                    "failed_payments": 5
                }
            }
            
            await websocket_manager.send_personal_message(websocket, {
                "type": "dashboard_metrics",
                "data": metrics
            })
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Error sending dashboard updates: {e}")


async def send_current_metrics(websocket: WebSocket):
    """Send current system metrics to a WebSocket connection."""
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": "operational",
            "uptime": "24h 15m 32s",
            "active_connections": websocket_manager.get_connection_stats(),
            "services": {
                "database": "healthy",
                "cache": "healthy",
                "queue": "healthy",
                "api": "healthy"
            }
        }
        
        await websocket_manager.send_personal_message(websocket, {
            "type": "current_metrics",
            "data": metrics
        })
        
    except Exception as e:
        logger.error(f"Error sending current metrics: {e}") 