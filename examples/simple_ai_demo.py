#!/usr/bin/env python3
"""
Simple AI Integration Demo - Working with Available MCP Tools
Shows how AI agents can interact with the MCP payments server.
"""

import asyncio
import json
import httpx
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime


class SimpleAIAgent:
    """Simple AI agent demonstrating MCP integration."""
    
    def __init__(self, mcp_endpoint: str = "http://localhost:8000/mcp"):
        self.mcp_endpoint = mcp_endpoint
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    async def mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Make MCP tool call."""
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
        return response.json()
    
    async def list_tools(self) -> Dict[str, Any]:
        """Get available MCP tools."""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": "tools/list"
        }
        
        response = await self.session.post(self.mcp_endpoint, json=payload)
        return response.json()
    
    async def intelligent_payment_decision(self, amount: float, customer_id: str) -> Dict[str, Any]:
        """Make intelligent payment decision using available AI features."""
        
        print(f"🧠 AI Agent analyzing payment: ${amount} for customer {customer_id}")
        
        # Step 1: Check wallet balance first
        print("   Step 1: Checking wallet balance...")
        wallet_result = await self.mcp_call("get_wallet_balance", {
            "customer_id": customer_id,
            "currency": "USD"
        })
        
        # Step 2: AI decision logic based on amount and context
        risk_score = self._calculate_risk_score(amount, customer_id)
        decision = self._make_ai_decision(amount, risk_score, wallet_result)
        
        print(f"   AI Risk Score: {risk_score:.1f}/100")
        print(f"   AI Decision: {decision['action'].upper()}")
        
        # Step 3: Execute decision
        if decision["action"] == "approve":
            print("   Step 2: Creating payment...")
            payment_result = await self.mcp_call("create_payment", {
                "amount": amount,
                "currency": "USD",
                "method": "card",
                "customer_id": customer_id,
                "idempotency_key": f"ai_payment_{uuid4().hex}",
                "description": f"AI-approved payment (risk: {risk_score:.1f})"
            })
            
            if not payment_result.get("error"):
                payment_id = payment_result.get("result", {}).get("_meta", {}).get("payment_id", "N/A")
                return {
                    "status": "success",
                    "action": "payment_created",
                    "payment_id": payment_id,
                    "ai_risk_score": risk_score,
                    "ai_confidence": decision["confidence"],
                    "reasoning": decision["reasoning"]
                }
            else:
                return {
                    "status": "error",
                    "action": "payment_failed",
                    "error": payment_result.get("error"),
                    "ai_risk_score": risk_score
                }
        else:
            return {
                "status": "declined",
                "action": "payment_blocked",
                "ai_risk_score": risk_score,
                "reasoning": decision["reasoning"],
                "suggestions": decision.get("suggestions", [])
            }
    
    def _calculate_risk_score(self, amount: float, customer_id: str) -> float:
        """Calculate AI risk score (0-100, higher = more risky)."""
        risk_score = 0.0
        
        # Amount-based risk
        if amount > 1000:
            risk_score += 30
        elif amount > 500:
            risk_score += 15
        elif amount > 100:
            risk_score += 5
        
        # Customer pattern analysis (simplified)
        if "test" in customer_id.lower():
            risk_score += 10  # Test accounts slightly riskier
        
        # Time-based risk
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 20  # Unusual hours
        
        # New customer risk
        if "new" in customer_id.lower():
            risk_score += 25
        
        return min(risk_score, 100)  # Cap at 100
    
    def _make_ai_decision(self, amount: float, risk_score: float, wallet_result: Dict[str, Any]) -> Dict[str, Any]:
        """AI decision engine for payment approval."""
        
        if risk_score > 75:
            return {
                "action": "block",
                "confidence": 0.9,
                "reasoning": f"High risk detected (score: {risk_score:.1f}) - requires manual review",
                "suggestions": ["Manual verification required", "Additional identity checks"]
            }
        elif risk_score > 50:
            return {
                "action": "approve",
                "confidence": 0.7,
                "reasoning": f"Medium risk approved with monitoring (score: {risk_score:.1f})",
                "suggestions": ["Enable transaction monitoring", "Set alerts for future payments"]
            }
        else:
            return {
                "action": "approve",
                "confidence": 0.95,
                "reasoning": f"Low risk approved for fast processing (score: {risk_score:.1f})",
                "suggestions": ["Standard processing recommended"]
            }


async def demo_ai_payments():
    """Demonstrate AI-powered payment processing."""
    
    print("🤖 Simple AI-MCP Integration Demo")
    print("=" * 50)
    
    async with SimpleAIAgent() as ai_agent:
        
        # Demo 1: List available tools
        print("\n1. 🔍 Discovering MCP Tools...")
        tools_result = await ai_agent.list_tools()
        tools = tools_result.get("result", {}).get("tools", [])
        print(f"   Found {len(tools)} available tools:")
        for tool in tools[:5]:
            print(f"   - {tool['name']}")
        
        # Demo 2: Low-risk payment (should approve)
        print("\n2. 💳 AI Processing: Low-Risk Payment...")
        low_risk_result = await ai_agent.intelligent_payment_decision(
            amount=50.00,
            customer_id="customer_001"
        )
        print(f"   Result: {low_risk_result['status'].upper()}")
        if low_risk_result['status'] == 'success':
            print(f"   Payment ID: {low_risk_result['payment_id']}")
        print(f"   AI Reasoning: {low_risk_result['reasoning']}")
        
        # Demo 3: Medium-risk payment (should approve with monitoring)
        print("\n3. ⚠️  AI Processing: Medium-Risk Payment...")
        medium_risk_result = await ai_agent.intelligent_payment_decision(
            amount=750.00,
            customer_id="test_customer_002"
        )
        print(f"   Result: {medium_risk_result['status'].upper()}")
        if medium_risk_result['status'] == 'success':
            print(f"   Payment ID: {medium_risk_result['payment_id']}")
        print(f"   AI Reasoning: {medium_risk_result['reasoning']}")
        
        # Demo 4: High-risk payment (should block)
        print("\n4. 🚫 AI Processing: High-Risk Payment...")
        high_risk_result = await ai_agent.intelligent_payment_decision(
            amount=2500.00,
            customer_id="new_test_customer_003"
        )
        print(f"   Result: {high_risk_result['status'].upper()}")
        print(f"   AI Reasoning: {high_risk_result['reasoning']}")
        if high_risk_result.get('suggestions'):
            print(f"   AI Suggestions: {', '.join(high_risk_result['suggestions'])}")
        
        # Demo 5: Wallet balance check
        print("\n5. 💰 AI Wallet Analysis...")
        wallet_result = await ai_agent.mcp_call("get_wallet_balance", {
            "customer_id": "customer_001",
            "currency": "USD"
        })
        
        if not wallet_result.get("error"):
            wallet_text = wallet_result.get("result", {}).get("content", [{}])[0].get("text", "No info")
            print(f"   {wallet_text}")
        
        print("\n" + "=" * 50)
        print("✅ AI Integration Demo Complete!")
        print("🎯 AI successfully analyzed and processed payments using MCP tools")


async def demo_batch_ai_processing():
    """Demonstrate batch AI processing of multiple payments."""
    
    print("\n🔄 AI Batch Processing Demo")
    print("=" * 30)
    
    async with SimpleAIAgent() as ai_agent:
        
        # Batch of payments with different risk profiles
        payments = [
            {"amount": 25.00, "customer_id": "customer_low_risk"},
            {"amount": 150.00, "customer_id": "customer_medium"},
            {"amount": 800.00, "customer_id": "test_customer_high"},
            {"amount": 1500.00, "customer_id": "new_customer_very_high"},
            {"amount": 75.00, "customer_id": "trusted_customer"}
        ]
        
        results = []
        approved_count = 0
        blocked_count = 0
        total_amount = 0
        
        print(f"Processing {len(payments)} payments with AI...")
        
        for i, payment in enumerate(payments, 1):
            print(f"\n  Payment {i}: ${payment['amount']} for {payment['customer_id']}")
            
            result = await ai_agent.intelligent_payment_decision(
                payment['amount'], 
                payment['customer_id']
            )
            
            results.append(result)
            
            if result['status'] == 'success':
                approved_count += 1
                total_amount += payment['amount']
                print(f"    ✅ APPROVED (Risk: {result['ai_risk_score']:.1f})")
            else:
                blocked_count += 1
                print(f"    🚫 BLOCKED (Risk: {result['ai_risk_score']:.1f})")
        
        # AI Analysis Summary
        print(f"\n📊 AI Batch Processing Summary:")
        print(f"   Total Payments: {len(payments)}")
        print(f"   Approved: {approved_count} ✅")
        print(f"   Blocked: {blocked_count} 🚫")
        print(f"   Total Approved Amount: ${total_amount:.2f}")
        print(f"   AI Approval Rate: {(approved_count/len(payments)*100):.1f}%")


if __name__ == "__main__":
    print("🚀 Starting AI-MCP Integration Demos...")
    
    # Run main demo
    asyncio.run(demo_ai_payments())
    
    # Run batch processing demo
    asyncio.run(demo_batch_ai_processing()) 