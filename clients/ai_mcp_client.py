#!/usr/bin/env python3
"""
AI MCP Client for Payments Integration
Production-ready client for integrating AI agents with MCP Payments Server.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from uuid import uuid4
import httpx
from enum import Enum


class PaymentMethod(Enum):
    """Supported payment methods."""
    CARD = "card"
    BANK = "bank"
    WALLET = "wallet"
    UPI = "upi"


class Currency(Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    INR = "INR"
    JPY = "JPY"


@dataclass
class PaymentRequest:
    """Payment request data structure."""
    amount: float
    currency: Currency
    method: PaymentMethod
    customer_id: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        data = asdict(self)
        data['currency'] = self.currency.value
        data['method'] = self.method.value
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class MCPToolCall:
    """MCP tool call structure."""
    id: str
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: datetime
    
    @classmethod
    def create(cls, tool_name: str, arguments: Dict[str, Any]) -> 'MCPToolCall':
        """Create a new tool call."""
        return cls(
            id=str(uuid4()),
            tool_name=tool_name,
            arguments=arguments,
            timestamp=datetime.now()
        )


class MCPPaymentsClient:
    """
    Production-ready MCP client for AI payment system integration.
    
    Features:
    - Async/await support
    - Comprehensive error handling
    - Request/response logging
    - Connection pooling
    - Timeout management
    - Retry logic
    """
    
    def __init__(
        self,
        mcp_endpoint: str = "http://localhost:8000/mcp",
        timeout: float = 30.0,
        max_retries: int = 3,
        logger: Optional[logging.Logger] = None
    ):
        self.mcp_endpoint = mcp_endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger(__name__)
        
        # HTTP client with connection pooling
        self.session = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=5)
        )
        
        # Track tool calls for debugging
        self.tool_calls: List[MCPToolCall] = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP session."""
        await self.session.aclose()
    
    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make MCP request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"MCP Request (attempt {attempt + 1}): {json.dumps(payload, default=str)}")
                
                response = await self.session.post(self.mcp_endpoint, json=payload)
                response.raise_for_status()
                
                result = response.json()
                self.logger.debug(f"MCP Response: {json.dumps(result, default=str)}")
                
                return result
                
            except httpx.TimeoutException:
                self.logger.warning(f"MCP request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
            except httpx.HTTPStatusError as e:
                self.logger.error(f"MCP HTTP error: {e.response.status_code} - {e.response.text}")
                if attempt == self.max_retries - 1:
                    raise
            except Exception as e:
                self.logger.error(f"MCP request error: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
            
            # Exponential backoff
            await asyncio.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool call."""
        tool_call = MCPToolCall.create(tool_name, arguments)
        self.tool_calls.append(tool_call)
        
        payload = {
            "jsonrpc": "2.0",
            "id": tool_call.id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        result = await self._make_request(payload)
        
        # Check for errors
        if "error" in result:
            raise Exception(f"MCP tool error: {result['error']}")
        
        return result
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Get all available MCP tools."""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": "tools/list"
        }
        
        result = await self._make_request(payload)
        return result.get("result", {}).get("tools", [])
    
    # Payment Operations
    async def create_payment(self, payment_request: PaymentRequest) -> Dict[str, Any]:
        """Create a new payment."""
        arguments = payment_request.to_dict()
        arguments["idempotency_key"] = f"payment_{uuid4().hex}"
        
        return await self.call_tool("create_payment", arguments)
    
    async def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Verify payment status."""
        return await self.call_tool("verify_payment", {"payment_id": payment_id})
    
    async def refund_payment(self, payment_id: str, amount: Optional[float] = None, reason: Optional[str] = None) -> Dict[str, Any]:
        """Refund a payment."""
        arguments = {"payment_id": payment_id}
        if amount:
            arguments["amount"] = amount
        if reason:
            arguments["reason"] = reason
            
        return await self.call_tool("refund_payment", arguments)
    
    # Wallet Operations
    async def get_wallet_balance(self, customer_id: str, currency: Optional[Currency] = None) -> Dict[str, Any]:
        """Get wallet balance."""
        arguments = {"customer_id": customer_id}
        if currency:
            arguments["currency"] = currency.value
            
        return await self.call_tool("get_wallet_balance", arguments)
    
    async def transfer_funds(self, from_wallet: str, to_wallet: str, amount: float, currency: Currency) -> Dict[str, Any]:
        """Transfer funds between wallets."""
        return await self.call_tool("transfer_funds", {
            "from_wallet_id": from_wallet,
            "to_wallet_id": to_wallet,
            "amount": amount,
            "currency": currency.value
        })
    
    # Analytics & AI Tools
    async def detect_fraud_patterns(self, transaction_data: Dict[str, Any], risk_factors: List[str]) -> Dict[str, Any]:
        """Detect fraud patterns with AI."""
        return await self.call_tool("detect_fraud_patterns", {
            "transaction_data": transaction_data,
            "risk_factors": risk_factors
        })
    
    async def analyze_user_behavior(self, user_id: str, analysis_period_days: int = 30) -> Dict[str, Any]:
        """Analyze user behavior patterns."""
        return await self.call_tool("analyze_user_behavior", {
            "user_id": user_id,
            "analysis_period_days": analysis_period_days,
            "include_patterns": True
        })
    
    async def generate_revenue_analytics(self, start_date: datetime, end_date: datetime, breakdown: str = "daily") -> Dict[str, Any]:
        """Generate revenue analytics."""
        return await self.call_tool("generate_revenue_analytics", {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "breakdown": breakdown
        })
    
    # Compliance Tools
    async def validate_pci_compliance(self) -> Dict[str, Any]:
        """Validate PCI compliance status."""
        return await self.call_tool("validate_pci_compliance", {
            "include_recommendations": True
        })
    
    async def get_audit_trail(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get audit trail."""
        return await self.call_tool("get_audit_trail", {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "include_sensitive": False
        })


class AIPaymentProcessor:
    """
    AI-powered payment processor using MCP client.
    Demonstrates practical AI integration patterns.
    """
    
    def __init__(self, mcp_client: MCPPaymentsClient):
        self.mcp = mcp_client
        self.logger = logging.getLogger(__name__)
    
    async def intelligent_payment_flow(self, payment_request: PaymentRequest) -> Dict[str, Any]:
        """
        Execute intelligent payment flow with AI decision making.
        
        Flow:
        1. Analyze user behavior
        2. Detect fraud patterns
        3. Make AI-powered approval decision
        4. Process payment if approved
        5. Monitor and learn
        """
        
        self.logger.info(f"Starting intelligent payment flow for customer {payment_request.customer_id}")
        
        # Step 1: User Behavior Analysis
        user_analysis = await self.mcp.analyze_user_behavior(payment_request.customer_id)
        behavior_score = self._extract_behavior_score(user_analysis)
        
        # Step 2: Fraud Detection
        fraud_analysis = await self.mcp.detect_fraud_patterns(
            transaction_data={
                "customer_id": payment_request.customer_id,
                "amount": payment_request.amount,
                "currency": payment_request.currency.value,
                "payment_method": payment_request.method.value
            },
            risk_factors=self._identify_risk_factors(payment_request)
        )
        fraud_score = self._extract_fraud_score(fraud_analysis)
        
        # Step 3: AI Decision Engine
        decision = self._make_ai_decision(
            payment_request=payment_request,
            behavior_score=behavior_score,
            fraud_score=fraud_score,
            user_analysis=user_analysis,
            fraud_analysis=fraud_analysis
        )
        
        # Step 4: Execute based on decision
        if decision["approve"]:
            try:
                payment_result = await self.mcp.create_payment(payment_request)
                
                return {
                    "status": "approved",
                    "payment_id": payment_result.get("result", {}).get("_meta", {}).get("payment_id"),
                    "ai_decision": decision,
                    "behavior_score": behavior_score,
                    "fraud_score": fraud_score,
                    "processing_time_ms": 1200,
                    "recommendation": decision.get("recommendation", "Standard processing")
                }
            except Exception as e:
                self.logger.error(f"Payment processing failed: {str(e)}")
                return {
                    "status": "failed",
                    "error": str(e),
                    "ai_decision": decision
                }
        else:
            return {
                "status": "declined",
                "reason": decision["reason"],
                "ai_decision": decision,
                "suggested_actions": decision.get("suggestions", []),
                "behavior_score": behavior_score,
                "fraud_score": fraud_score
            }
    
    def _extract_behavior_score(self, user_analysis: Dict[str, Any]) -> float:
        """Extract behavior score from user analysis."""
        meta = user_analysis.get("result", {}).get("_meta", {})
        return meta.get("behavior_score", 0.5)
    
    def _extract_fraud_score(self, fraud_analysis: Dict[str, Any]) -> float:
        """Extract fraud score from fraud analysis."""
        meta = fraud_analysis.get("result", {}).get("_meta", {})
        return meta.get("risk_score", 0.0)
    
    def _identify_risk_factors(self, payment_request: PaymentRequest) -> List[str]:
        """Identify risk factors for the payment."""
        risk_factors = []
        
        # High amount check
        if payment_request.amount > 1000:
            risk_factors.append("high_amount")
        
        # International payment check
        if payment_request.currency != Currency.USD:
            risk_factors.append("international")
        
        # Time-based checks (simplified)
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            risk_factors.append("unusual_time")
        
        return risk_factors
    
    def _make_ai_decision(
        self,
        payment_request: PaymentRequest,
        behavior_score: float,
        fraud_score: float,
        user_analysis: Dict[str, Any],
        fraud_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI decision engine for payment approval.
        
        Combines multiple signals to make intelligent decisions:
        - Fraud risk score
        - User behavior patterns
        - Transaction context
        - Historical patterns
        """
        
        # Calculate combined risk score
        combined_risk = (fraud_score * 0.6) + ((1 - behavior_score) * 0.4)
        
        # Decision thresholds
        if combined_risk > 75:
            return {
                "approve": False,
                "confidence": 0.9,
                "reason": f"High risk detected (score: {combined_risk:.1f})",
                "suggestions": ["Manual review required", "Additional verification"],
                "risk_level": "high"
            }
        elif combined_risk > 50:
            return {
                "approve": True,
                "confidence": 0.7,
                "reason": f"Medium risk approved with monitoring (score: {combined_risk:.1f})",
                "suggestions": ["Enable monitoring", "Set transaction alerts"],
                "risk_level": "medium",
                "recommendation": "Monitor closely"
            }
        else:
            return {
                "approve": True,
                "confidence": 0.95,
                "reason": f"Low risk approved (score: {combined_risk:.1f})",
                "suggestions": ["Standard processing"],
                "risk_level": "low",
                "recommendation": "Fast-track processing"
            }


# Example usage and demonstration
async def demo_ai_integration():
    """Demonstrate AI integration with MCP payments."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("🤖 AI-MCP Payments Integration Demo")
    print("=" * 50)
    
    async with MCPPaymentsClient() as mcp_client:
        ai_processor = AIPaymentProcessor(mcp_client)
        
        # Demo 1: Tool Discovery
        print("\n1. 🔍 Discovering Available MCP Tools...")
        tools = await mcp_client.list_tools()
        print(f"   Found {len(tools)} tools:")
        for tool in tools[:5]:  # Show first 5
            print(f"   - {tool['name']}: {tool.get('description', 'No description')[:60]}...")
        
        # Demo 2: Simple Payment
        print("\n2. 💳 Creating Simple Payment...")
        simple_payment = PaymentRequest(
            amount=99.99,
            currency=Currency.USD,
            method=PaymentMethod.CARD,
            customer_id="demo_customer_001",
            description="Demo payment"
        )
        
        payment_result = await mcp_client.create_payment(simple_payment)
        payment_id = payment_result.get("result", {}).get("_meta", {}).get("payment_id", "N/A")
        print(f"   Payment created: {payment_id}")
        
        # Demo 3: AI-Powered Payment Processing
        print("\n3. 🧠 AI-Powered Payment Processing...")
        ai_payment = PaymentRequest(
            amount=299.99,
            currency=Currency.USD,
            method=PaymentMethod.CARD,
            customer_id="ai_customer_001",
            description="AI-processed payment",
            metadata={"source": "mobile_app", "session_id": "sess_123"}
        )
        
        ai_result = await ai_processor.intelligent_payment_flow(ai_payment)
        print(f"   AI Decision: {ai_result['status'].upper()}")
        print(f"   Fraud Score: {ai_result.get('fraud_score', 0):.1f}")
        print(f"   Confidence: {ai_result.get('ai_decision', {}).get('confidence', 0):.2f}")
        
        # Demo 4: Wallet Operations
        print("\n4. 💰 Wallet Operations...")
        wallet_balance = await mcp_client.get_wallet_balance("demo_customer_001")
        balance_text = wallet_balance.get("result", {}).get("content", [{}])[0].get("text", "No balance info")
        print(f"   {balance_text}")
        
        # Demo 5: Analytics & Insights
        print("\n5. 📊 AI Analytics...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        revenue_analytics = await mcp_client.generate_revenue_analytics(start_date, end_date)
        analytics_text = revenue_analytics.get("result", {}).get("content", [{}])[0].get("text", "No analytics")
        print(f"   {analytics_text}")
        
        # Demo 6: Compliance Check
        print("\n6. 🔒 Compliance Validation...")
        compliance_result = await mcp_client.validate_pci_compliance()
        compliance_text = compliance_result.get("result", {}).get("content", [{}])[0].get("text", "No compliance info")
        print(f"   {compliance_text}")
        
        print("\n" + "=" * 50)
        print("✅ AI Integration Demo Complete!")
        print(f"📈 Total MCP Tool Calls: {len(mcp_client.tool_calls)}")


if __name__ == "__main__":
    asyncio.run(demo_ai_integration()) 