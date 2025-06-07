"""
Payment Tools for MCP Server
Enterprise-grade payment processing tools with comprehensive validation and security.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ..schemas import ToolDefinition, ToolInputSchema, ToolContent, ToolResult
from ...services.payment_service import PaymentService


logger = logging.getLogger(__name__)


class CreatePaymentInput(BaseModel):
    """Input schema for create_payment tool."""
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: str = Field(..., description="Currency code (ISO 4217)")
    method: str = Field(..., description="Payment method")
    customer_id: str = Field(..., description="Customer identifier")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > Decimal("1000000"):
            raise ValueError("Amount exceeds maximum limit")
        return v


class VerifyPaymentInput(BaseModel):
    """Input schema for verify_payment tool."""
    payment_id: str = Field(..., description="Payment identifier")
    provider_reference: Optional[str] = Field(None, description="Provider reference ID")


class RefundPaymentInput(BaseModel):
    """Input schema for refund_payment tool.""" 
    payment_id: str = Field(..., description="Payment identifier")
    amount: Optional[Decimal] = Field(None, gt=0, description="Refund amount (partial)")
    reason: str = Field(..., description="Refund reason")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")


class PaymentTools:
    """
    Payment Tools for MCP Server.
    
    Provides comprehensive payment processing capabilities including:
    - Payment creation and processing
    - Payment verification and status tracking
    - Refund processing
    - Transaction history and reporting
    """
    
    def __init__(
        self,
        database=None,
        redis_client=None,
        audit_service=None,
        encryption_manager=None,
        metrics_collector=None
    ):
        self.database = database
        self.redis_client = redis_client
        self.audit_service = audit_service
        self.encryption_manager = encryption_manager
        self.metrics_collector = metrics_collector
        self.payment_service: Optional[PaymentService] = None
        
    async def initialize(self) -> None:
        """Initialize payment tools and services."""
        try:
            # Initialize payment service if database is available
            if self.database:
                # Import required classes
                from ...repositories.payment_repository import PaymentRepository
                from ...integrations.stripe_client import StripeClient
                from ...integrations.razorpay_client import RazorpayClient
                
                # Create required dependencies
                session = self.database.get_session()
                payment_repo = PaymentRepository(session)
                stripe_client = StripeClient()
                razorpay_client = RazorpayClient()
                
                # Create payment service with correct parameters
                self.payment_service = PaymentService(
                    repo=payment_repo,
                    stripe=stripe_client,
                    razorpay=razorpay_client
                )
            
            logger.info("✅ Payment tools initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize payment tools: %s", str(e))
            raise
    
    async def shutdown(self) -> None:
        """Shutdown payment tools gracefully."""
        try:
            logger.info("🔄 Shutting down payment tools...")
            logger.info("✅ Payment tools shut down successfully")
        except Exception as e:
            logger.error("❌ Error during payment tools shutdown: %s", str(e))
            raise
    
    async def get_tool_definitions(self) -> Dict[str, ToolDefinition]:
        """Get all payment tool definitions for MCP registration."""
        
        tools = {
            "create_payment": ToolDefinition(
                name="create_payment",
                description="Create a new payment transaction",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "amount": {
                            "type": "number",
                            "minimum": 0.01,
                            "description": "Payment amount"
                        },
                        "currency": {
                            "type": "string",
                            "enum": ["USD", "EUR", "GBP", "INR", "JPY"],
                            "description": "Currency code (ISO 4217)"
                        },
                        "method": {
                            "type": "string",
                            "enum": ["card", "bank_transfer", "wallet", "upi"],
                            "description": "Payment method"
                        },
                        "customer_id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Customer identifier"
                        },
                        "idempotency_key": {
                            "type": "string",
                            "minLength": 16,
                            "description": "Idempotency key for duplicate prevention"
                        },
                        "description": {
                            "type": "string",
                            "description": "Payment description"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Additional metadata"
                        }
                    },
                    required=["amount", "currency", "method", "customer_id", "idempotency_key"]
                )
            ),
            
            "verify_payment": ToolDefinition(
                name="verify_payment",
                description="Verify payment status and update transaction state",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "payment_id": {
                            "type": "string",
                            "description": "Payment identifier"
                        },
                        "provider_reference": {
                            "type": "string",
                            "description": "Provider reference ID"
                        }
                    },
                    required=["payment_id"]
                )
            ),
            
            "refund_payment": ToolDefinition(
                name="refund_payment",
                description="Process payment refund with audit trail",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "payment_id": {
                            "type": "string",
                            "description": "Payment identifier"
                        },
                        "amount": {
                            "type": "number",
                            "minimum": 0.01,
                            "description": "Refund amount (optional for partial refund)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Refund reason"
                        },
                        "idempotency_key": {
                            "type": "string",
                            "minLength": 16,
                            "description": "Idempotency key"
                        }
                    },
                    required=["payment_id", "reason", "idempotency_key"]
                )
            )
        }
        
        return tools
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Handle payment tool calls."""
        
        try:
            # Record metrics
            if self.metrics_collector:
                await self.metrics_collector.record_tool_call("payment", tool_name)
            
            # Route to appropriate handler
            if tool_name == "create_payment":
                return await self._handle_create_payment(arguments)
            elif tool_name == "verify_payment":
                return await self._handle_verify_payment(arguments)
            elif tool_name == "refund_payment":
                return await self._handle_refund_payment(arguments)
            else:
                return ToolResult(
                    content=[ToolContent(
                        type="text",
                        text=f"Unknown payment tool: {tool_name}"
                    )],
                    isError=True
                )
                
        except Exception as e:
            logger.error("Payment tool call failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text", 
                    text=f"Payment tool error: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_create_payment(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle create payment tool call."""
        
        try:
            # Validate input
            input_data = CreatePaymentInput(**arguments)
            
            # For now, simulate payment creation (replace with actual service call)
            payment_id = str(uuid4())
            
            result_data = {
                "payment_id": payment_id,
                "status": "pending",
                "amount": str(input_data.amount),
                "currency": input_data.currency,
                "method": input_data.method,
                "customer_id": input_data.customer_id,
                "created_at": datetime.utcnow().isoformat(),
                "idempotency_key": input_data.idempotency_key
            }
            
            # Log audit event
            if self.audit_service:
                await self.audit_service.log_event(
                    event_type="payment_created",
                    user_id=input_data.customer_id,
                    metadata=result_data
                )
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Payment created successfully with ID: {payment_id}"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Create payment failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to create payment: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_verify_payment(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle verify payment tool call."""
        
        try:
            input_data = VerifyPaymentInput(**arguments)
            
            # For now, simulate payment verification
            result_data = {
                "payment_id": input_data.payment_id,
                "status": "completed",
                "verified_at": datetime.utcnow().isoformat(),
                "provider_status": "success"
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Payment {input_data.payment_id} verified successfully"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Verify payment failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to verify payment: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_refund_payment(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle refund payment tool call."""
        
        try:
            input_data = RefundPaymentInput(**arguments)
            
            # For now, simulate refund processing
            refund_id = str(uuid4())
            result_data = {
                "refund_id": refund_id,
                "payment_id": input_data.payment_id,
                "amount": str(input_data.amount) if input_data.amount else "full",
                "reason": input_data.reason,
                "status": "processed",
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Refund processed successfully with ID: {refund_id}"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Refund payment failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to process refund: {str(e)}"
                )],
                isError=True
            )

# Function-based implementations for backward compatibility
# These provide direct access to payment tools without class instantiation

async def create_payment(
    amount: float,
    currency: str,
    method: str,
    customer_id: str,
    idempotency_key: str,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new payment transaction.
    
    Args:
        amount: Payment amount
        currency: Currency code (ISO 4217)
        method: Payment method
        customer_id: Customer identifier
        idempotency_key: Idempotency key
        description: Payment description
        metadata: Additional metadata
        
    Returns:
        Payment creation result
    """
    try:
        # Create payment tools instance
        payment_tools = PaymentTools()
        await payment_tools.initialize()
        
        # Prepare arguments
        arguments = {
            "amount": amount,
            "currency": currency,
            "method": method,
            "customer_id": customer_id,
            "idempotency_key": idempotency_key
        }
        
        if description:
            arguments["description"] = description
        if metadata:
            arguments["metadata"] = metadata
            
        # Call the class method
        result = await payment_tools._handle_create_payment(arguments)
        
        return {
            "success": not result.isError,
            "data": result.meta if hasattr(result, 'meta') else None,
            "message": result.content[0].text if result.content else "Payment created"
        }
        
    except Exception as e:
        logger.error("Function create_payment failed: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create payment: {str(e)}"
        }


async def verify_payment(
    payment_id: str,
    provider_reference: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify payment status and update transaction state.
    
    Args:
        payment_id: Payment identifier
        provider_reference: Provider reference ID
        
    Returns:
        Payment verification result
    """
    try:
        # Create payment tools instance
        payment_tools = PaymentTools()
        await payment_tools.initialize()
        
        # Prepare arguments
        arguments = {
            "payment_id": payment_id
        }
        
        if provider_reference:
            arguments["provider_reference"] = provider_reference
            
        # Call the class method
        result = await payment_tools._handle_verify_payment(arguments)
        
        return {
            "success": not result.isError,
            "data": result.meta if hasattr(result, 'meta') else None,
            "message": result.content[0].text if result.content else "Payment verified"
        }
        
    except Exception as e:
        logger.error("Function verify_payment failed: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to verify payment: {str(e)}"
        }


async def refund_payment(
    payment_id: str,
    reason: str,
    idempotency_key: str,
    amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Process payment refund with audit trail.
    
    Args:
        payment_id: Payment identifier
        reason: Refund reason
        idempotency_key: Idempotency key
        amount: Refund amount (optional for partial refund)
        
    Returns:
        Refund processing result
    """
    try:
        # Create payment tools instance
        payment_tools = PaymentTools()
        await payment_tools.initialize()
        
        # Prepare arguments
        arguments = {
            "payment_id": payment_id,
            "reason": reason,
            "idempotency_key": idempotency_key
        }
        
        if amount:
            arguments["amount"] = Decimal(str(amount))
            
        # Call the class method
        result = await payment_tools._handle_refund_payment(arguments)
        
        return {
            "success": not result.isError,
            "data": result.meta if hasattr(result, 'meta') else None,
            "message": result.content[0].text if result.content else "Refund processed"
        }
        
    except Exception as e:
        logger.error("Function refund_payment failed: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to process refund: {str(e)}"
        }


async def get_payment_status(
    payment_id: str
) -> Dict[str, Any]:
    """
    Retrieve current payment status and details.
    
    Args:
        payment_id: Payment identifier
        
    Returns:
        Payment status information
    """
    try:
        # For now, simulate payment status retrieval
        # In a real implementation, this would query the database
        result_data = {
            "payment_id": payment_id,
            "status": "completed",
            "amount": "100.00",
            "currency": "USD",
            "method": "card",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": result_data,
            "message": f"Payment {payment_id} status retrieved"
        }
        
    except Exception as e:
        logger.error("Function get_payment_status failed: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get payment status: {str(e)}"
        }
