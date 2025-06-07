"""
Advanced Features API Endpoints
MCP Tools, AI Insights, Custom Reports, Chat Support, and Documentation.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from uuid import uuid4
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, Query, status, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..auth.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/advanced", tags=["Advanced Features"])

# Request/Response Models
class MCPToolCall(BaseModel):
    tool_name: str = Field(..., description="MCP tool name")
    arguments: Dict[str, Any] = Field(default={}, description="Tool arguments")

class MCPToolResponse(BaseModel):
    tool_name: str
    success: bool
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time: float
    timestamp: datetime

class AIInsightRequest(BaseModel):
    insight_type: str = Field(..., description="Type of insight to generate")
    data_source: str = Field(..., description="Data source for analysis")
    parameters: Dict[str, Any] = Field(default={}, description="Analysis parameters")
    time_range: Optional[Dict[str, str]] = Field(None, description="Time range for analysis")

class AIInsightResponse(BaseModel):
    insight_type: str
    title: str
    summary: str
    detailed_analysis: str
    recommendations: List[str]
    confidence_score: float
    data_points: int
    generated_at: datetime
    expires_at: datetime
    visualization_data: Optional[Dict[str, Any]]

class CustomReportCreate(BaseModel):
    name: str = Field(..., description="Report name")
    description: Optional[str] = Field(None, description="Report description")
    data_sources: List[str] = Field(..., description="Data sources to include")
    filters: Dict[str, Any] = Field(default={}, description="Report filters")
    grouping: List[str] = Field(default=[], description="Grouping fields")
    metrics: List[str] = Field(..., description="Metrics to calculate")
    chart_type: str = Field(default="table", description="Chart type")
    schedule: Optional[Dict[str, Any]] = Field(None, description="Report schedule")

class CustomReportResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    data_sources: List[str]
    filters: Dict[str, Any]
    grouping: List[str]
    metrics: List[str]
    chart_type: str
    schedule: Optional[Dict[str, Any]]
    created_by: str
    created_at: datetime
    last_generated: Optional[datetime]
    status: str

class ChatSupportMessage(BaseModel):
    message: str = Field(..., description="Chat message")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Additional context")

class ChatSupportResponse(BaseModel):
    session_id: str
    message: str
    response: str
    response_type: str
    confidence: float
    suggested_actions: List[Dict[str, str]]
    timestamp: datetime
    response_time: float

class DocumentationSearch(BaseModel):
    query: str = Field(..., description="Search query")
    category: Optional[str] = Field(None, description="Documentation category")
    tags: List[str] = Field(default=[], description="Filter tags")

class DocumentationResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    last_updated: datetime
    relevance_score: float
    author: str

# MCP Tool Interface
@router.get("/mcp/tools", response_model=List[Dict[str, Any]])
async def get_available_mcp_tools(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get available MCP tools."""
    try:
        # Simulate available MCP tools
        tools = [
            {
                "name": "create_payment",
                "description": "Create a new payment transaction",
                "category": "payments",
                "parameters": {
                    "amount": {"type": "number", "required": True},
                    "currency": {"type": "string", "required": True},
                    "customer_id": {"type": "string", "required": True}
                },
                "permissions_required": ["payments.write"]
            },
            {
                "name": "analyze_fraud_patterns",
                "description": "Analyze fraud patterns in transaction data",
                "category": "fraud_detection",
                "parameters": {
                    "time_range": {"type": "string", "required": False},
                    "threshold": {"type": "number", "required": False}
                },
                "permissions_required": ["fraud.read"]
            },
            {
                "name": "generate_revenue_report",
                "description": "Generate comprehensive revenue analytics",
                "category": "analytics",
                "parameters": {
                    "start_date": {"type": "string", "required": True},
                    "end_date": {"type": "string", "required": True},
                    "breakdown": {"type": "string", "required": False}
                },
                "permissions_required": ["analytics.read"]
            },
            {
                "name": "predict_user_churn",
                "description": "Predict user churn probability using ML",
                "category": "ml_insights",
                "parameters": {
                    "user_segments": {"type": "array", "required": False},
                    "prediction_window": {"type": "string", "required": False}
                },
                "permissions_required": ["analytics.read", "ml.read"]
            },
            {
                "name": "optimize_payment_routing",
                "description": "Optimize payment provider routing",
                "category": "optimization",
                "parameters": {
                    "transaction_volume": {"type": "number", "required": False},
                    "cost_priority": {"type": "number", "required": False}
                },
                "permissions_required": ["payments.write", "admin"]
            }
        ]
        
        return tools
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch MCP tools: {str(e)}"
        )

@router.post("/mcp/execute", response_model=MCPToolResponse)
async def execute_mcp_tool(
    tool_call: MCPToolCall,
    current_user: Dict[str, Any] = Depends(require_permission("write")),
    db: AsyncSession = Depends(get_db)
):
    """Execute an MCP tool."""
    try:
        start_time = datetime.utcnow()
        
        # Simulate tool execution based on tool name
        if tool_call.tool_name == "create_payment":
            result = {
                "payment_id": f"pay_{uuid4().hex[:8]}",
                "status": "pending",
                "amount": tool_call.arguments.get("amount", 100.0),
                "currency": tool_call.arguments.get("currency", "USD")
            }
        elif tool_call.tool_name == "analyze_fraud_patterns":
            result = {
                "patterns_detected": 3,
                "risk_score": 23.4,
                "suspicious_transactions": 12,
                "confidence": 94.2,
                "recommendations": ["Increase monitoring for new users", "Review geographic patterns"]
            }
        elif tool_call.tool_name == "generate_revenue_report":
            result = {
                "total_revenue": 284756.89,
                "growth_rate": 12.3,
                "top_performing_segments": ["Enterprise", "Premium"],
                "forecast": {
                    "next_month": 298234.56,
                    "confidence": 87.9
                }
            }
        elif tool_call.tool_name == "predict_user_churn":
            result = {
                "high_risk_users": 45,
                "churn_probability": 18.7,
                "retention_actions": ["Discount offer", "Feature education", "Personal outreach"],
                "model_accuracy": 91.3
            }
        else:
            result = {
                "message": f"Tool {tool_call.tool_name} executed successfully",
                "status": "completed"
            }
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return MCPToolResponse(
            tool_name=tool_call.tool_name,
            success=True,
            result=result,
            error=None,
            execution_time=execution_time,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        return MCPToolResponse(
            tool_name=tool_call.tool_name,
            success=False,
            result=None,
            error=str(e),
            execution_time=0.0,
            timestamp=datetime.utcnow()
        )

# AI Insights Dashboard
@router.post("/ai-insights/generate", response_model=AIInsightResponse)
async def generate_ai_insight(
    insight_request: AIInsightRequest,
    current_user: Dict[str, Any] = Depends(require_permission("read")),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI-powered business insights."""
    try:
        # Simulate AI insight generation
        insights = {
            "revenue_optimization": {
                "title": "Revenue Optimization Opportunities",
                "summary": "AI analysis identified 3 key opportunities to increase revenue by 18.5%",
                "detailed_analysis": """
                Based on transaction patterns and user behavior analysis, our AI models have identified several optimization opportunities:
                
                1. **Payment Method Optimization**: Switching to optimal payment providers could reduce processing costs by 12%
                2. **Pricing Strategy**: Dynamic pricing for premium features could increase ARPU by 15%
                3. **Customer Retention**: Proactive churn prevention could retain 85% of at-risk customers
                """,
                "recommendations": [
                    "Implement dynamic payment routing based on transaction characteristics",
                    "A/B test tiered pricing for enterprise customers",
                    "Deploy predictive churn model with automated retention campaigns",
                    "Optimize checkout flow to reduce abandonment by 8%"
                ],
                "confidence_score": 92.4,
                "visualization_data": {
                    "chart_type": "line",
                    "data": [
                        {"month": "Jan", "current": 245000, "optimized": 289000},
                        {"month": "Feb", "current": 267000, "optimized": 315000},
                        {"month": "Mar", "current": 289000, "optimized": 342000}
                    ]
                }
            },
            "fraud_prevention": {
                "title": "Fraud Detection Enhancement",
                "summary": "ML models can improve fraud detection accuracy to 99.2% while reducing false positives by 40%",
                "detailed_analysis": """
                Advanced machine learning analysis of transaction patterns reveals opportunities for enhanced fraud detection:
                
                1. **Behavioral Analytics**: User behavior patterns show distinct fraud signatures
                2. **Geographic Analysis**: Location-based risk scoring can improve accuracy
                3. **Temporal Patterns**: Time-based transaction analysis reveals fraud clusters
                """,
                "recommendations": [
                    "Deploy enhanced behavioral analytics model",
                    "Implement real-time geolocation risk scoring",
                    "Add device fingerprinting for improved accuracy",
                    "Create adaptive thresholds based on customer segments"
                ],
                "confidence_score": 96.7,
                "visualization_data": {
                    "chart_type": "radar",
                    "data": {
                        "accuracy": 99.2,
                        "false_positives": 2.1,
                        "processing_speed": 94.5,
                        "cost_efficiency": 87.3
                    }
                }
            }
        }
        
        insight = insights.get(insight_request.insight_type, insights["revenue_optimization"])
        
        return AIInsightResponse(
            insight_type=insight_request.insight_type,
            title=insight["title"],
            summary=insight["summary"],
            detailed_analysis=insight["detailed_analysis"],
            recommendations=insight["recommendations"],
            confidence_score=insight["confidence_score"],
            data_points=12847,
            generated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            visualization_data=insight.get("visualization_data")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI insight: {str(e)}"
        )

@router.get("/ai-insights", response_model=List[AIInsightResponse])
async def get_ai_insights(
    insight_type: Optional[str] = Query(None, description="Filter by insight type"),
    current_user: Dict[str, Any] = Depends(require_permission("read")),
    db: AsyncSession = Depends(get_db)
):
    """Get available AI insights."""
    try:
        # Simulate recent insights
        insights = [
            {
                "insight_type": "revenue_optimization",
                "title": "Q1 Revenue Growth Opportunities",
                "summary": "AI identified 3 strategies to increase Q1 revenue by 22%",
                "detailed_analysis": "Detailed revenue optimization analysis...",
                "recommendations": ["Optimize pricing", "Reduce churn", "Expand markets"],
                "confidence_score": 91.5,
                "data_points": 15632,
                "generated_at": datetime.utcnow() - timedelta(hours=2),
                "expires_at": datetime.utcnow() + timedelta(hours=22),
                "visualization_data": None
            },
            {
                "insight_type": "customer_behavior",
                "title": "Customer Engagement Patterns",
                "summary": "User behavior analysis reveals optimal engagement strategies",
                "detailed_analysis": "Customer behavior pattern analysis...",
                "recommendations": ["Personalize onboarding", "Implement gamification", "Improve mobile UX"],
                "confidence_score": 88.3,
                "data_points": 23945,
                "generated_at": datetime.utcnow() - timedelta(hours=6),
                "expires_at": datetime.utcnow() + timedelta(hours=18),
                "visualization_data": None
            }
        ]
        
        if insight_type:
            insights = [i for i in insights if i["insight_type"] == insight_type]
        
        return [AIInsightResponse(**insight) for insight in insights]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch AI insights: {str(e)}"
        )

# Custom Report Builder
@router.post("/reports", response_model=CustomReportResponse)
async def create_custom_report(
    report_data: CustomReportCreate,
    current_user: Dict[str, Any] = Depends(require_permission("write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a custom report."""
    try:
        report_id = f"report_{uuid4().hex[:8]}"
        
        report = {
            "id": report_id,
            "name": report_data.name,
            "description": report_data.description,
            "data_sources": report_data.data_sources,
            "filters": report_data.filters,
            "grouping": report_data.grouping,
            "metrics": report_data.metrics,
            "chart_type": report_data.chart_type,
            "schedule": report_data.schedule,
            "created_by": current_user["email"],
            "created_at": datetime.utcnow(),
            "last_generated": None,
            "status": "active"
        }
        
        return CustomReportResponse(**report)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create custom report: {str(e)}"
        )

@router.get("/reports", response_model=List[CustomReportResponse])
async def get_custom_reports(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get custom reports."""
    try:
        # Simulate custom reports
        reports = [
            {
                "id": f"report_{i}",
                "name": f"Revenue Report {i}",
                "description": f"Custom revenue analysis report {i}",
                "data_sources": ["payments", "subscriptions"],
                "filters": {"date_range": "last_30_days"},
                "grouping": ["payment_method", "currency"],
                "metrics": ["total_revenue", "transaction_count", "avg_transaction_value"],
                "chart_type": ["bar", "line", "pie"][i % 3],
                "schedule": {"frequency": "weekly", "day": "monday"} if i % 2 == 0 else None,
                "created_by": current_user["email"],
                "created_at": datetime.utcnow() - timedelta(days=i * 5),
                "last_generated": datetime.utcnow() - timedelta(days=i) if i <= 3 else None,
                "status": "active"
            }
            for i in range(1, 6)
        ]
        
        return [CustomReportResponse(**report) for report in reports]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch custom reports: {str(e)}"
        )

@router.post("/reports/{report_id}/generate")
async def generate_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a custom report."""
    try:
        # Simulate report generation
        result = {
            "report_id": report_id,
            "generation_started": datetime.utcnow(),
            "estimated_completion": datetime.utcnow() + timedelta(minutes=5),
            "status": "generating",
            "message": "Report generation started successfully"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

# Chat Support
@router.post("/chat/message", response_model=ChatSupportResponse)
async def send_chat_message(
    message_data: ChatSupportMessage,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a chat support message."""
    try:
        start_time = datetime.utcnow()
        session_id = message_data.session_id or f"chat_{uuid4().hex[:8]}"
        
        # Use real MCP AI tools for intelligent responses
        message_lower = message_data.message.lower()
        response = ""
        response_type = "general"
        suggested_actions = []
        confidence = 0.75
        
        try:
            # Import MCP server for real AI processing
            from ..main import mcp_server
            
            if mcp_server.initialized:
                # Route to appropriate MCP tools based on message content
                if "payment" in message_lower or "transaction" in message_lower:
                    if "failed" in message_lower or "error" in message_lower:
                        # Analyze recent payment issues
                        payment_result = await mcp_server.tool_handlers["get_payment_metrics"](
                            "get_payment_metrics", {"days": 7}
                        )
                        response = "I've analyzed your recent payment activity. "
                        if payment_result and hasattr(payment_result, 'content'):
                            mcp_text = payment_result.content[0].text if payment_result.content else ""
                            response += mcp_text
                        response += " Let me help you troubleshoot this payment issue."
                        response_type = "troubleshooting"
                        suggested_actions = [
                            {"action": "check_payment_logs", "label": "Check Payment Logs"},
                            {"action": "retry_payment", "label": "Retry Payment"},
                            {"action": "contact_provider", "label": "Contact Payment Provider"}
                        ]
                        confidence = 0.92
                    elif "create" in message_lower or "new" in message_lower:
                        # Help with creating optimized payments
                        response = "I can help you create an AI-optimized payment. Our system uses machine learning to route payments for maximum success rate and minimum cost."
                        response_type = "assistance"
                        suggested_actions = [
                            {"action": "create_optimized_payment", "label": "Create Optimized Payment"},
                            {"action": "view_routing_options", "label": "View Routing Options"},
                            {"action": "check_fraud_rules", "label": "Check Fraud Rules"}
                        ]
                        confidence = 0.88
                
                elif "fraud" in message_lower or "security" in message_lower:
                    # Use AI fraud detection
                    fraud_result = await mcp_server.tool_handlers["detect_fraud_patterns"](
                        "detect_fraud_patterns", {
                            "hours_back": 24,
                            "risk_threshold": 70.0
                        }
                    )
                    response = "I've performed an AI-powered fraud analysis. "
                    if fraud_result and hasattr(fraud_result, 'content'):
                        mcp_text = fraud_result.content[0].text if fraud_result.content else ""
                        response += mcp_text
                    response_type = "security"
                    suggested_actions = [
                        {"action": "view_fraud_alerts", "label": "View Fraud Alerts"},
                        {"action": "update_security_rules", "label": "Update Security Rules"},
                        {"action": "review_suspicious_activity", "label": "Review Suspicious Activity"}
                    ]
                    confidence = 0.95
                
                elif "wallet" in message_lower or "balance" in message_lower:
                    # Check wallet status
                    response = "Let me check your wallet information and provide insights on balance management and transaction optimization."
                    response_type = "information"
                    suggested_actions = [
                        {"action": "check_wallet_balance", "label": "Check Wallet Balance"},
                        {"action": "view_transaction_history", "label": "View Transaction History"},
                        {"action": "transfer_funds", "label": "Transfer Funds"}
                    ]
                    confidence = 0.90
                
                elif "analytics" in message_lower or "dashboard" in message_lower or "metrics" in message_lower:
                    # Provide dashboard insights
                    dashboard_result = await mcp_server.tool_handlers["get_dashboard_metrics"](
                        "get_dashboard_metrics", {"time_range": "24h", "refresh_cache": True}
                    )
                    response = "I've generated real-time analytics insights. "
                    if dashboard_result and hasattr(dashboard_result, 'content'):
                        mcp_text = dashboard_result.content[0].text if dashboard_result.content else ""
                        response += mcp_text
                    response_type = "analytics"
                    suggested_actions = [
                        {"action": "view_revenue_analytics", "label": "View Revenue Analytics"},
                        {"action": "analyze_user_behavior", "label": "Analyze User Behavior"},
                        {"action": "generate_custom_report", "label": "Generate Custom Report"}
                    ]
                    confidence = 0.93
                
                elif "routing" in message_lower or "optimize" in message_lower:
                    # Payment routing optimization
                    routing_result = await mcp_server.tool_handlers["optimize_payment_routing"](
                        "optimize_payment_routing", {
                            "amount": 100.0,
                            "currency": "USD",
                            "optimize_for": "success_rate"
                        }
                    )
                    response = "I've analyzed optimal payment routing strategies. "
                    if routing_result and hasattr(routing_result, 'content'):
                        mcp_text = routing_result.content[0].text if routing_result.content else ""
                        response += mcp_text
                    response_type = "optimization"
                    suggested_actions = [
                        {"action": "apply_optimal_routing", "label": "Apply Optimal Routing"},
                        {"action": "view_routing_analytics", "label": "View Routing Analytics"},
                        {"action": "test_routing_scenarios", "label": "Test Routing Scenarios"}
                    ]
                    confidence = 0.89
                
                else:
                    # General AI assistance
                    response = "I'm your AI Payment Assistant powered by advanced MCP tools. I can help you with payment processing, fraud detection, wallet management, analytics, and business optimization. What specific aspect would you like to explore?"
                    suggested_actions = [
                        {"action": "view_ai_capabilities", "label": "View AI Capabilities"},
                        {"action": "get_system_status", "label": "Get System Status"},
                        {"action": "schedule_consultation", "label": "Schedule Consultation"}
                    ]
            
            else:
                # Fallback if MCP server not available
                response = "I'm currently initializing my AI capabilities. Please try again in a moment, or let me know how I can assist you with basic payment operations."
                
        except Exception as e:
            print(f"MCP chat processing error: {e}")
            # Fallback response
            response = "I'm experiencing a temporary issue accessing my AI tools. I can still help you with basic inquiries. What do you need assistance with?"
            suggested_actions = [
                {"action": "contact_support", "label": "Contact Human Support"},
                {"action": "view_documentation", "label": "View Documentation"}
            ]
        
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ChatSupportResponse(
            session_id=session_id,
            message=message_data.message,
            response=response,
            response_type=response_type,
            confidence=confidence,
            suggested_actions=suggested_actions,
            timestamp=datetime.utcnow(),
            response_time=response_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )

@router.get("/chat/sessions")
async def get_chat_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chat support sessions."""
    try:
        # Simulate chat sessions
        sessions = [
            {
                "session_id": f"chat_{i:08d}",
                "started_at": datetime.utcnow() - timedelta(hours=i),
                "last_message": datetime.utcnow() - timedelta(minutes=i * 15),
                "message_count": 5 + i,
                "status": "active" if i <= 2 else "closed",
                "topic": ["Payment Issues", "Subscription Help", "Fraud Alert", "General Inquiry"][i % 4],
                "satisfaction_rating": 4.5 - (i * 0.2) if i > 2 else None
            }
            for i in range(1, 8)
        ]
        
        return sessions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch chat sessions: {str(e)}"
        )

# Documentation Center
@router.post("/documentation/search", response_model=List[DocumentationResponse])
async def search_documentation(
    search_request: DocumentationSearch,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search documentation."""
    try:
        # Simulate documentation search results
        all_docs = [
            {
                "id": "doc_001",
                "title": "Payment Processing Guide",
                "content": "Complete guide to payment processing including setup, configuration, and troubleshooting...",
                "category": "payments",
                "tags": ["payments", "setup", "configuration"],
                "last_updated": datetime.utcnow() - timedelta(days=5),
                "relevance_score": 0.95,
                "author": "Technical Team"
            },
            {
                "id": "doc_002", 
                "title": "Fraud Detection Setup",
                "content": "How to configure and optimize fraud detection settings for maximum security...",
                "category": "security",
                "tags": ["fraud", "security", "configuration"],
                "last_updated": datetime.utcnow() - timedelta(days=8),
                "relevance_score": 0.88,
                "author": "Security Team"
            },
            {
                "id": "doc_003",
                "title": "API Integration Tutorial",
                "content": "Step-by-step guide to integrating with the MCP Payments API...",
                "category": "api",
                "tags": ["api", "integration", "tutorial"],
                "last_updated": datetime.utcnow() - timedelta(days=12),
                "relevance_score": 0.82,
                "author": "Developer Team"
            },
            {
                "id": "doc_004",
                "title": "Subscription Management",
                "content": "Managing subscriptions, billing cycles, and customer lifecycle...",
                "category": "subscriptions",
                "tags": ["subscriptions", "billing", "lifecycle"],
                "last_updated": datetime.utcnow() - timedelta(days=15),
                "relevance_score": 0.79,
                "author": "Product Team"
            },
            {
                "id": "doc_005",
                "title": "Analytics and Reporting",
                "content": "Understanding analytics dashboards and creating custom reports...",
                "category": "analytics",
                "tags": ["analytics", "reporting", "dashboards"],
                "last_updated": datetime.utcnow() - timedelta(days=20),
                "relevance_score": 0.76,
                "author": "Analytics Team"
            }
        ]
        
        # Filter by search query and category
        query_lower = search_request.query.lower()
        filtered_docs = []
        
        for doc in all_docs:
            # Simple relevance scoring based on query match
            relevance = 0.0
            if query_lower in doc["title"].lower():
                relevance += 0.5
            if query_lower in doc["content"].lower():
                relevance += 0.3
            if any(tag.lower() in query_lower for tag in doc["tags"]):
                relevance += 0.2
            
            # Filter by category if specified
            if search_request.category and doc["category"] != search_request.category:
                continue
                
            # Filter by tags if specified
            if search_request.tags and not any(tag in doc["tags"] for tag in search_request.tags):
                continue
            
            if relevance > 0.1:  # Minimum relevance threshold
                doc["relevance_score"] = min(relevance, 1.0)
                filtered_docs.append(doc)
        
        # Sort by relevance
        filtered_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return [DocumentationResponse(**doc) for doc in filtered_docs[:10]]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search documentation: {str(e)}"
        )

@router.get("/documentation/categories")
async def get_documentation_categories(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get documentation categories."""
    try:
        categories = [
            {
                "name": "payments",
                "display_name": "Payment Processing",
                "description": "Payment setup, processing, and troubleshooting",
                "document_count": 15,
                "icon": "payment"
            },
            {
                "name": "security", 
                "display_name": "Security & Fraud",
                "description": "Security configuration and fraud detection",
                "document_count": 8,
                "icon": "security"
            },
            {
                "name": "api",
                "display_name": "API Documentation",
                "description": "API integration guides and references",
                "document_count": 22,
                "icon": "code"
            },
            {
                "name": "subscriptions",
                "display_name": "Subscription Management",
                "description": "Subscription billing and lifecycle management",
                "document_count": 12,
                "icon": "subscription"
            },
            {
                "name": "analytics",
                "display_name": "Analytics & Reporting",
                "description": "Analytics dashboards and custom reporting",
                "document_count": 9,
                "icon": "analytics"
            }
        ]
        
        return categories
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch documentation categories: {str(e)}"
        ) 