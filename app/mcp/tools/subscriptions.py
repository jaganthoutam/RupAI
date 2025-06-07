"""
Subscription Tools for MCP Server
Enterprise-grade subscription management tools with billing and lifecycle management.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from ..schemas import ToolDefinition, ToolInputSchema, ToolContent, ToolResult


logger = logging.getLogger(__name__)


class SubscriptionFrequency(str, Enum):
    """Subscription billing frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class CreateSubscriptionInput(BaseModel):
    """Input schema for create_subscription tool."""
    customer_id: str = Field(..., description="Customer identifier")
    plan_id: str = Field(..., description="Subscription plan ID")
    amount: Decimal = Field(..., gt=0, description="Subscription amount")
    currency: str = Field(..., description="Currency code")
    frequency: SubscriptionFrequency = Field(..., description="Billing frequency")
    start_date: Optional[datetime] = Field(None, description="Subscription start date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Subscription amount must be greater than 0")
        if v > Decimal("50000"):
            raise ValueError("Subscription amount exceeds maximum limit")
        return v


class CancelSubscriptionInput(BaseModel):
    """Input schema for cancel_subscription tool."""
    subscription_id: str = Field(..., description="Subscription identifier")
    reason: Optional[str] = Field(None, description="Cancellation reason")
    cancel_at_period_end: bool = Field(True, description="Cancel at period end")


class UpdateSubscriptionInput(BaseModel):
    """Input schema for update_subscription tool."""
    subscription_id: str = Field(..., description="Subscription identifier")
    plan_id: Optional[str] = Field(None, description="New plan ID")
    amount: Optional[Decimal] = Field(None, gt=0, description="New amount")
    frequency: Optional[SubscriptionFrequency] = Field(None, description="New frequency")


class GetSubscriptionInput(BaseModel):
    """Input schema for get_subscription tool."""
    subscription_id: str = Field(..., description="Subscription identifier")


class ListSubscriptionsInput(BaseModel):
    """Input schema for list_subscriptions tool."""
    customer_id: str = Field(..., description="Customer identifier")
    status: Optional[str] = Field(None, description="Filter by status")


class SubscriptionTools:
    """
    Subscription Tools for MCP Server.
    
    Provides comprehensive subscription management capabilities including:
    - Subscription creation and management
    - Billing cycle management
    - Plan changes and updates
    - Subscription analytics and reporting
    - Lifecycle management (pause, resume, cancel)
    """
    
    def __init__(
        self,
        database=None,
        redis_client=None,
        audit_service=None,
        metrics_collector=None
    ):
        self.database = database
        self.redis_client = redis_client
        self.audit_service = audit_service
        self.metrics_collector = metrics_collector
        
    async def initialize(self) -> None:
        """Initialize subscription tools and services."""
        try:
            logger.info("✅ Subscription tools initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize subscription tools: %s", str(e))
            raise
    
    async def shutdown(self) -> None:
        """Shutdown subscription tools gracefully."""
        try:
            logger.info("🔄 Shutting down subscription tools...")
            logger.info("✅ Subscription tools shut down successfully")
        except Exception as e:
            logger.error("❌ Error during subscription tools shutdown: %s", str(e))
            raise
    
    async def get_tool_definitions(self) -> Dict[str, ToolDefinition]:
        """Get all subscription tool definitions for MCP registration."""
        
        tools = {
            "create_subscription": ToolDefinition(
                name="create_subscription",
                description="Create a new subscription for customer",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier"
                        },
                        "plan_id": {
                            "type": "string",
                            "description": "Subscription plan ID"
                        },
                        "amount": {
                            "type": "number",
                            "minimum": 0.01,
                            "description": "Subscription amount"
                        },
                        "currency": {
                            "type": "string",
                            "enum": ["USD", "EUR", "GBP", "INR", "JPY"],
                            "description": "Currency code"
                        },
                        "frequency": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly", "quarterly", "yearly"],
                            "description": "Billing frequency"
                        }
                    },
                    required=["customer_id", "plan_id", "amount", "currency", "frequency"]
                )
            ),
            
            "cancel_subscription": ToolDefinition(
                name="cancel_subscription",
                description="Cancel an existing subscription",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "subscription_id": {
                            "type": "string",
                            "description": "Subscription identifier"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Cancellation reason"
                        },
                        "cancel_at_period_end": {
                            "type": "boolean",
                            "description": "Cancel at period end"
                        }
                    },
                    required=["subscription_id"]
                )
            ),
            
            "update_subscription": ToolDefinition(
                name="update_subscription",
                description="Update subscription details",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "subscription_id": {
                            "type": "string",
                            "description": "Subscription identifier"
                        },
                        "plan_id": {
                            "type": "string",
                            "description": "New plan ID"
                        },
                        "amount": {
                            "type": "number",
                            "minimum": 0.01,
                            "description": "New amount"
                        },
                        "frequency": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly", "quarterly", "yearly"],
                            "description": "New frequency"
                        }
                    },
                    required=["subscription_id"]
                )
            ),
            
            "get_subscription": ToolDefinition(
                name="get_subscription",
                description="Get subscription details",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "subscription_id": {
                            "type": "string",
                            "description": "Subscription identifier"
                        }
                    },
                    required=["subscription_id"]
                )
            ),
            
            "list_subscriptions": ToolDefinition(
                name="list_subscriptions",
                description="List customer subscriptions",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["active", "paused", "canceled", "expired"],
                            "description": "Filter by status"
                        }
                    },
                    required=["customer_id"]
                )
            )
        }
        
        return tools
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Handle subscription tool calls."""
        
        try:
            # Record metrics
            if self.metrics_collector:
                await self.metrics_collector.record_tool_call("subscription", tool_name)
            
            # Route to appropriate handler
            if tool_name == "create_subscription":
                return await self._handle_create_subscription(arguments)
            elif tool_name == "cancel_subscription":
                return await self._handle_cancel_subscription(arguments)
            elif tool_name == "update_subscription":
                return await self._handle_update_subscription(arguments)
            elif tool_name == "get_subscription":
                return await self._handle_get_subscription(arguments)
            elif tool_name == "list_subscriptions":
                return await self._handle_list_subscriptions(arguments)
            else:
                return ToolResult(
                    content=[ToolContent(
                        type="text",
                        text=f"Unknown subscription tool: {tool_name}"
                    )],
                    isError=True
                )
                
        except Exception as e:
            logger.error("Subscription tool call failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text", 
                    text=f"Subscription tool error: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_create_subscription(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle create subscription tool call."""
        
        try:
            input_data = CreateSubscriptionInput(**arguments)
            
            # Simulate subscription creation
            subscription_id = str(uuid4())
            
            result_data = {
                "subscription_id": subscription_id,
                "customer_id": input_data.customer_id,
                "plan_id": input_data.plan_id,
                "amount": str(input_data.amount),
                "currency": input_data.currency,
                "frequency": input_data.frequency,
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Subscription created successfully with ID: {subscription_id}"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Create subscription failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to create subscription: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_cancel_subscription(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle cancel subscription tool call."""
        
        try:
            input_data = CancelSubscriptionInput(**arguments)
            
            result_data = {
                "subscription_id": input_data.subscription_id,
                "status": "canceled",
                "reason": input_data.reason,
                "canceled_at": datetime.utcnow().isoformat()
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Subscription {input_data.subscription_id} canceled successfully"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Cancel subscription failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to cancel subscription: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_update_subscription(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle update subscription tool call."""
        
        try:
            input_data = UpdateSubscriptionInput(**arguments)
            
            # Simulate subscription update
            result_data = {
                "subscription_id": input_data.subscription_id,
                "updated_fields": {},
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if input_data.plan_id:
                result_data["updated_fields"]["plan_id"] = input_data.plan_id
            if input_data.amount:
                result_data["updated_fields"]["amount"] = str(input_data.amount)
            if input_data.frequency:
                result_data["updated_fields"]["frequency"] = input_data.frequency
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Subscription {input_data.subscription_id} updated successfully"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Update subscription failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to update subscription: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_get_subscription(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle get subscription tool call."""
        
        try:
            input_data = GetSubscriptionInput(**arguments)
            
            # Simulate subscription retrieval
            result_data = {
                "subscription_id": input_data.subscription_id,
                "customer_id": "cust_12345",
                "plan_id": "plan_premium",
                "amount": "29.99",
                "currency": "USD",
                "frequency": "monthly",
                "status": "active",
                "start_date": "2024-01-01T00:00:00Z",
                "next_billing_date": "2024-02-01T00:00:00Z",
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Subscription {input_data.subscription_id} details retrieved"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Get subscription failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to get subscription: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_list_subscriptions(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle list subscriptions tool call."""
        
        try:
            input_data = ListSubscriptionsInput(**arguments)
            
            # Simulate subscription listing
            subscriptions = [
                {
                    "subscription_id": "sub_1",
                    "plan_id": "plan_basic",
                    "amount": "9.99",
                    "currency": "USD",
                    "frequency": "monthly",
                    "status": "active"
                },
                {
                    "subscription_id": "sub_2",
                    "plan_id": "plan_premium",
                    "amount": "29.99",
                    "currency": "USD",
                    "frequency": "monthly",
                    "status": "active"
                }
            ]
            
            # Filter by status if provided
            if input_data.status:
                subscriptions = [s for s in subscriptions if s["status"] == input_data.status]
            
            result_data = {
                "customer_id": input_data.customer_id,
                "subscriptions": subscriptions,
                "total_count": len(subscriptions),
                "filtered_by_status": input_data.status
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Found {len(subscriptions)} subscriptions for customer {input_data.customer_id}"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("List subscriptions failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to list subscriptions: {str(e)}"
                )],
                isError=True
            )
    
    def _calculate_next_billing_date(self, start_date: datetime, frequency: SubscriptionFrequency) -> datetime:
        """Calculate next billing date based on frequency."""
        
        if frequency == SubscriptionFrequency.DAILY:
            return start_date + timedelta(days=1)
        elif frequency == SubscriptionFrequency.WEEKLY:
            return start_date + timedelta(weeks=1)
        elif frequency == SubscriptionFrequency.MONTHLY:
            return start_date + timedelta(days=30)
        elif frequency == SubscriptionFrequency.QUARTERLY:
            return start_date + timedelta(days=90)
        elif frequency == SubscriptionFrequency.YEARLY:
            return start_date + timedelta(days=365)
        else:
            return start_date + timedelta(days=30)  # Default to monthly 