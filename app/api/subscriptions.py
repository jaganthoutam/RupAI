"""
Subscription Management API Endpoints
Comprehensive subscription handling with plans, billing, and analytics.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4, UUID
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..auth.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/subscriptions", tags=["Subscription Management"])

# Request/Response Models
class SubscriptionPlanCreate(BaseModel):
    name: str = Field(..., description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    price: Decimal = Field(..., ge=0, description="Plan price")
    currency: str = Field(default="USD", description="Currency code")
    billing_interval: str = Field(..., description="Billing interval: monthly, yearly, weekly")
    trial_days: int = Field(default=0, ge=0, description="Trial period in days")
    features: List[str] = Field(default=[], description="Plan features")
    is_active: bool = Field(default=True, description="Is plan active")
    max_users: Optional[int] = Field(None, ge=1, description="Maximum users allowed")
    max_transactions: Optional[int] = Field(None, ge=1, description="Maximum transactions per month")

class SubscriptionPlanResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: Decimal
    currency: str
    billing_interval: str
    trial_days: int
    features: List[str]
    is_active: bool
    max_users: Optional[int]
    max_transactions: Optional[int]
    created_at: datetime
    updated_at: datetime
    subscriber_count: int

class SubscriptionCreate(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    plan_id: str = Field(..., description="Subscription plan ID")
    payment_method_id: Optional[str] = Field(None, description="Payment method ID")
    trial_end: Optional[datetime] = Field(None, description="Trial end date")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

class SubscriptionResponse(BaseModel):
    id: str
    customer_id: str
    plan_id: str
    plan_name: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    cancel_at_period_end: bool
    canceled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    next_billing_amount: Decimal
    next_billing_date: datetime

class BillingInvoiceResponse(BaseModel):
    id: str
    subscription_id: str
    customer_id: str
    amount: Decimal
    currency: str
    status: str
    billing_period_start: datetime
    billing_period_end: datetime
    due_date: datetime
    paid_at: Optional[datetime]
    payment_method: Optional[str]
    created_at: datetime

class SubscriptionAnalytics(BaseModel):
    total_subscriptions: int
    active_subscriptions: int
    trial_subscriptions: int
    canceled_subscriptions: int
    monthly_recurring_revenue: Decimal
    annual_recurring_revenue: Decimal
    average_revenue_per_user: Decimal
    churn_rate: float
    growth_rate: float
    trial_conversion_rate: float
    plan_distribution: List[Dict[str, Any]]
    revenue_by_period: List[Dict[str, Any]]

# Subscription Plan Management
@router.post("/plans", response_model=SubscriptionPlanResponse)
async def create_subscription_plan(
    plan_data: SubscriptionPlanCreate,
    current_user: Dict[str, Any] = Depends(require_permission("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription plan."""
    try:
        # Simulate plan creation
        plan_id = f"plan_{uuid4().hex[:8]}"
        
        # In real implementation, save to database
        plan = {
            "id": plan_id,
            "name": plan_data.name,
            "description": plan_data.description,
            "price": plan_data.price,
            "currency": plan_data.currency,
            "billing_interval": plan_data.billing_interval,
            "trial_days": plan_data.trial_days,
            "features": plan_data.features,
            "is_active": plan_data.is_active,
            "max_users": plan_data.max_users,
            "max_transactions": plan_data.max_transactions,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "subscriber_count": 0
        }
        
        return SubscriptionPlanResponse(**plan)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription plan: {str(e)}"
        )

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(
    active_only: bool = Query(False, description="Filter active plans only"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all subscription plans."""
    try:
        # Simulate fetching plans
        plans = [
            {
                "id": f"plan_{i}",
                "name": f"{'Basic' if i == 1 else 'Premium' if i == 2 else 'Enterprise'}",
                "description": f"{'Starter plan' if i == 1 else 'Advanced features' if i == 2 else 'Full enterprise suite'}",
                "price": Decimal(f"{9.99 if i == 1 else 29.99 if i == 2 else 99.99}"),
                "currency": "USD",
                "billing_interval": "monthly",
                "trial_days": 14 if i <= 2 else 30,
                "features": [
                    f"Up to {100 * i} transactions/month",
                    f"{'Basic' if i == 1 else 'Advanced' if i == 2 else 'Enterprise'} analytics",
                    f"{'Email' if i == 1 else 'Email + Chat' if i == 2 else '24/7 Priority'} support"
                ],
                "is_active": True,
                "max_users": 5 * i if i <= 2 else None,
                "max_transactions": 1000 * i if i <= 2 else None,
                "created_at": datetime.utcnow() - timedelta(days=30),
                "updated_at": datetime.utcnow(),
                "subscriber_count": 150 - (i * 20)
            }
            for i in range(1, 4)
        ]
        
        if active_only:
            plans = [p for p in plans if p["is_active"]]
        
        return [SubscriptionPlanResponse(**plan) for plan in plans]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscription plans: {str(e)}"
        )

@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(
    plan_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get subscription plan by ID."""
    try:
        # Simulate fetching plan
        plan = {
            "id": plan_id,
            "name": "Premium Plan",
            "description": "Advanced features for growing businesses",
            "price": Decimal("29.99"),
            "currency": "USD",
            "billing_interval": "monthly",
            "trial_days": 14,
            "features": [
                "Up to 5,000 transactions/month",
                "Advanced analytics",
                "Email + Chat support",
                "API access",
                "Custom integrations"
            ],
            "is_active": True,
            "max_users": 10,
            "max_transactions": 5000,
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow(),
            "subscriber_count": 89
        }
        
        return SubscriptionPlanResponse(**plan)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription plan not found: {plan_id}"
        )

# Subscription Management
@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: Dict[str, Any] = Depends(require_permission("write")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription."""
    try:
        subscription_id = f"sub_{uuid4().hex[:8]}"
        current_time = datetime.utcnow()
        
        # Calculate billing period
        period_start = current_time
        period_end = period_start + timedelta(days=30)  # Assuming monthly
        
        subscription = {
            "id": subscription_id,
            "customer_id": subscription_data.customer_id,
            "plan_id": subscription_data.plan_id,
            "plan_name": "Premium Plan",
            "status": "trialing" if subscription_data.trial_end else "active",
            "current_period_start": period_start,
            "current_period_end": period_end,
            "trial_start": current_time if subscription_data.trial_end else None,
            "trial_end": subscription_data.trial_end,
            "cancel_at_period_end": False,
            "canceled_at": None,
            "created_at": current_time,
            "updated_at": current_time,
            "metadata": subscription_data.metadata,
            "next_billing_amount": Decimal("29.99"),
            "next_billing_date": subscription_data.trial_end or period_end
        }
        
        return SubscriptionResponse(**subscription)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.get("/", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get subscriptions with filtering and pagination."""
    try:
        # Simulate fetching subscriptions
        subscriptions = []
        for i in range(1, min(limit + 1, 26)):
            current_time = datetime.utcnow()
            subscriptions.append({
                "id": f"sub_{i:08d}",
                "customer_id": customer_id or f"cust_{i:06d}",
                "plan_id": f"plan_{(i % 3) + 1}",
                "plan_name": ["Basic", "Premium", "Enterprise"][i % 3],
                "status": ["active", "trialing", "canceled"][i % 3],
                "current_period_start": current_time - timedelta(days=i),
                "current_period_end": current_time + timedelta(days=30 - i),
                "trial_start": current_time - timedelta(days=i) if i % 4 == 0 else None,
                "trial_end": current_time + timedelta(days=14 - i) if i % 4 == 0 else None,
                "cancel_at_period_end": i % 5 == 0,
                "canceled_at": current_time - timedelta(days=i//2) if i % 7 == 0 else None,
                "created_at": current_time - timedelta(days=i + 10),
                "updated_at": current_time - timedelta(days=i//2),
                "metadata": {"source": "web", "campaign": f"campaign_{i}"},
                "next_billing_amount": Decimal(f"{[9.99, 29.99, 99.99][i % 3]}"),
                "next_billing_date": current_time + timedelta(days=30 - i)
            })
        
        return [SubscriptionResponse(**sub) for sub in subscriptions]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscriptions: {str(e)}"
        )

@router.get("/{subscription_id}/invoices", response_model=List[BillingInvoiceResponse])
async def get_subscription_invoices(
    subscription_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get billing invoices for a subscription."""
    try:
        # Simulate fetching invoices
        invoices = []
        for i in range(1, 6):
            current_time = datetime.utcnow()
            invoices.append({
                "id": f"inv_{subscription_id}_{i:03d}",
                "subscription_id": subscription_id,
                "customer_id": f"cust_{i:06d}",
                "amount": Decimal("29.99"),
                "currency": "USD",
                "status": ["paid", "pending", "failed"][i % 3],
                "billing_period_start": current_time - timedelta(days=30 * i),
                "billing_period_end": current_time - timedelta(days=30 * (i - 1)),
                "due_date": current_time - timedelta(days=30 * (i - 1) - 3),
                "paid_at": current_time - timedelta(days=30 * (i - 1) - 1) if i % 3 == 1 else None,
                "payment_method": "card" if i % 2 == 0 else "bank_transfer",
                "created_at": current_time - timedelta(days=30 * i + 5)
            })
        
        return [BillingInvoiceResponse(**invoice) for invoice in invoices]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invoices: {str(e)}"
        )

@router.get("/analytics", response_model=SubscriptionAnalytics)
async def get_subscription_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_user: Dict[str, Any] = Depends(require_permission("read")),
    db: AsyncSession = Depends(get_db)
):
    """Get subscription analytics and metrics."""
    try:
        # Simulate analytics calculation
        analytics = {
            "total_subscriptions": 2547,
            "active_subscriptions": 2156,
            "trial_subscriptions": 234,
            "canceled_subscriptions": 157,
            "monthly_recurring_revenue": Decimal("76891.45"),
            "annual_recurring_revenue": Decimal("922697.40"),
            "average_revenue_per_user": Decimal("35.67"),
            "churn_rate": 2.8,
            "growth_rate": 15.6,
            "trial_conversion_rate": 68.4,
            "plan_distribution": [
                {"plan": "Basic", "count": 1234, "percentage": 48.5},
                {"plan": "Premium", "count": 892, "percentage": 35.0},
                {"plan": "Enterprise", "count": 421, "percentage": 16.5}
            ],
            "revenue_by_period": [
                {"period": "2024-01", "revenue": Decimal("68234.50"), "growth": 12.3},
                {"period": "2024-02", "revenue": Decimal("72456.80"), "growth": 6.2},
                {"period": "2024-03", "revenue": Decimal("76891.45"), "growth": 6.1}
            ]
        }
        
        return SubscriptionAnalytics(**analytics)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch subscription analytics: {str(e)}"
        )

@router.put("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    at_period_end: bool = Query(True, description="Cancel at period end"),
    current_user: Dict[str, Any] = Depends(require_permission("write")),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a subscription."""
    try:
        # Simulate subscription cancellation
        result = {
            "subscription_id": subscription_id,
            "status": "canceled" if not at_period_end else "active",
            "cancel_at_period_end": at_period_end,
            "canceled_at": datetime.utcnow() if not at_period_end else None,
            "effective_date": datetime.utcnow() + timedelta(days=30) if at_period_end else datetime.utcnow(),
            "message": f"Subscription {'will be canceled at period end' if at_period_end else 'canceled immediately'}"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

@router.put("/{subscription_id}/reactivate")
async def reactivate_subscription(
    subscription_id: str,
    current_user: Dict[str, Any] = Depends(require_permission("write")),
    db: AsyncSession = Depends(get_db)
):
    """Reactivate a canceled subscription."""
    try:
        # Simulate subscription reactivation
        result = {
            "subscription_id": subscription_id,
            "status": "active",
            "cancel_at_period_end": False,
            "canceled_at": None,
            "reactivated_at": datetime.utcnow(),
            "message": "Subscription reactivated successfully"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reactivate subscription: {str(e)}"
        ) 