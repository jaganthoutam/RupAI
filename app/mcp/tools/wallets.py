"""
Wallet Tools for MCP Server
Enterprise-grade wallet management tools with balance tracking and fund operations.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ..schemas import ToolDefinition, ToolInputSchema, ToolContent, ToolResult


logger = logging.getLogger(__name__)


class GetWalletBalanceInput(BaseModel):
    """Input schema for get_wallet_balance tool."""
    customer_id: str = Field(..., description="Customer identifier")
    currency: Optional[str] = Field(None, description="Specific currency")


class CreateWalletInput(BaseModel):
    """Input schema for create_wallet tool."""
    customer_id: str = Field(..., description="Customer identifier")
    currency: str = Field(..., description="Wallet currency")
    initial_balance: Optional[Decimal] = Field(Decimal("0"), ge=0, description="Initial balance")


class TransferFundsInput(BaseModel):
    """Input schema for transfer_funds tool."""
    from_customer_id: str = Field(..., description="Source customer ID")
    to_customer_id: str = Field(..., description="Target customer ID")
    amount: Decimal = Field(..., gt=0, description="Transfer amount")
    currency: str = Field(..., description="Currency code")
    description: Optional[str] = Field(None, description="Transfer description")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Transfer amount must be greater than 0")
        if v > Decimal("500000"):
            raise ValueError("Transfer amount exceeds maximum limit")
        return v


class AddFundsInput(BaseModel):
    """Input schema for add_funds tool."""
    customer_id: str = Field(..., description="Customer identifier")
    amount: Decimal = Field(..., gt=0, description="Amount to add")
    currency: str = Field(..., description="Currency code")
    source: str = Field(..., description="Funding source")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")


class WithdrawFundsInput(BaseModel):
    """Input schema for withdraw_funds tool."""
    customer_id: str = Field(..., description="Customer identifier")
    amount: Decimal = Field(..., gt=0, description="Amount to withdraw")
    currency: str = Field(..., description="Currency code")
    destination: str = Field(..., description="Withdrawal destination")
    idempotency_key: str = Field(..., min_length=16, description="Idempotency key")


class WalletTools:
    """
    Wallet Tools for MCP Server.
    
    Provides comprehensive wallet management capabilities including:
    - Wallet creation and management
    - Balance tracking and reporting
    - Fund transfers between wallets
    - Add and withdraw operations
    - Transaction history
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
        
    async def initialize(self) -> None:
        """Initialize wallet tools and services."""
        try:
            logger.info("✅ Wallet tools initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize wallet tools: %s", str(e))
            raise
    
    async def shutdown(self) -> None:
        """Shutdown wallet tools gracefully."""
        try:
            logger.info("🔄 Shutting down wallet tools...")
            logger.info("✅ Wallet tools shut down successfully")
        except Exception as e:
            logger.error("❌ Error during wallet tools shutdown: %s", str(e))
            raise
    
    async def get_tool_definitions(self) -> Dict[str, ToolDefinition]:
        """Get all wallet tool definitions for MCP registration."""
        
        tools = {
            "get_wallet_balance": ToolDefinition(
                name="get_wallet_balance",
                description="Retrieve current wallet balance for user",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier"
                        },
                        "currency": {
                            "type": "string",
                            "enum": ["USD", "EUR", "GBP", "INR", "JPY"],
                            "description": "Specific currency (optional)"
                        }
                    },
                    required=["customer_id"]
                )
            ),
            
            "create_wallet": ToolDefinition(
                name="create_wallet",
                description="Create a new wallet for customer",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier"
                        },
                        "currency": {
                            "type": "string",
                            "enum": ["USD", "EUR", "GBP", "INR", "JPY"],
                            "description": "Wallet currency"
                        },
                        "initial_balance": {
                            "type": "number",
                            "minimum": 0,
                            "description": "Initial balance (optional)"
                        }
                    },
                    required=["customer_id", "currency"]
                )
            ),
            
            "transfer_funds": ToolDefinition(
                name="transfer_funds",
                description="Execute P2P or merchant transfer",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "from_customer_id": {
                            "type": "string",
                            "description": "Source customer ID"
                        },
                        "to_customer_id": {
                            "type": "string",
                            "description": "Target customer ID"
                        },
                        "amount": {
                            "type": "number",
                            "minimum": 0.01,
                            "description": "Transfer amount"
                        },
                        "currency": {
                            "type": "string",
                            "enum": ["USD", "EUR", "GBP", "INR", "JPY"],
                            "description": "Currency code"
                        },
                        "description": {
                            "type": "string",
                            "description": "Transfer description"
                        },
                        "idempotency_key": {
                            "type": "string",
                            "minLength": 16,
                            "description": "Idempotency key"
                        }
                    },
                    required=["from_customer_id", "to_customer_id", "amount", "currency", "idempotency_key"]
                )
            ),
            
            "add_funds": ToolDefinition(
                name="add_funds",
                description="Add funds to customer wallet",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier"
                        },
                        "amount": {
                            "type": "number",
                            "minimum": 0.01,
                            "description": "Amount to add"
                        },
                        "currency": {
                            "type": "string",
                            "enum": ["USD", "EUR", "GBP", "INR", "JPY"],
                            "description": "Currency code"
                        },
                        "source": {
                            "type": "string",
                            "description": "Funding source"
                        },
                        "idempotency_key": {
                            "type": "string",
                            "minLength": 16,
                            "description": "Idempotency key"
                        }
                    },
                    required=["customer_id", "amount", "currency", "source", "idempotency_key"]
                )
            ),
            
            "withdraw_funds": ToolDefinition(
                name="withdraw_funds",
                description="Withdraw funds from customer wallet",
                inputSchema=ToolInputSchema(
                    type="object",
                    properties={
                        "customer_id": {
                            "type": "string",
                            "description": "Customer identifier"
                        },
                        "amount": {
                            "type": "number",
                            "minimum": 0.01,
                            "description": "Amount to withdraw"
                        },
                        "currency": {
                            "type": "string",
                            "enum": ["USD", "EUR", "GBP", "INR", "JPY"],
                            "description": "Currency code"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Withdrawal destination"
                        },
                        "idempotency_key": {
                            "type": "string",
                            "minLength": 16,
                            "description": "Idempotency key"
                        }
                    },
                    required=["customer_id", "amount", "currency", "destination", "idempotency_key"]
                )
            )
        }
        
        return tools
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Handle wallet tool calls."""
        
        try:
            # Record metrics
            if self.metrics_collector:
                await self.metrics_collector.record_tool_call("wallet", tool_name)
            
            # Route to appropriate handler
            if tool_name == "get_wallet_balance":
                return await self._handle_get_wallet_balance(arguments)
            elif tool_name == "create_wallet":
                return await self._handle_create_wallet(arguments)
            elif tool_name == "transfer_funds":
                return await self._handle_transfer_funds(arguments)
            elif tool_name == "add_funds":
                return await self._handle_add_funds(arguments)
            elif tool_name == "withdraw_funds":
                return await self._handle_withdraw_funds(arguments)
            else:
                return ToolResult(
                    content=[ToolContent(
                        type="text",
                        text=f"Unknown wallet tool: {tool_name}"
                    )],
                    isError=True
                )
                
        except Exception as e:
            logger.error("Wallet tool call failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text", 
                    text=f"Wallet tool error: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_get_wallet_balance(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle get wallet balance tool call."""
        
        try:
            input_data = GetWalletBalanceInput(**arguments)
            
            # Simulate wallet balance retrieval
            balances = {
                "USD": "1500.00",
                "EUR": "800.50",
                "GBP": "600.25"
            }
            
            result_data = {
                "customer_id": input_data.customer_id,
                "balances": balances if not input_data.currency else {input_data.currency: balances.get(input_data.currency, "0.00")},
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Wallet balance retrieved for customer {input_data.customer_id}"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Get wallet balance failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to get wallet balance: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_create_wallet(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle create wallet tool call."""
        
        try:
            input_data = CreateWalletInput(**arguments)
            
            # Simulate wallet creation
            wallet_id = str(uuid4())
            result_data = {
                "wallet_id": wallet_id,
                "customer_id": input_data.customer_id,
                "currency": input_data.currency,
                "balance": str(input_data.initial_balance or Decimal("0")),
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Log audit event
            if self.audit_service:
                await self.audit_service.log_event(
                    event_type="wallet_created",
                    user_id=input_data.customer_id,
                    metadata=result_data
                )
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Wallet created successfully with ID: {wallet_id}"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Create wallet failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to create wallet: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_transfer_funds(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle transfer funds tool call."""
        
        try:
            input_data = TransferFundsInput(**arguments)
            
            # Simulate fund transfer
            transfer_id = str(uuid4())
            result_data = {
                "transfer_id": transfer_id,
                "from_customer_id": input_data.from_customer_id,
                "to_customer_id": input_data.to_customer_id,
                "amount": str(input_data.amount),
                "currency": input_data.currency,
                "description": input_data.description,
                "status": "completed",
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Transfer completed successfully with ID: {transfer_id}"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Transfer funds failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to transfer funds: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_add_funds(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle add funds tool call."""
        
        try:
            input_data = AddFundsInput(**arguments)
            
            # Simulate adding funds
            transaction_id = str(uuid4())
            result_data = {
                "transaction_id": transaction_id,
                "customer_id": input_data.customer_id,
                "amount": str(input_data.amount),
                "currency": input_data.currency,
                "source": input_data.source,
                "status": "completed",
                "processed_at": datetime.utcnow().isoformat()
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Funds added successfully with transaction ID: {transaction_id}"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Add funds failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to add funds: {str(e)}"
                )],
                isError=True
            )
    
    async def _handle_withdraw_funds(self, arguments: Dict[str, Any]) -> ToolResult:
        """Handle withdraw funds tool call."""
        
        try:
            input_data = WithdrawFundsInput(**arguments)
            
            # Simulate withdrawing funds
            transaction_id = str(uuid4())
            result_data = {
                "transaction_id": transaction_id,
                "customer_id": input_data.customer_id,
                "amount": str(input_data.amount),
                "currency": input_data.currency,
                "destination": input_data.destination,
                "status": "processing",
                "initiated_at": datetime.utcnow().isoformat()
            }
            
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Withdrawal initiated successfully with transaction ID: {transaction_id}"
                )],
                isError=False,
                meta=result_data
            )
            
        except Exception as e:
            logger.error("Withdraw funds failed: %s", str(e))
            return ToolResult(
                content=[ToolContent(
                    type="text",
                    text=f"Failed to withdraw funds: {str(e)}"
                )],
                isError=True
            )

# Function-based implementations for backward compatibility
# These provide direct access to wallet tools without class instantiation

async def get_wallet_balance(
    customer_id: str,
    currency: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve current wallet balance for user.
    
    Args:
        customer_id: Customer identifier
        currency: Specific currency (optional)
        
    Returns:
        Wallet balance information
    """
    try:
        # Create wallet tools instance
        wallet_tools = WalletTools()
        await wallet_tools.initialize()
        
        # Prepare arguments
        arguments = {
            "customer_id": customer_id
        }
        
        if currency:
            arguments["currency"] = currency
            
        # Call the class method
        result = await wallet_tools._handle_get_wallet_balance(arguments)
        
        return {
            "success": not result.isError,
            "data": result.meta if hasattr(result, 'meta') else None,
            "message": result.content[0].text if result.content else "Balance retrieved"
        }
        
    except Exception as e:
        logger.error("Function get_wallet_balance failed: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get wallet balance: {str(e)}"
        }


async def transfer_funds(
    from_customer_id: str,
    to_customer_id: str,
    amount: float,
    currency: str,
    idempotency_key: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute P2P or merchant transfer.
    
    Args:
        from_customer_id: Source customer ID
        to_customer_id: Target customer ID
        amount: Transfer amount
        currency: Currency code
        idempotency_key: Idempotency key
        description: Transfer description
        
    Returns:
        Transfer result
    """
    try:
        # Create wallet tools instance
        wallet_tools = WalletTools()
        await wallet_tools.initialize()
        
        # Prepare arguments
        arguments = {
            "from_customer_id": from_customer_id,
            "to_customer_id": to_customer_id,
            "amount": Decimal(str(amount)),
            "currency": currency,
            "idempotency_key": idempotency_key
        }
        
        if description:
            arguments["description"] = description
            
        # Call the class method
        result = await wallet_tools._handle_transfer_funds(arguments)
        
        return {
            "success": not result.isError,
            "data": result.meta if hasattr(result, 'meta') else None,
            "message": result.content[0].text if result.content else "Transfer completed"
        }
        
    except Exception as e:
        logger.error("Function transfer_funds failed: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to transfer funds: {str(e)}"
        }


async def wallet_transaction_history(
    customer_id: str,
    currency: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get wallet transaction history.
    
    Args:
        customer_id: Customer identifier
        currency: Filter by currency (optional)
        limit: Number of transactions to return
        offset: Number of transactions to skip
        
    Returns:
        Transaction history
    """
    try:
        # Simulate transaction history retrieval
        transactions = []
        for i in range(min(limit, 10)):  # Simulate up to 10 transactions
            transactions.append({
                "transaction_id": str(uuid4()),
                "type": "transfer" if i % 2 == 0 else "deposit",
                "amount": f"{(i + 1) * 10}.00",
                "currency": currency or "USD",
                "description": f"Transaction {i + 1}",
                "status": "completed",
                "created_at": datetime.utcnow().isoformat()
            })
        
        result_data = {
            "customer_id": customer_id,
            "transactions": transactions,
            "total": len(transactions),
            "limit": limit,
            "offset": offset
        }
        
        return {
            "success": True,
            "data": result_data,
            "message": f"Retrieved {len(transactions)} transactions"
        }
        
    except Exception as e:
        logger.error("Function wallet_transaction_history failed: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get transaction history: {str(e)}"
        }


async def top_up_wallet(
    customer_id: str,
    amount: float,
    currency: str,
    source: str,
    idempotency_key: str
) -> Dict[str, Any]:
    """
    Add funds to user wallet.
    
    Args:
        customer_id: Customer identifier
        amount: Amount to add
        currency: Currency code  
        source: Funding source
        idempotency_key: Idempotency key
        
    Returns:
        Top-up result
    """
    try:
        # Create wallet tools instance
        wallet_tools = WalletTools()
        await wallet_tools.initialize()
        
        # Prepare arguments
        arguments = {
            "customer_id": customer_id,
            "amount": Decimal(str(amount)),
            "currency": currency,
            "source": source,
            "idempotency_key": idempotency_key
        }
            
        # Call the class method
        result = await wallet_tools._handle_add_funds(arguments)
        
        return {
            "success": not result.isError,
            "data": result.meta if hasattr(result, 'meta') else None,
            "message": result.content[0].text if result.content else "Funds added"
        }
        
    except Exception as e:
        logger.error("Function top_up_wallet failed: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to top up wallet: {str(e)}"
        }
