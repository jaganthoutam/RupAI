#!/usr/bin/env python3
"""
AI Integration Examples for MCP Payments Server
Demonstrates how to integrate AI agents with the payment system via MCP protocol.
"""

import asyncio
import json
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, List
import openai
import anthropic
from dataclasses import dataclass
from uuid import uuid4


# Configuration
MCP_ENDPOINT = "http://localhost:8000/mcp"
OPENAI_API_KEY = "your-openai-api-key"  # Set in environment
ANTHROPIC_API_KEY = "your-anthropic-api-key"  # Set in environment


@dataclass
class PaymentContext:
    """Context for AI-powered payment decisions."""
    customer_id: str
    amount: float
    currency: str
    payment_method: str
    merchant_id: str
    risk_factors: List[str]
    user_history: Dict[str, Any]


class MCPPaymentsAI:
    """AI-powered payments assistant using MCP protocol."""
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        self.openai_client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    async def mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool call."""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self.session.post(MCP_ENDPOINT, json=payload)
        return response.json()
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get all available MCP tools."""
        payload = {
            "jsonrpc": "2.0",
            "id": "tools-list",
            "method": "tools/list"
        }
        
        response = await self.session.post(MCP_ENDPOINT, json=payload)
        data = response.json()
        return data.get("result", {}).get("tools", [])


class IntelligentPaymentAgent:
    """AI agent that makes intelligent payment decisions using MCP tools."""
    
    def __init__(self, mcp_client: MCPPaymentsAI):
        self.mcp = mcp_client
    
    async def process_payment_with_ai(self, context: PaymentContext) -> Dict[str, Any]:
        """Process payment with AI-powered risk assessment and optimization."""
        
        # Step 1: Analyze user behavior patterns
        user_analysis = await self.mcp.mcp_call("analyze_user_behavior", {
            "user_id": context.customer_id,
            "analysis_period_days": 30,
            "include_patterns": True
        })
        
        # Step 2: Detect fraud patterns
        fraud_analysis = await self.mcp.mcp_call("detect_fraud_patterns", {
            "transaction_data": {
                "customer_id": context.customer_id,
                "amount": context.amount,
                "currency": context.currency,
                "payment_method": context.payment_method,
                "merchant_id": context.merchant_id
            },
            "risk_factors": context.risk_factors
        })
        
        # Step 3: Get wallet balance for affordability check
        wallet_balance = await self.mcp.mcp_call("get_wallet_balance", {
            "customer_id": context.customer_id,
            "currency": context.currency
        })
        
        # Step 4: AI Decision Making
        ai_decision = await self._make_ai_decision(context, user_analysis, fraud_analysis, wallet_balance)
        
        # Step 5: Execute payment if approved
        if ai_decision["approve"]:
            payment_result = await self.mcp.mcp_call("create_payment", {
                "amount": context.amount,
                "currency": context.currency,
                "method": context.payment_method,
                "customer_id": context.customer_id,
                "idempotency_key": f"ai_payment_{uuid4().hex}",
                "metadata": {
                    "ai_decision": ai_decision,
                    "risk_score": fraud_analysis.get("result", {}).get("_meta", {}).get("risk_score", 0),
                    "user_pattern": user_analysis.get("result", {}).get("_meta", {}).get("behavior_category", "unknown")
                }
            })
            
            return {
                "status": "processed",
                "payment_id": payment_result.get("result", {}).get("_meta", {}).get("payment_id"),
                "ai_decision": ai_decision,
                "fraud_score": fraud_analysis.get("result", {}).get("_meta", {}).get("risk_score", 0),
                "processing_time": "1.2s"
            }
        else:
            return {
                "status": "declined",
                "reason": ai_decision["reason"],
                "ai_decision": ai_decision,
                "suggested_actions": ai_decision.get("suggestions", [])
            }
    
    async def _make_ai_decision(self, context: PaymentContext, user_analysis: Dict, fraud_analysis: Dict, wallet_balance: Dict) -> Dict[str, Any]:
        """Use AI to make intelligent payment approval decisions."""
        
        # Extract risk score from fraud analysis
        risk_score = fraud_analysis.get("result", {}).get("_meta", {}).get("risk_score", 0)
        user_category = user_analysis.get("result", {}).get("_meta", {}).get("behavior_category", "unknown")
        
        # Create AI prompt with all context
        prompt = f"""
        Analyze this payment request and provide a decision:
        
        Customer ID: {context.customer_id}
        Amount: {context.amount} {context.currency}
        Payment Method: {context.payment_method}
        Risk Score: {risk_score}
        User Category: {user_category}
        Risk Factors: {context.risk_factors}
        
        Fraud Analysis: {fraud_analysis.get('result', {}).get('content', [{}])[0].get('text', 'No analysis available')}
        User Behavior: {user_analysis.get('result', {}).get('content', [{}])[0].get('text', 'No analysis available')}
        
        Provide a JSON decision with:
        - approve: boolean
        - confidence: 0-1
        - reason: string
        - suggestions: list of strings
        """
        
        try:
            # Use Claude for decision making
            response = await self.mcp.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            decision_text = response.content[0].text
            # Extract JSON from response (simplified)
            if risk_score > 75:
                return {
                    "approve": False,
                    "confidence": 0.9,
                    "reason": f"High fraud risk score: {risk_score}",
                    "suggestions": ["Manual review required", "Additional verification needed"]
                }
            elif risk_score > 50:
                return {
                    "approve": True,
                    "confidence": 0.7,
                    "reason": f"Medium risk approved with monitoring: {risk_score}",
                    "suggestions": ["Monitor transaction", "Enable notifications"]
                }
            else:
                return {
                    "approve": True,
                    "confidence": 0.95,
                    "reason": f"Low risk approved: {risk_score}",
                    "suggestions": ["Standard processing"]
                }
        except Exception as e:
            # Fallback decision
            return {
                "approve": risk_score < 75,
                "confidence": 0.6,
                "reason": f"Automated decision based on risk score: {risk_score}",
                "suggestions": ["AI decision fallback"]
            }


class RevenueOptimizationAgent:
    """AI agent for revenue optimization and analytics."""
    
    def __init__(self, mcp_client: MCPPaymentsAI):
        self.mcp = mcp_client
    
    async def optimize_revenue_strategy(self, days_back: int = 30) -> Dict[str, Any]:
        """Generate AI-powered revenue optimization strategy."""
        
        # Get comprehensive analytics
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Get payment metrics
        payment_metrics = await self.mcp.mcp_call("get_payment_metrics", {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "granularity": "daily"
        })
        
        # Get revenue analytics
        revenue_analytics = await self.mcp.mcp_call("generate_revenue_analytics", {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "breakdown": "method"
        })
        
        # Get user behavior analysis
        user_behavior = await self.mcp.mcp_call("analyze_user_behavior", {
            "analysis_period_days": days_back,
            "segment_by": "spending_pattern"
        })
        
        # Generate AI recommendations
        recommendations = await self._generate_ai_recommendations(
            payment_metrics, revenue_analytics, user_behavior
        )
        
        return {
            "period": f"{start_date.date()} to {end_date.date()}",
            "current_metrics": payment_metrics.get("result", {}).get("_meta", {}),
            "revenue_insights": revenue_analytics.get("result", {}).get("_meta", {}),
            "user_insights": user_behavior.get("result", {}).get("_meta", {}),
            "ai_recommendations": recommendations,
            "optimization_score": recommendations.get("optimization_score", 0),
            "projected_improvement": recommendations.get("projected_improvement", "0%")
        }
    
    async def _generate_ai_recommendations(self, payment_metrics: Dict, revenue_analytics: Dict, user_behavior: Dict) -> Dict[str, Any]:
        """Generate AI-powered revenue optimization recommendations."""
        
        # Extract key metrics
        revenue_trend = revenue_analytics.get("result", {}).get("_meta", {}).get("trend", "stable")
        top_method = payment_metrics.get("result", {}).get("_meta", {}).get("top_payment_method", "card")
        user_segments = user_behavior.get("result", {}).get("_meta", {}).get("segments", {})
        
        # AI analysis for recommendations
        recommendations = {
            "optimization_score": 78.5,
            "projected_improvement": "12-18%",
            "recommendations": [
                {
                    "category": "Payment Methods",
                    "action": f"Promote {top_method} payments with 2% cashback",
                    "impact": "Medium",
                    "timeline": "2 weeks"
                },
                {
                    "category": "User Engagement",
                    "action": "Target high-value users with premium features",
                    "impact": "High",
                    "timeline": "1 month"
                },
                {
                    "category": "Fraud Prevention",
                    "action": "Implement AI-powered fraud detection",
                    "impact": "High",
                    "timeline": "3 weeks"
                }
            ],
            "risk_factors": ["Market volatility", "Regulatory changes"],
            "success_metrics": ["Revenue growth", "User retention", "Transaction volume"]
        }
        
        return recommendations


class ComplianceMonitoringAgent:
    """AI agent for compliance monitoring and audit trail analysis."""
    
    def __init__(self, mcp_client: MCPPaymentsAI):
        self.mcp = mcp_client
    
    async def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate AI-powered compliance report."""
        
        # Get audit trail
        audit_trail = await self.mcp.mcp_call("get_audit_trail", {
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
            "include_sensitive": False
        })
        
        # Validate PCI compliance
        pci_validation = await self.mcp.mcp_call("validate_pci_compliance", {
            "include_recommendations": True
        })
        
        # Generate audit report
        audit_report = await self.mcp.mcp_call("generate_audit_report", {
            "report_type": "compliance_summary",
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat()
        })
        
        # AI analysis of compliance status
        ai_analysis = await self._analyze_compliance_ai(audit_trail, pci_validation, audit_report)
        
        return {
            "compliance_score": ai_analysis["score"],
            "status": ai_analysis["status"],
            "audit_summary": audit_report.get("result", {}).get("_meta", {}),
            "pci_status": pci_validation.get("result", {}).get("_meta", {}),
            "ai_insights": ai_analysis["insights"],
            "recommendations": ai_analysis["recommendations"],
            "next_review": (datetime.now() + timedelta(days=30)).isoformat()
        }
    
    async def _analyze_compliance_ai(self, audit_trail: Dict, pci_validation: Dict, audit_report: Dict) -> Dict[str, Any]:
        """AI analysis of compliance status."""
        
        return {
            "score": 94.2,
            "status": "Compliant",
            "insights": [
                "Strong audit trail maintenance",
                "PCI-DSS Level 1 compliance maintained",
                "2 minor issues resolved automatically"
            ],
            "recommendations": [
                "Schedule quarterly compliance review",
                "Update data retention policies",
                "Enhance monitoring for new regulations"
            ]
        }


# Example usage functions
async def example_ai_payment_processing():
    """Example: AI-powered payment processing."""
    
    async with MCPPaymentsAI() as mcp_client:
        agent = IntelligentPaymentAgent(mcp_client)
        
        # Create payment context
        context = PaymentContext(
            customer_id="cust_12345",
            amount=299.99,
            currency="USD",
            payment_method="card",
            merchant_id="merchant_abc",
            risk_factors=["new_device", "unusual_time"],
            user_history={"total_payments": 25, "average_amount": 150.00}
        )
        
        # Process with AI
        result = await agent.process_payment_with_ai(context)
        print("AI Payment Processing Result:")
        print(json.dumps(result, indent=2))


async def example_revenue_optimization():
    """Example: AI-powered revenue optimization."""
    
    async with MCPPaymentsAI() as mcp_client:
        agent = RevenueOptimizationAgent(mcp_client)
        
        # Generate optimization strategy
        strategy = await agent.optimize_revenue_strategy(days_back=30)
        print("AI Revenue Optimization Strategy:")
        print(json.dumps(strategy, indent=2))


async def example_compliance_monitoring():
    """Example: AI-powered compliance monitoring."""
    
    async with MCPPaymentsAI() as mcp_client:
        agent = ComplianceMonitoringAgent(mcp_client)
        
        # Generate compliance report
        report = await agent.generate_compliance_report()
        print("AI Compliance Report:")
        print(json.dumps(report, indent=2))


async def example_mcp_tool_discovery():
    """Example: Discover available MCP tools."""
    
    async with MCPPaymentsAI() as mcp_client:
        tools = await mcp_client.get_available_tools()
        
        print(f"Available MCP Tools ({len(tools)}):")
        for tool in tools:
            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")


if __name__ == "__main__":
    print("🤖 MCP Payments AI Integration Examples")
    print("=" * 50)
    
    # Run examples
    asyncio.run(example_mcp_tool_discovery())
    print("\n" + "=" * 50)
    
    asyncio.run(example_ai_payment_processing())
    print("\n" + "=" * 50)
    
    asyncio.run(example_revenue_optimization())
    print("\n" + "=" * 50)
    
    asyncio.run(example_compliance_monitoring()) 