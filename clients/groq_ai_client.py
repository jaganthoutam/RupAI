#!/usr/bin/env python3
"""
Production Groq AI Client for MCP Payments Server
Ultra-fast AI inference for real-time payment processing, fraud detection, and decision making.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from uuid import uuid4
import httpx
from enum import Enum
import os
from groq import Groq


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PaymentContext:
    """Comprehensive payment context for AI analysis."""
    customer_id: str
    amount: float
    currency: Currency
    method: PaymentMethod
    merchant_id: Optional[str] = None
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    previous_transactions: Optional[int] = None
    account_age_days: Optional[int] = None
    location: Optional[str] = None
    time_of_day: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for processing."""
        data = asdict(self)
        data['currency'] = self.currency.value if isinstance(self.currency, Currency) else self.currency
        data['method'] = self.method.value if isinstance(self.method, PaymentMethod) else self.method
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class AIDecision:
    """AI decision structure."""
    approve: bool
    risk_level: RiskLevel
    confidence: float
    risk_score: float
    reasoning: str
    recommendations: List[str]
    processing_time_ms: float
    model_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['risk_level'] = self.risk_level.value
        return data


class GroqMCPClient:
    """
    Production-ready Groq AI client for MCP Payments Server.
    
    Features:
    - Ultra-fast AI inference with Groq
    - Real-time fraud detection
    - Intelligent payment routing
    - Risk assessment and scoring
    - Production-grade error handling
    - Comprehensive logging and monitoring
    """
    
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        mcp_endpoint: str = "http://localhost:8000/mcp",
        model: str = "llama-3.1-8b-instant",  # Fast Groq model
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        # Initialize Groq client
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable or groq_api_key parameter required")
        
        self.groq_client = Groq(api_key=self.groq_api_key)
        self.model = model
        self.mcp_endpoint = mcp_endpoint
        self.timeout = timeout
        self.max_retries = max_retries
        
        # HTTP client for MCP calls
        self.session = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=10)
        )
        
        # Performance tracking
        self.metrics = {
            "total_decisions": 0,
            "approved_payments": 0,
            "blocked_payments": 0,
            "total_amount_processed": 0.0,
            "avg_response_time_ms": 0.0,
            "groq_calls": 0,
            "mcp_calls": 0
        }
        
        logger.info(f"GroqMCPClient initialized with model: {model}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close HTTP session and log final metrics."""
        await self.session.aclose()
        logger.info(f"GroqMCPClient metrics: {self.metrics}")
    
    async def mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool call with retry logic."""
        self.metrics["mcp_calls"] += 1
        
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": str(uuid4()),
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
                
                response = await self.session.post(self.mcp_endpoint, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                if "error" in result:
                    logger.error(f"MCP tool error: {result['error']}")
                    if attempt == self.max_retries - 1:
                        raise Exception(f"MCP tool error: {result['error']}")
                else:
                    return result
                
            except Exception as e:
                logger.warning(f"MCP call attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Max retries exceeded for MCP call")
    
    def groq_analyze(self, prompt: str, max_tokens: int = 1000) -> str:
        """Synchronous Groq AI analysis."""
        self.metrics["groq_calls"] += 1
        
        try:
            start_time = time.time()
            
            completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert financial AI analyst specializing in payment fraud detection and risk assessment. Provide clear, actionable insights based on transaction data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.1,  # Low temperature for consistent decisions
                top_p=0.9
            )
            
            response_time = (time.time() - start_time) * 1000
            logger.debug(f"Groq response time: {response_time:.2f}ms")
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise
    
    async def intelligent_payment_processing(self, payment_context: PaymentContext) -> AIDecision:
        """
        Process payment with AI-powered fraud detection and risk assessment.
        
        This is the main production method that combines:
        1. MCP tool calls for data gathering
        2. Groq AI for intelligent analysis
        3. Real-time decision making
        4. Performance optimization
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing payment: ${payment_context.amount} for {payment_context.customer_id}")
            
            # Step 1: Gather context data via MCP
            context_data = await self._gather_payment_context(payment_context)
            
            # Step 2: AI-powered risk analysis with Groq
            risk_analysis = await self._groq_risk_analysis(payment_context, context_data)
            
            # Step 3: Make intelligent decision
            ai_decision = self._make_production_decision(payment_context, risk_analysis, context_data)
            
            # Step 4: Execute decision via MCP
            if ai_decision.approve:
                execution_result = await self._execute_payment(payment_context, ai_decision)
                ai_decision.recommendations.append(f"Payment executed: {execution_result.get('payment_id', 'N/A')}")
            
            # Step 5: Update metrics
            processing_time = (time.time() - start_time) * 1000
            ai_decision.processing_time_ms = processing_time
            
            self._update_metrics(ai_decision, payment_context.amount)
            
            logger.info(f"AI Decision: {ai_decision.approve} (Risk: {ai_decision.risk_score:.1f}, Time: {processing_time:.2f}ms)")
            
            return ai_decision
            
        except Exception as e:
            logger.error(f"Payment processing failed: {str(e)}")
            
            # Return safe fallback decision
            return AIDecision(
                approve=False,
                risk_level=RiskLevel.CRITICAL,
                confidence=1.0,
                risk_score=100.0,
                reasoning=f"Processing error: {str(e)}",
                recommendations=["Manual review required", "System error occurred"],
                processing_time_ms=(time.time() - start_time) * 1000,
                model_version=self.model
            )
    
    async def _gather_payment_context(self, payment_context: PaymentContext) -> Dict[str, Any]:
        """Gather comprehensive context data via MCP calls."""
        context_data = {}
        
        try:
            # Get wallet balance
            wallet_result = await self.mcp_call("get_wallet_balance", {
                "customer_id": payment_context.customer_id,
                "currency": payment_context.currency.value
            })
            context_data["wallet_balance"] = wallet_result
            
            # Get payment history (if available)
            try:
                history_result = await self.mcp_call("wallet_transaction_history", {
                    "wallet_id": payment_context.customer_id,
                    "limit": 10
                })
                context_data["transaction_history"] = history_result
            except:
                context_data["transaction_history"] = {"error": "not_available"}
            
            # System health check
            health_result = await self.mcp_call("perform_health_check", {})
            context_data["system_health"] = health_result
            
        except Exception as e:
            logger.warning(f"Context gathering partial failure: {str(e)}")
            context_data["gathering_error"] = str(e)
        
        return context_data
    
    async def _groq_risk_analysis(self, payment_context: PaymentContext, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI risk analysis using Groq."""
        
        # Construct comprehensive analysis prompt
        prompt = self._build_analysis_prompt(payment_context, context_data)
        
        # Get AI analysis
        try:
            analysis_text = self.groq_analyze(prompt, max_tokens=800)
            
            # Parse AI response (simplified JSON extraction)
            risk_analysis = self._parse_groq_response(analysis_text)
            risk_analysis["raw_response"] = analysis_text
            
            return risk_analysis
            
        except Exception as e:
            logger.error(f"Groq analysis failed: {str(e)}")
            # Fallback to rule-based analysis
            return self._fallback_risk_analysis(payment_context)
    
    def _build_analysis_prompt(self, payment_context: PaymentContext, context_data: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt for Groq."""
        
        prompt = f"""
PAYMENT FRAUD ANALYSIS REQUEST

TRANSACTION DETAILS:
- Amount: ${payment_context.amount} {payment_context.currency.value}
- Customer ID: {payment_context.customer_id}
- Payment Method: {payment_context.method.value}
- Merchant: {payment_context.merchant_id or 'N/A'}
- Device: {payment_context.device_fingerprint or 'N/A'}
- Location: {payment_context.location or 'N/A'}
- Time of Day: {payment_context.time_of_day or datetime.now().hour}
- IP Address: {payment_context.ip_address or 'N/A'}

CUSTOMER CONTEXT:
- Previous Transactions: {payment_context.previous_transactions or 'Unknown'}
- Account Age: {payment_context.account_age_days or 'Unknown'} days

SYSTEM DATA:
- Wallet Balance: {context_data.get('wallet_balance', {}).get('result', {}).get('content', [{}])[0].get('text', 'N/A')}
- System Health: {context_data.get('system_health', {}).get('result', {}).get('content', [{}])[0].get('text', 'Healthy')}

ANALYSIS REQUIRED:
1. Calculate risk score (0-100, where 100 is highest risk)
2. Identify specific risk factors
3. Provide approval recommendation
4. Suggest monitoring actions

Respond in this JSON format:
{{
    "risk_score": <number 0-100>,
    "risk_factors": ["factor1", "factor2"],
    "approval_recommendation": "approve|decline|review",
    "confidence": <number 0-1>,
    "reasoning": "detailed explanation",
    "monitoring_actions": ["action1", "action2"]
}}
"""
        return prompt
    
    def _parse_groq_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Groq AI response into structured data."""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                return parsed
            else:
                # Fallback parsing
                return self._fallback_parse(response_text)
                
        except json.JSONDecodeError:
            return self._fallback_parse(response_text)
    
    def _fallback_parse(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails."""
        # Simple keyword-based parsing
        risk_score = 50.0  # Default medium risk
        
        if "high risk" in response_text.lower() or "decline" in response_text.lower():
            risk_score = 80.0
        elif "low risk" in response_text.lower() or "approve" in response_text.lower():
            risk_score = 20.0
        
        return {
            "risk_score": risk_score,
            "risk_factors": ["parsing_fallback"],
            "approval_recommendation": "approve" if risk_score < 60 else "decline",
            "confidence": 0.6,
            "reasoning": "Fallback analysis due to parsing error",
            "monitoring_actions": ["manual_review"]
        }
    
    def _fallback_risk_analysis(self, payment_context: PaymentContext) -> Dict[str, Any]:
        """Fallback risk analysis when AI is unavailable."""
        risk_score = 0.0
        risk_factors = []
        
        # Amount-based risk
        if payment_context.amount > 5000:
            risk_score += 40
            risk_factors.append("high_amount")
        elif payment_context.amount > 1000:
            risk_score += 20
            risk_factors.append("medium_amount")
        
        # Time-based risk
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 25
            risk_factors.append("unusual_time")
        
        # Customer risk
        if payment_context.previous_transactions is not None and payment_context.previous_transactions < 3:
            risk_score += 30
            risk_factors.append("new_customer")
        
        return {
            "risk_score": min(risk_score, 100),
            "risk_factors": risk_factors,
            "approval_recommendation": "approve" if risk_score < 60 else "decline",
            "confidence": 0.7,
            "reasoning": "Rule-based fallback analysis",
            "monitoring_actions": ["standard_monitoring"]
        }
    
    def _make_production_decision(
        self, 
        payment_context: PaymentContext, 
        risk_analysis: Dict[str, Any], 
        context_data: Dict[str, Any]
    ) -> AIDecision:
        """Make production-grade payment decision."""
        
        risk_score = risk_analysis.get("risk_score", 50.0)
        confidence = risk_analysis.get("confidence", 0.5)
        reasoning = risk_analysis.get("reasoning", "AI analysis completed")
        
        # Determine risk level and approval
        if risk_score >= 80:
            risk_level = RiskLevel.CRITICAL
            approve = False
            recommendations = ["Immediate manual review", "Additional verification required", "Consider blocking customer"]
        elif risk_score >= 60:
            risk_level = RiskLevel.HIGH
            approve = False
            recommendations = ["Manual review required", "Enhanced monitoring", "Verify customer identity"]
        elif risk_score >= 40:
            risk_level = RiskLevel.MEDIUM
            approve = True
            recommendations = ["Monitor transaction", "Set alerts for future payments", "Review in 24 hours"]
        else:
            risk_level = RiskLevel.LOW
            approve = True
            recommendations = ["Standard processing", "Normal monitoring"]
        
        # Add AI-specific recommendations
        ai_recommendations = risk_analysis.get("monitoring_actions", [])
        recommendations.extend(ai_recommendations)
        
        return AIDecision(
            approve=approve,
            risk_level=risk_level,
            confidence=confidence,
            risk_score=risk_score,
            reasoning=reasoning,
            recommendations=recommendations,
            processing_time_ms=0.0,  # Will be set later
            model_version=self.model
        )
    
    async def _execute_payment(self, payment_context: PaymentContext, ai_decision: AIDecision) -> Dict[str, Any]:
        """Execute approved payment via MCP."""
        try:
            payment_result = await self.mcp_call("create_payment", {
                "amount": payment_context.amount,
                "currency": payment_context.currency.value,
                "method": payment_context.method.value,
                "customer_id": payment_context.customer_id,
                "idempotency_key": f"groq_ai_{uuid4().hex}",
                "description": f"AI-approved payment (Groq risk: {ai_decision.risk_score:.1f})",
                "metadata": {
                    "ai_model": self.model,
                    "risk_score": ai_decision.risk_score,
                    "risk_level": ai_decision.risk_level.value,
                    "confidence": ai_decision.confidence
                }
            })
            
            return payment_result.get("result", {}).get("_meta", {})
            
        except Exception as e:
            logger.error(f"Payment execution failed: {str(e)}")
            raise
    
    def _update_metrics(self, ai_decision: AIDecision, amount: float):
        """Update performance metrics."""
        self.metrics["total_decisions"] += 1
        
        if ai_decision.approve:
            self.metrics["approved_payments"] += 1
            self.metrics["total_amount_processed"] += amount
        else:
            self.metrics["blocked_payments"] += 1
        
        # Update average response time
        prev_avg = self.metrics["avg_response_time_ms"]
        new_avg = (prev_avg * (self.metrics["total_decisions"] - 1) + ai_decision.processing_time_ms) / self.metrics["total_decisions"]
        self.metrics["avg_response_time_ms"] = new_avg
    
    async def batch_process_payments(self, payment_contexts: List[PaymentContext]) -> List[AIDecision]:
        """Process multiple payments concurrently for high throughput."""
        logger.info(f"Batch processing {len(payment_contexts)} payments")
        
        # Process payments concurrently
        tasks = [self.intelligent_payment_processing(context) for context in payment_contexts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch payment {i} failed: {str(result)}")
                # Create error decision
                error_decision = AIDecision(
                    approve=False,
                    risk_level=RiskLevel.CRITICAL,
                    confidence=1.0,
                    risk_score=100.0,
                    reasoning=f"Batch processing error: {str(result)}",
                    recommendations=["Manual review required"],
                    processing_time_ms=0.0,
                    model_version=self.model
                )
                processed_results.append(error_decision)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self.metrics,
            "approval_rate": (self.metrics["approved_payments"] / max(self.metrics["total_decisions"], 1)) * 100,
            "average_amount": self.metrics["total_amount_processed"] / max(self.metrics["approved_payments"], 1),
            "model": self.model,
            "groq_api_efficiency": self.metrics["groq_calls"] / max(self.metrics["total_decisions"], 1)
        }


# Production utility functions
async def create_payment_context_from_request(request_data: Dict[str, Any]) -> PaymentContext:
    """Create PaymentContext from API request data."""
    return PaymentContext(
        customer_id=request_data["customer_id"],
        amount=float(request_data["amount"]),
        currency=Currency(request_data.get("currency", "USD")),
        method=PaymentMethod(request_data.get("method", "card")),
        merchant_id=request_data.get("merchant_id"),
        device_fingerprint=request_data.get("device_fingerprint"),
        ip_address=request_data.get("ip_address"),
        user_agent=request_data.get("user_agent"),
        previous_transactions=request_data.get("previous_transactions"),
        account_age_days=request_data.get("account_age_days"),
        location=request_data.get("location"),
        time_of_day=datetime.now().hour
    )


# Example production usage
async def production_demo():
    """Production demonstration of Groq AI integration."""
    
    print("🚀 Production Groq AI-MCP Integration Demo")
    print("=" * 60)
    
    # Initialize with production settings
    async with GroqMCPClient(
        model="llama-3.1-8b-instant",  # Fast, capable model
        timeout=15.0,  # Production timeout
        max_retries=2   # Quick failover
    ) as groq_client:
        
        # Test 1: Single high-value payment
        print("\n1. 🧠 Processing High-Value Payment with Groq AI...")
        high_value_context = PaymentContext(
            customer_id="premium_customer_001",
            amount=5000.00,
            currency=Currency.USD,
            method=PaymentMethod.CARD,
            merchant_id="merchant_luxury_goods",
            previous_transactions=45,
            account_age_days=365,
            location="New York, NY"
        )
        
        decision = await groq_client.intelligent_payment_processing(high_value_context)
        print(f"   Decision: {'✅ APPROVED' if decision.approve else '🚫 BLOCKED'}")
        print(f"   Risk Score: {decision.risk_score:.1f}/100")
        print(f"   Confidence: {decision.confidence:.2f}")
        print(f"   Processing Time: {decision.processing_time_ms:.2f}ms")
        print(f"   AI Reasoning: {decision.reasoning}")
        
        # Test 2: Batch processing
        print("\n2. ⚡ Batch Processing with Groq AI...")
        batch_contexts = [
            PaymentContext("customer_001", 100.00, Currency.USD, PaymentMethod.CARD, previous_transactions=5),
            PaymentContext("customer_002", 2500.00, Currency.EUR, PaymentMethod.BANK, previous_transactions=20),
            PaymentContext("new_customer_003", 750.00, Currency.USD, PaymentMethod.CARD, previous_transactions=0),
        ]
        
        batch_start = time.time()
        batch_decisions = await groq_client.batch_process_payments(batch_contexts)
        batch_time = (time.time() - batch_start) * 1000
        
        approved = sum(1 for d in batch_decisions if d.approve)
        print(f"   Batch Results: {approved}/{len(batch_decisions)} approved in {batch_time:.2f}ms")
        
        for i, decision in enumerate(batch_decisions):
            status = "✅" if decision.approve else "🚫"
            print(f"   Payment {i+1}: {status} Risk: {decision.risk_score:.1f}")
        
        # Test 3: Performance metrics
        print("\n3. 📊 Production Performance Metrics:")
        metrics = groq_client.get_metrics()
        print(f"   Total Decisions: {metrics['total_decisions']}")
        print(f"   Approval Rate: {metrics['approval_rate']:.1f}%")
        print(f"   Avg Response Time: {metrics['avg_response_time_ms']:.2f}ms")
        print(f"   Total Amount Processed: ${metrics['total_amount_processed']:,.2f}")
        print(f"   Groq API Calls: {metrics['groq_calls']}")
        print(f"   MCP API Calls: {metrics['mcp_calls']}")
        
        print("\n" + "=" * 60)
        print("🎯 Production Groq AI Integration Complete!")
        print(f"⚡ Ultra-fast AI inference with {metrics['avg_response_time_ms']:.0f}ms average response time")


if __name__ == "__main__":
    # Set your Groq API key
    # export GROQ_API_KEY="your-groq-api-key-here"
    
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Please set GROQ_API_KEY environment variable")
        print("   Get your free API key at: https://console.groq.com/")
        print("   export GROQ_API_KEY='your-key-here'")
    else:
        asyncio.run(production_demo()) 