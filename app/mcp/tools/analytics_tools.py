"""
Analytics Tools for MCP Server
Provides AI-powered analytics and optimization tools
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationError

from app.mcp.tools.analytics import (
    optimize_payment_routing,
    create_payment_optimized,
    smart_payment_routing,
    get_payment_metrics,
    analyze_user_behavior,
    generate_revenue_analytics,
    detect_fraud_patterns,
    generate_performance_report,
    get_dashboard_metrics,
    generate_custom_report
)
from app.mcp.schemas import ToolDefinition, ToolResult, ToolContent
from app.utils.monitoring import MetricsCollector
from app.services.audit_service import AuditService
from app.db.database import Database
from app.db.redis import RedisClient

logger = logging.getLogger(__name__)


class AnalyticsTools:
    """
    Analytics and AI optimization tools for MCP server.
    
    Provides AI-powered payment optimization, fraud detection,
    analytics generation, and business intelligence features.
    """
    
    def __init__(
        self,
        database: Database,
        redis_client: RedisClient,
        audit_service: AuditService,
        metrics_collector: MetricsCollector
    ):
        self.database = database
        self.redis_client = redis_client
        self.audit_service = audit_service
        self.metrics_collector = metrics_collector
        self.initialized = False
        
        logger.info("AnalyticsTools instance created")
    
    async def initialize(self) -> None:
        """Initialize analytics tools."""
        try:
            logger.info("Initializing Analytics Tools...")
            self.initialized = True
            logger.info("✅ Analytics Tools initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Analytics Tools: %s", str(e))
            raise
    
    async def get_tool_definitions(self) -> Dict[str, ToolDefinition]:
        """Get all analytics tool definitions for MCP registration."""
        
        tools = {
            # AI Optimization Tools
            "optimize_payment_routing": ToolDefinition(
                name="optimize_payment_routing",
                description="AI-powered payment routing optimization for cost, speed, or success rate",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "minimum": 0.01,
                            "description": "Payment amount"
                        },
                        "currency": {
                            "type": "string", 
                            "enum": ["USD", "EUR", "GBP", "INR", "JPY"],
                            "default": "USD",
                            "description": "Currency code"
                        },
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier (optional)"
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "Payment method (optional)"
                        },
                        "optimize_for": {
                            "type": "string",
                            "enum": ["cost", "speed", "success_rate"],
                            "default": "cost",
                            "description": "Optimization target"
                        }
                    },
                    "required": ["amount"],
                    "additionalProperties": False
                }
            ),
            
            "create_payment_optimized": ToolDefinition(
                name="create_payment_optimized",
                description="Create AI-optimized payment with intelligent routing and fraud detection",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "minimum": 0.01,
                            "description": "Payment amount"
                        },
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier"
                        },
                        "currency": {
                            "type": "string",
                            "enum": ["USD", "EUR", "GBP", "INR", "JPY"],
                            "default": "USD",
                            "description": "Currency code"
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "Payment method (optional)"
                        },
                        "optimize_for": {
                            "type": "string",
                            "enum": ["cost", "speed", "success_rate"],
                            "default": "cost",
                            "description": "Optimization target"
                        },
                        "ai_optimization": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable AI optimization"
                        },
                        "fraud_check": {
                            "type": "boolean", 
                            "default": True,
                            "description": "Enable fraud detection"
                        }
                    },
                    "required": ["amount", "customer_id"],
                    "additionalProperties": False
                }
            ),
            
            "smart_payment_routing": ToolDefinition(
                name="smart_payment_routing",
                description="Intelligent payment routing based on customer profile and transaction context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "payment_context": {
                            "type": "object",
                            "description": "Payment transaction context",
                            "properties": {
                                "amount": {"type": "number", "minimum": 0.01},
                                "currency": {"type": "string", "default": "USD"},
                                "payment_method": {"type": "string"},
                                "merchant_category": {"type": "string"}
                            },
                            "required": ["amount"]
                        },
                        "customer_profile": {
                            "type": "object",
                            "description": "Customer profile data (optional)",
                            "properties": {
                                "location": {"type": "string"},
                                "preferred_method": {"type": "string"},
                                "loyalty_tier": {"type": "string"},
                                "success_rate_card": {"type": "number"},
                                "success_rate_upi": {"type": "number"},
                                "success_rate_wallet": {"type": "number"}
                            }
                        }
                    },
                    "required": ["payment_context"],
                    "additionalProperties": False
                }
            ),
            
            # Analytics Tools
            "get_payment_metrics": ToolDefinition(
                name="get_payment_metrics",
                description="Generate comprehensive payment metrics and KPIs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Start date for analysis"
                        },
                        "end_date": {
                            "type": "string", 
                            "format": "date-time",
                            "description": "End date for analysis"
                        },
                        "granularity": {
                            "type": "string",
                            "enum": ["hourly", "daily", "weekly", "monthly"],
                            "default": "daily",
                            "description": "Time granularity"
                        },
                        "currency": {
                            "type": "string",
                            "description": "Filter by currency (optional)"
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "Filter by payment method (optional)"
                        },
                        "provider": {
                            "type": "string",
                            "description": "Filter by provider (optional)"
                        }
                    },
                    "required": ["start_date", "end_date"],
                    "additionalProperties": False
                }
            ),
            
            "analyze_user_behavior": ToolDefinition(
                name="analyze_user_behavior",
                description="Analyze user behavior patterns and engagement",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Specific user ID to analyze (optional)"
                        },
                        "segment": {
                            "type": "string",
                            "description": "User segment to analyze (optional)"
                        },
                        "days": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 365,
                            "default": 30,
                            "description": "Number of days to analyze"
                        },
                        "include_churn_analysis": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include churn risk analysis"
                        }
                    },
                    "required": [],
                    "additionalProperties": False
                }
            ),
            
            "detect_fraud_patterns": ToolDefinition(
                name="detect_fraud_patterns", 
                description="Detect fraud patterns and analyze transaction risk",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "transaction_id": {
                            "type": "string",
                            "description": "Specific transaction to analyze (optional)"
                        },
                        "user_id": {
                            "type": "string",
                            "description": "Specific user to analyze (optional)"
                        },
                        "hours_back": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 168,
                            "default": 24,
                            "description": "Hours to look back for analysis"
                        },
                        "risk_threshold": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                            "default": 70.0,
                            "description": "Risk score threshold"
                        }
                    },
                    "required": [],
                    "additionalProperties": False
                }
            ),
            
            "generate_revenue_analytics": ToolDefinition(
                name="generate_revenue_analytics",
                description="Generate revenue analytics and forecasting",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Start date for analysis"
                        },
                        "end_date": {
                            "type": "string",
                            "format": "date-time", 
                            "description": "End date for analysis"
                        },
                        "currency": {
                            "type": "string",
                            "default": "USD",
                            "description": "Currency for analysis"
                        },
                        "breakdown_by": {
                            "type": "string",
                            "enum": ["hourly", "daily", "weekly", "monthly"],
                            "default": "daily",
                            "description": "Breakdown granularity"
                        },
                        "include_forecast": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include revenue forecasting"
                        }
                    },
                    "required": ["start_date", "end_date"],
                    "additionalProperties": False
                }
            ),
            
            "get_dashboard_metrics": ToolDefinition(
                name="get_dashboard_metrics",
                description="Get real-time dashboard metrics and KPIs",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "time_range": {
                            "type": "string",
                            "enum": ["1h", "24h", "7d", "30d", "90d"],
                            "default": "24h",
                            "description": "Time range for metrics"
                        },
                        "refresh_cache": {
                            "type": "boolean",
                            "default": False,
                            "description": "Force refresh cache"
                        }
                    },
                    "required": [],
                    "additionalProperties": False
                }
            ),
            
            "generate_custom_report": ToolDefinition(
                name="generate_custom_report",
                description="Generate custom analytics reports",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "enum": ["payment_summary", "fraud_analysis", "revenue_breakdown", "user_engagement"],
                            "description": "Type of report to generate"
                        },
                        "start_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Start date for report"
                        },
                        "end_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "End date for report"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional filters for report",
                            "additionalProperties": True
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "csv", "pdf"],
                            "default": "json",
                            "description": "Report format"
                        }
                    },
                    "required": ["report_type", "start_date", "end_date"],
                    "additionalProperties": False
                }
            ),
            
            "generate_performance_report": ToolDefinition(
                name="generate_performance_report",
                description="Generate system performance analytics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "hours_back": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 168,
                            "default": 24,
                            "description": "Hours to analyze"
                        },
                        "include_predictions": {
                            "type": "boolean",
                            "default": True,
                            "description": "Include performance predictions"
                        },
                        "service_name": {
                            "type": "string", 
                            "description": "Specific service to analyze (optional)"
                        }
                    },
                    "required": [],
                    "additionalProperties": False
                }
            )
        }
        
        return tools
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Handle analytics tool calls."""
        
        try:
            # Log the tool call
            await self.audit_service.log_event(
                event_type="analytics_tool_call",
                metadata={
                    "tool_name": tool_name,
                    "arguments": arguments
                }
            )
            
            # Route to appropriate handler and get result
            result_data = None
            
            if tool_name == "optimize_payment_routing":
                result_data = await optimize_payment_routing(**arguments)
            elif tool_name == "create_payment_optimized":
                result_data = await create_payment_optimized(**arguments)
            elif tool_name == "smart_payment_routing":
                result_data = await smart_payment_routing(**arguments)
            elif tool_name == "get_payment_metrics":
                # Convert string dates to datetime
                if "start_date" in arguments:
                    arguments["start_date"] = datetime.fromisoformat(arguments["start_date"].replace('Z', '+00:00'))
                if "end_date" in arguments:
                    arguments["end_date"] = datetime.fromisoformat(arguments["end_date"].replace('Z', '+00:00'))
                result_data = await get_payment_metrics(**arguments)
            elif tool_name == "analyze_user_behavior":
                result_data = await analyze_user_behavior(**arguments)
            elif tool_name == "generate_revenue_analytics":
                # Convert string dates to datetime
                if "start_date" in arguments:
                    arguments["start_date"] = datetime.fromisoformat(arguments["start_date"].replace('Z', '+00:00'))
                if "end_date" in arguments:
                    arguments["end_date"] = datetime.fromisoformat(arguments["end_date"].replace('Z', '+00:00'))
                result_data = await generate_revenue_analytics(**arguments)
            elif tool_name == "detect_fraud_patterns":
                result_data = await detect_fraud_patterns(**arguments)
            elif tool_name == "generate_performance_report":
                result_data = await generate_performance_report(**arguments)
            elif tool_name == "get_dashboard_metrics":
                result_data = await get_dashboard_metrics(**arguments)
            elif tool_name == "generate_custom_report":
                # Convert string dates to datetime
                if "start_date" in arguments:
                    arguments["start_date"] = datetime.fromisoformat(arguments["start_date"].replace('Z', '+00:00'))
                if "end_date" in arguments:
                    arguments["end_date"] = datetime.fromisoformat(arguments["end_date"].replace('Z', '+00:00'))
                result_data = await generate_custom_report(**arguments)
            else:
                return ToolResult(
                    content=[ToolContent(
                        type="text",
                        text=f"Unknown analytics tool: {tool_name}"
                    )],
                    isError=True
                )
            
            # Format the result as MCP ToolResult
            if result_data:
                success_message = result_data.get("message", f"{tool_name} completed successfully")
                return ToolResult(
                    content=[ToolContent(
                        type="text",
                        text=success_message
                    )],
                    isError=False,
                    meta=result_data
                )
            else:
                return ToolResult(
                    content=[ToolContent(
                        type="text",
                        text=f"No data returned from {tool_name}"
                    )],
                    isError=True
                )
                
        except Exception as e:
            logger.error("Error in analytics tool call %s: %s", tool_name, str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Analytics tool error: {str(e)}"
                )],
                isError=True
            ) 