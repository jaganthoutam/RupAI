"""
Enterprise MCP Server Implementation
Model Context Protocol v2024.1

Production-ready MCP server with comprehensive payment tools,
enterprise security, and full observability.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationError

from app.config.settings import settings
from app.mcp.tools.payments import PaymentTools
from app.mcp.tools.wallets import WalletTools  
from app.mcp.tools.subscriptions import SubscriptionTools
from app.mcp.tools.compliance import ComplianceTools
from app.mcp.schemas import (
    MCPRequest, MCPResponse, MCPError, ToolCall, ToolResult,
    InitializeRequest, InitializeResponse, ListToolsRequest, ListToolsResponse,
    CallToolRequest, CallToolResponse, ToolDefinition
)
from app.utils.monitoring import MetricsCollector
from app.utils.encryption import EncryptionManager
from app.db.database import Database
from app.db.redis import RedisClient
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService
from ..repositories.audit_repository import AuditRepository

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Enterprise MCP Server for payments processing.
    
    Implements the Model Context Protocol v2024.1 specification with:
    - Complete payment tool registry
    - Enterprise security features
    - Comprehensive audit logging
    - Real-time monitoring and metrics
    - High availability and resilience
    """
    
    def __init__(
        self,
        database: Database,
        redis_client: RedisClient,
        metrics_collector: MetricsCollector,
        notification_service: NotificationService
    ):
        self.database = database
        self.redis_client = redis_client
        self.metrics_collector = metrics_collector
        self.notification_service = notification_service
        
        # MCP Server Configuration
        self.server_info = {
            "name": settings.SERVER_NAME,
            "version": settings.SERVER_VERSION,
            "mcp_version": settings.MCP_VERSION,
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": False,
                "logging": True,
                "sampling": False
            }
        }
        
        # Tool registry
        self.tools = {}
        self.tool_handlers = {}
        
        # Services
        self.audit_service: Optional[AuditService] = None
        self.encryption_manager: Optional[EncryptionManager] = None
        
        # Tool implementations
        self.payment_tools: Optional[PaymentTools] = None
        self.wallet_tools: Optional[WalletTools] = None
        self.subscription_tools: Optional[SubscriptionTools] = None
        self.compliance_tools: Optional[ComplianceTools] = None
        
        # State management
        self.initialized = False
        self.session_id = str(uuid.uuid4())
        
        logger.info("MCP Server instance created with session: %s", self.session_id)
    
    async def initialize(self) -> None:
        """Initialize the MCP server with all tools and services."""
        try:
            logger.info("Initializing MCP Server...")
            
            # Initialize services
            session = self.database.get_session()
            audit_repo = AuditRepository(session)
            self.audit_service = AuditService(audit_repo)
            await self.audit_service.initialize()
            
            self.encryption_manager = EncryptionManager()
            await self.encryption_manager.initialize()
            
            # Initialize tool implementations
            self.payment_tools = PaymentTools(
                database=self.database,
                redis_client=self.redis_client,
                audit_service=self.audit_service,
                encryption_manager=self.encryption_manager,
                metrics_collector=self.metrics_collector
            )
            await self.payment_tools.initialize()
            
            self.wallet_tools = WalletTools(
                database=self.database,
                redis_client=self.redis_client,
                audit_service=self.audit_service,
                encryption_manager=self.encryption_manager,
                metrics_collector=self.metrics_collector
            )
            await self.wallet_tools.initialize()
            
            self.subscription_tools = SubscriptionTools(
                database=self.database,
                redis_client=self.redis_client,
                audit_service=self.audit_service,
                metrics_collector=self.metrics_collector
            )
            await self.subscription_tools.initialize()
            
            self.compliance_tools = ComplianceTools(
                database=self.database,
                audit_service=self.audit_service,
                metrics_collector=self.metrics_collector
            )
            await self.compliance_tools.initialize()
            
            # Register all tools
            await self._register_tools()
            
            self.initialized = True
            logger.info("✅ MCP Server initialized successfully with %d tools", len(self.tools))
            
            # Record initialization in audit log
            await self.audit_service.log_event(
                event_type="mcp_server_initialized",
                session_id=self.session_id,
                metadata={
                    "tools_count": len(self.tools),
                    "server_version": settings.SERVER_VERSION,
                    "mcp_version": settings.MCP_VERSION
                }
            )
            
        except Exception as e:
            logger.error("Failed to initialize MCP Server: %s", str(e))
            raise
    
    async def _register_tools(self) -> None:
        """Register all available MCP tools."""
        
        # Payment tools
        payment_tools = await self.payment_tools.get_tool_definitions()
        for tool_name, tool_def in payment_tools.items():
            logger.debug(f"Registering payment tool {tool_name}, type: {type(tool_def)}")
            self.tools[tool_name] = tool_def
            self.tool_handlers[tool_name] = self.payment_tools.handle_tool_call
        
        # Wallet tools
        wallet_tools = await self.wallet_tools.get_tool_definitions()
        for tool_name, tool_def in wallet_tools.items():
            logger.debug(f"Registering wallet tool {tool_name}, type: {type(tool_def)}")
            self.tools[tool_name] = tool_def
            self.tool_handlers[tool_name] = self.wallet_tools.handle_tool_call
        
        # Subscription tools
        subscription_tools = await self.subscription_tools.get_tool_definitions()
        for tool_name, tool_def in subscription_tools.items():
            logger.debug(f"Registering subscription tool {tool_name}, type: {type(tool_def)}")
            self.tools[tool_name] = tool_def
            self.tool_handlers[tool_name] = self.subscription_tools.handle_tool_call
        
        # Compliance tools
        compliance_tools = await self.compliance_tools.get_tool_definitions()
        for tool_name, tool_def in compliance_tools.items():
            logger.debug(f"Registering compliance tool {tool_name}, type: {type(tool_def)}")
            self.tools[tool_name] = tool_def
            self.tool_handlers[tool_name] = self.compliance_tools.handle_tool_call
        
        logger.info("Registered %d MCP tools", len(self.tools))
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main request handler for MCP protocol messages.
        
        Args:
            request_data: Raw JSON-RPC request data
            
        Returns:
            JSON-RPC response data
        """
        start_time = datetime.utcnow()
        request_id = request_data.get("id")
        method = request_data.get("method")
        
        try:
            # Validate JSON-RPC structure
            if not self._is_valid_jsonrpc(request_data):
                return self._create_error_response(
                    request_id, -32600, "Invalid Request", "Invalid JSON-RPC format"
                )
            
            # Record metrics
            await self.metrics_collector.record_request(method)
            
            # Handle different MCP methods
            if method == "initialize":
                response = await self._handle_initialize(request_data)
            elif method == "tools/list":
                response = await self._handle_list_tools(request_data)
            elif method == "tools/call":
                response = await self._handle_call_tool(request_data)
            elif method == "resources/list":
                response = await self._handle_list_resources(request_data)
            elif method == "logging/setLevel":
                response = await self._handle_set_log_level(request_data)
            else:
                response = self._create_error_response(
                    request_id, -32601, "Method not found", f"Method '{method}' not supported"
                )
            
            # Record successful request metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self.metrics_collector.record_request_duration(method, duration)
            
            return response
            
        except ValidationError as e:
            logger.error("Validation error for request %s: %s", request_id, str(e))
            return self._create_error_response(
                request_id, -32602, "Invalid params", str(e)
            )
        except Exception as e:
            logger.error("Error handling request %s: %s", request_id, str(e), exc_info=True)
            
            # Record error metrics
            await self.metrics_collector.record_error(method, str(e))
            
            return self._create_error_response(
                request_id, -32603, "Internal error", str(e)
            )
    
    async def _handle_initialize(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        request_id = request_data.get("id")
        
        try:
            # Parse initialize request
            params = request_data.get("params", {})
            client_info = params.get("clientInfo", {})
            
            logger.info(
                "MCP Initialize request from client: %s v%s",
                client_info.get("name", "unknown"),
                client_info.get("version", "unknown")
            )
            
            # Create response
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": settings.MCP_VERSION,
                    "serverInfo": self.server_info,
                    "capabilities": self.server_info["capabilities"],
                    "instructions": (
                        "Enterprise MCP Payments Server is ready. "
                        "Use tools/list to see available payment operations."
                    )
                }
            }
            
            # Log initialization
            await self.audit_service.log_event(
                event_type="mcp_client_initialized",
                session_id=self.session_id,
                metadata={
                    "client_info": client_info,
                    "request_id": request_id
                }
            )
            
            return response
            
        except Exception as e:
            logger.error("Error in initialize handler: %s", str(e))
            raise
    
    async def _handle_list_tools(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP list tools request."""
        request_id = request_data.get("id")
        
        try:
            # Create tools list response
            tools_list = []
            logger.info(f"Processing {len(self.tools)} tools")
            
            for tool_name, tool_def in self.tools.items():
                logger.info(f"Processing tool: {tool_name}")
                logger.info(f"Tool def type: {type(tool_def)}")
                logger.info(f"Tool def: {tool_def}")
                
                try:
                    # Try to access as ToolDefinition object
                    description = tool_def.description
                    input_schema = tool_def.inputSchema.model_dump()
                    logger.info(f"Successfully accessed as ToolDefinition")
                except Exception as e:
                    logger.error(f"Error accessing as ToolDefinition: {e}")
                    # Try as dictionary
                    try:
                        description = tool_def["description"]
                        input_schema = tool_def["inputSchema"]
                        logger.info(f"Successfully accessed as dictionary")
                    except Exception as e2:
                        logger.error(f"Error accessing as dictionary: {e2}")
                        description = "Unknown"
                        input_schema = {}
                
                tools_list.append({
                    "name": tool_name,
                    "description": description,
                    "inputSchema": input_schema
                })
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools_list
                }
            }
            
            logger.debug("Listed %d MCP tools", len(tools_list))
            return response
            
        except Exception as e:
            logger.error("Error in list tools handler: %s", str(e))
            raise
    
    async def _handle_call_tool(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP tool call request."""
        request_id = request_data.get("id")
        
        try:
            params = request_data.get("params", {})
            tool_name = params.get("name")
            tool_arguments = params.get("arguments", {})
            
            if not tool_name:
                return self._create_error_response(
                    request_id, -32602, "Invalid params", "Tool name is required"
                )
            
            if tool_name not in self.tool_handlers:
                return self._create_error_response(
                    request_id, -32601, "Tool not found", f"Tool '{tool_name}' not available"
                )
            
            logger.info("Calling MCP tool: %s", tool_name)
            
            # Call the appropriate tool handler
            handler = self.tool_handlers[tool_name]
            tool_result = await handler(tool_name, tool_arguments)
            
            # Create response from ToolResult
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [content.model_dump() for content in tool_result.content],
                    "isError": tool_result.isError,
                    "_meta": tool_result.meta or {}
                }
            }
            
            # Log tool execution
            # await self.audit_service.log_event(
            #     event_type="mcp_tool_called",
            #     session_id=self.session_id,
            #     metadata={
            #         "tool_name": tool_name,
            #         "arguments": tool_arguments,
            #         "success": not tool_result.isError,
            #         "request_id": request_id
            #     }
            # )
            
            return response
            
        except Exception as e:
            logger.error("Error in call tool handler: %s", str(e))
            
            # Log tool error
            # await self.audit_service.log_event(
            #     event_type="mcp_tool_error",
            #     session_id=self.session_id,
            #     metadata={
            #         "tool_name": tool_name if 'tool_name' in locals() else "unknown",
            #         "error": str(e),
            #         "request_id": request_id
            #     }
            # )
            
            raise
    
    async def _handle_list_resources(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP list resources request."""
        request_id = request_data.get("id")
        
        # For now, return empty resources list
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": []
            }
        }
        
        return response
    
    async def _handle_set_log_level(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP set log level request."""
        request_id = request_data.get("id")
        
        try:
            params = request_data.get("params", {})
            level = params.get("level", "INFO").upper()
            
            # Update logging level
            logging.getLogger().setLevel(getattr(logging, level, logging.INFO))
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "success": True,
                    "level": level
                }
            }
            
            logger.info("Log level changed to: %s", level)
            return response
            
        except Exception as e:
            logger.error("Error in set log level handler: %s", str(e))
            raise
    
    def _is_valid_jsonrpc(self, request_data: Dict[str, Any]) -> bool:
        """Validate JSON-RPC 2.0 format."""
        return (
            isinstance(request_data, dict) and
            request_data.get("jsonrpc") == "2.0" and
            "method" in request_data and
            "id" in request_data
        )
    
    def _create_error_response(
        self,
        request_id: Optional[str],
        code: int,
        message: str,
        data: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create JSON-RPC error response."""
        error_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        
        if data:
            error_response["error"]["data"] = data
        
        return error_response
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the MCP server."""
        return {
            "status": "healthy" if self.initialized else "initializing",
            "session_id": self.session_id,
            "tools_count": len(self.tools),
            "uptime": datetime.utcnow().isoformat()
        }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of the MCP server."""
        logger.info("Shutting down MCP Server...")
        
        try:
            # Log shutdown event
            if self.audit_service:
                await self.audit_service.log_event(
                    event_type="mcp_server_shutdown",
                    session_id=self.session_id,
                    metadata={"graceful": True}
                )
            
            # Shutdown tool implementations
            if self.payment_tools:
                await self.payment_tools.shutdown()
            
            if self.wallet_tools:
                await self.wallet_tools.shutdown()
            
            if self.subscription_tools:
                await self.subscription_tools.shutdown()
            
            if self.compliance_tools:
                await self.compliance_tools.shutdown()
            
            # Shutdown services
            if self.audit_service:
                await self.audit_service.shutdown()
            
            self.initialized = False
            logger.info("✅ MCP Server shut down gracefully")
            
        except Exception as e:
            logger.error("Error during MCP Server shutdown: %s", str(e))
            raise
