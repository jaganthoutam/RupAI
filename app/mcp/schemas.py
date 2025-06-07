"""
MCP Protocol Schemas - Model Context Protocol v2024.1
JSON Schema definitions for MCP requests, responses, and tool specifications.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Base MCP Protocol Schemas
# ============================================================================

class MCPRequest(BaseModel):
    """Base MCP JSON-RPC 2.0 request."""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    id: Union[str, int, None] = Field(..., description="Request identifier")
    method: str = Field(..., description="Method name")
    params: Optional[Dict[str, Any]] = Field(None, description="Method parameters")


class MCPResponse(BaseModel):
    """Base MCP JSON-RPC 2.0 response."""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    id: Union[str, int, None] = Field(..., description="Request identifier")
    result: Optional[Dict[str, Any]] = Field(None, description="Success result")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details")


class MCPError(BaseModel):
    """MCP JSON-RPC 2.0 error object."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Any] = Field(None, description="Additional error data")


# ============================================================================
# MCP Initialization
# ============================================================================

class ClientInfo(BaseModel):
    """MCP client information."""
    name: str = Field(..., description="Client name")
    version: str = Field(..., description="Client version")


class ServerInfo(BaseModel):
    """MCP server information."""
    name: str = Field(..., description="Server name")
    version: str = Field(..., description="Server version")


class MCPCapabilities(BaseModel):
    """MCP server capabilities."""
    tools: bool = Field(True, description="Supports tools")
    resources: bool = Field(False, description="Supports resources")
    prompts: bool = Field(False, description="Supports prompts")
    logging: bool = Field(True, description="Supports logging")
    sampling: bool = Field(False, description="Supports sampling")


class InitializeRequest(BaseModel):
    """MCP initialize request parameters."""
    protocolVersion: str = Field(..., description="MCP protocol version")
    clientInfo: ClientInfo = Field(..., description="Client information")
    capabilities: Optional[MCPCapabilities] = Field(None, description="Client capabilities")


class InitializeResponse(BaseModel):
    """MCP initialize response result."""
    protocolVersion: str = Field(..., description="MCP protocol version")
    serverInfo: ServerInfo = Field(..., description="Server information")
    capabilities: MCPCapabilities = Field(..., description="Server capabilities")
    instructions: Optional[str] = Field(None, description="Usage instructions")


# ============================================================================
# MCP Tools
# ============================================================================

class ToolInputSchema(BaseModel):
    """JSON Schema for tool input validation."""
    type: str = Field("object", description="Schema type")
    properties: Dict[str, Any] = Field(..., description="Property definitions")
    required: List[str] = Field(default_factory=list, description="Required properties")
    additionalProperties: bool = Field(False, description="Allow additional properties")


class ToolDefinition(BaseModel):
    """MCP tool definition."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    inputSchema: ToolInputSchema = Field(..., description="Input validation schema")


class ListToolsRequest(BaseModel):
    """MCP list tools request (no parameters)."""
    pass


class ListToolsResponse(BaseModel):
    """MCP list tools response."""
    tools: List[ToolDefinition] = Field(..., description="Available tools")


class ToolCall(BaseModel):
    """MCP tool call parameters."""
    name: str = Field(..., description="Tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class CallToolRequest(BaseModel):
    """MCP call tool request parameters."""
    name: str = Field(..., description="Tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class ToolContent(BaseModel):
    """Tool response content."""
    type: str = Field("text", description="Content type")
    text: str = Field(..., description="Text content")


class ToolResult(BaseModel):
    """MCP tool call result."""
    content: List[ToolContent] = Field(..., description="Result content")
    isError: bool = Field(False, description="Whether result is an error")
    meta: Optional[Dict[str, Any]] = Field(None, description="Metadata")


class CallToolResponse(BaseModel):
    """MCP call tool response."""
    content: List[ToolContent] = Field(..., description="Tool result content")
    isError: bool = Field(False, description="Whether result is an error")
    meta: Optional[Dict[str, Any]] = Field(None, description="Result metadata")


# ============================================================================
# Payment-Specific Schemas
# ============================================================================

class CurrencyCode(str, Enum):
    """Supported currency codes (ISO 4217)."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"


class PaymentMethod(str, Enum):
    """Supported payment methods."""
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    UPI = "upi"
    CRYPTO = "crypto"


class PaymentStatus(str, Enum):
    """Payment status values."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class TransactionType(str, Enum):
    """Transaction type values."""
    PAYMENT = "payment"
    REFUND = "refund"
    TRANSFER = "transfer"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"


# ============================================================================
# Payment Tool Schemas
# ============================================================================

class CreatePaymentInput(BaseModel):
    """Input schema for create_payment tool."""
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: CurrencyCode = Field(..., description="Currency code")
    method: PaymentMethod = Field(..., description="Payment method")
    customer_id: UUID = Field(..., description="Customer identifier")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        """Validate payment amount is positive and reasonable."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > Decimal("1000000"):  # 1 million limit
            raise ValueError("Amount exceeds maximum limit")
        return v


class VerifyPaymentInput(BaseModel):
    """Input schema for verify_payment tool."""
    payment_id: UUID = Field(..., description="Payment identifier")
    provider_reference: Optional[str] = Field(None, description="Provider reference ID")


class RefundPaymentInput(BaseModel):
    """Input schema for refund_payment tool."""
    payment_id: UUID = Field(..., description="Payment identifier")
    amount: Optional[Decimal] = Field(None, gt=0, description="Refund amount (partial)")
    reason: str = Field(..., description="Refund reason")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")


class GetWalletBalanceInput(BaseModel):
    """Input schema for get_wallet_balance tool."""
    customer_id: UUID = Field(..., description="Customer identifier")
    currency: Optional[CurrencyCode] = Field(None, description="Specific currency")


class TransferFundsInput(BaseModel):
    """Input schema for transfer_funds tool."""
    from_customer_id: UUID = Field(..., description="Source customer ID")
    to_customer_id: UUID = Field(..., description="Target customer ID")
    amount: Decimal = Field(..., gt=0, description="Transfer amount")
    currency: CurrencyCode = Field(..., description="Currency code")
    description: Optional[str] = Field(None, description="Transfer description")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")


# ============================================================================
# Wallet Tool Schemas
# ============================================================================

class CreateWalletInput(BaseModel):
    """Input schema for create_wallet tool."""
    customer_id: UUID = Field(..., description="Customer identifier")
    currency: CurrencyCode = Field(..., description="Wallet currency")
    initial_balance: Optional[Decimal] = Field(Decimal("0"), ge=0, description="Initial balance")


class AddFundsInput(BaseModel):
    """Input schema for add_funds tool."""
    customer_id: UUID = Field(..., description="Customer identifier")
    amount: Decimal = Field(..., gt=0, description="Amount to add")
    currency: CurrencyCode = Field(..., description="Currency code")
    source: str = Field(..., description="Funding source")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")


class WithdrawFundsInput(BaseModel):
    """Input schema for withdraw_funds tool."""
    customer_id: UUID = Field(..., description="Customer identifier")
    amount: Decimal = Field(..., gt=0, description="Amount to withdraw")
    currency: CurrencyCode = Field(..., description="Currency code")
    destination: str = Field(..., description="Withdrawal destination")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")


# ============================================================================
# Subscription Tool Schemas
# ============================================================================

class SubscriptionFrequency(str, Enum):
    """Subscription billing frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class CreateSubscriptionInput(BaseModel):
    """Input schema for create_subscription tool."""
    customer_id: UUID = Field(..., description="Customer identifier")
    plan_id: str = Field(..., description="Subscription plan ID")
    amount: Decimal = Field(..., gt=0, description="Subscription amount")
    currency: CurrencyCode = Field(..., description="Currency code")
    frequency: SubscriptionFrequency = Field(..., description="Billing frequency")
    start_date: Optional[datetime] = Field(None, description="Subscription start date")


class CancelSubscriptionInput(BaseModel):
    """Input schema for cancel_subscription tool."""
    subscription_id: UUID = Field(..., description="Subscription identifier")
    reason: Optional[str] = Field(None, description="Cancellation reason")
    cancel_at_period_end: bool = Field(True, description="Cancel at period end")


# ============================================================================
# Compliance Tool Schemas
# ============================================================================

class KYCLevel(str, Enum):
    """KYC verification levels."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ENHANCED = "enhanced"


class InitiateKYCInput(BaseModel):
    """Input schema for initiate_kyc tool."""
    customer_id: UUID = Field(..., description="Customer identifier")
    level: KYCLevel = Field(..., description="KYC verification level")
    documents: List[str] = Field(..., description="Required document types")


class GenerateComplianceReportInput(BaseModel):
    """Input schema for generate_compliance_report tool."""
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    report_type: str = Field(..., description="Report type")
    customer_id: Optional[UUID] = Field(None, description="Specific customer")


# ============================================================================
# Tool Registry Schema Definitions
# ============================================================================

def get_payment_tool_schemas() -> Dict[str, ToolDefinition]:
    """Get payment tool schema definitions."""
    return {
        "create_payment": ToolDefinition(
            name="create_payment",
            description="Initialize payment transaction with provider",
            inputSchema=ToolInputSchema(
                type="object",
                properties={
                    "amount": {"type": "number", "minimum": 0.01, "description": "Payment amount"},
                    "currency": {"type": "string", "enum": [c.value for c in CurrencyCode], "description": "Currency code"},
                    "method": {"type": "string", "enum": [m.value for m in PaymentMethod], "description": "Payment method"},
                    "customer_id": {"type": "string", "format": "uuid", "description": "Customer identifier"},
                    "idempotency_key": {"type": "string", "minLength": 16, "description": "Idempotency key"},
                    "description": {"type": "string", "description": "Payment description"},
                    "metadata": {"type": "object", "description": "Additional metadata"}
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
                    "payment_id": {"type": "string", "format": "uuid", "description": "Payment identifier"},
                    "provider_reference": {"type": "string", "description": "Provider reference ID"}
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
                    "payment_id": {"type": "string", "format": "uuid", "description": "Payment identifier"},
                    "amount": {"type": "number", "minimum": 0.01, "description": "Refund amount"},
                    "reason": {"type": "string", "description": "Refund reason"},
                    "idempotency_key": {"type": "string", "minLength": 16, "description": "Idempotency key"}
                },
                required=["payment_id", "reason", "idempotency_key"]
            )
        )
    }


def get_wallet_tool_schemas() -> Dict[str, ToolDefinition]:
    """Get wallet tool schema definitions."""
    return {
        "get_wallet_balance": ToolDefinition(
            name="get_wallet_balance",
            description="Retrieve current wallet balance for user",
            inputSchema=ToolInputSchema(
                type="object",
                properties={
                    "customer_id": {"type": "string", "format": "uuid", "description": "Customer identifier"},
                    "currency": {"type": "string", "enum": [c.value for c in CurrencyCode], "description": "Specific currency"}
                },
                required=["customer_id"]
            )
        ),
        "transfer_funds": ToolDefinition(
            name="transfer_funds",
            description="Execute P2P or merchant transfer",
            inputSchema=ToolInputSchema(
                type="object",
                properties={
                    "from_customer_id": {"type": "string", "format": "uuid", "description": "Source customer ID"},
                    "to_customer_id": {"type": "string", "format": "uuid", "description": "Target customer ID"},
                    "amount": {"type": "number", "minimum": 0.01, "description": "Transfer amount"},
                    "currency": {"type": "string", "enum": [c.value for c in CurrencyCode], "description": "Currency code"},
                    "description": {"type": "string", "description": "Transfer description"},
                    "idempotency_key": {"type": "string", "minLength": 16, "description": "Idempotency key"}
                },
                required=["from_customer_id", "to_customer_id", "amount", "currency", "idempotency_key"]
            )
        )
    } 