"""
Settings & Configuration API Endpoints
System settings, user preferences, API keys, and notification management.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_db
from ..auth.dependencies import get_current_user, require_permission

router = APIRouter(prefix="/settings", tags=["Settings & Configuration"])

# Request/Response Models
class SystemSettingUpdate(BaseModel):
    value: Union[str, int, float, bool, List[str], Dict[str, Any]]
    description: Optional[str] = None

class SystemSettingResponse(BaseModel):
    key: str
    value: Union[str, int, float, bool, List[str], Dict[str, Any]]
    description: str
    category: str
    is_sensitive: bool
    updated_by: str
    updated_at: datetime

class UserPreferenceUpdate(BaseModel):
    value: Union[str, int, float, bool, List[str], Dict[str, Any]]

class UserPreferenceResponse(BaseModel):
    key: str
    value: Union[str, int, float, bool, List[str], Dict[str, Any]]
    description: str
    category: str
    updated_at: datetime

class APIKeyCreate(BaseModel):
    name: str = Field(..., description="API key name")
    service: str = Field(..., description="External service name")
    description: Optional[str] = Field(None, description="API key description")
    permissions: List[str] = Field(default=[], description="API key permissions")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")

class APIKeyResponse(BaseModel):
    id: str
    name: str
    service: str
    description: Optional[str]
    permissions: List[str]
    key_preview: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]

class NotificationSettingUpdate(BaseModel):
    enabled: bool = Field(..., description="Enable notification")
    channels: List[str] = Field(default=[], description="Notification channels")
    frequency: str = Field(default="immediate", description="Notification frequency")
    conditions: Optional[Dict[str, Any]] = Field(default={}, description="Trigger conditions")

class NotificationSettingResponse(BaseModel):
    type: str
    enabled: bool
    channels: List[str]
    frequency: str
    conditions: Dict[str, Any]
    description: str
    updated_at: datetime

# System Settings Management
@router.get("/system", response_model=List[SystemSettingResponse])
async def get_system_settings(
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: Dict[str, Any] = Depends(require_permission("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Get system settings."""
    try:
        # Simulate system settings
        settings = [
            {
                "key": "payment_processing.default_currency",
                "value": "USD",
                "description": "Default currency for payment processing",
                "category": "payment",
                "is_sensitive": False,
                "updated_by": "admin",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "payment_processing.transaction_timeout",
                "value": 30,
                "description": "Transaction timeout in seconds",
                "category": "payment",
                "is_sensitive": False,
                "updated_by": "admin",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "security.max_login_attempts",
                "value": 5,
                "description": "Maximum login attempts before account lockout",
                "category": "security",
                "is_sensitive": False,
                "updated_by": "admin",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "security.session_timeout",
                "value": 3600,
                "description": "Session timeout in seconds",
                "category": "security",
                "is_sensitive": False,
                "updated_by": "admin",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "notifications.webhook_url",
                "value": "https://api.company.com/webhooks",
                "description": "Default webhook URL for notifications",
                "category": "notifications",
                "is_sensitive": True,
                "updated_by": "admin",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "analytics.retention_days",
                "value": 365,
                "description": "Data retention period in days",
                "category": "analytics",
                "is_sensitive": False,
                "updated_by": "admin",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "fraud_detection.threshold",
                "value": 75.0,
                "description": "Fraud detection threshold percentage",
                "category": "fraud",
                "is_sensitive": False,
                "updated_by": "admin",
                "updated_at": datetime.utcnow()
            }
        ]
        
        if category:
            settings = [s for s in settings if s["category"] == category]
        
        return [SystemSettingResponse(**setting) for setting in settings]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch system settings: {str(e)}"
        )

@router.put("/system/{setting_key}")
async def update_system_setting(
    setting_key: str,
    setting_data: SystemSettingUpdate,
    current_user: Dict[str, Any] = Depends(require_permission("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Update a system setting."""
    try:
        # Simulate setting update
        result = {
            "key": setting_key,
            "old_value": "previous_value",
            "new_value": setting_data.value,
            "updated_by": current_user["email"],
            "updated_at": datetime.utcnow(),
            "message": f"Setting {setting_key} updated successfully"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update system setting: {str(e)}"
        )

# User Preferences Management
@router.get("/preferences", response_model=List[UserPreferenceResponse])
async def get_user_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user preferences."""
    try:
        # Simulate user preferences
        preferences = [
            {
                "key": "dashboard.theme",
                "value": "dark",
                "description": "Dashboard theme preference",
                "category": "appearance",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "dashboard.layout",
                "value": "grid",
                "description": "Dashboard layout preference",
                "category": "appearance",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "notifications.email_enabled",
                "value": True,
                "description": "Enable email notifications",
                "category": "notifications",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "analytics.default_timeframe",
                "value": "7d",
                "description": "Default analytics timeframe",
                "category": "analytics",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "language.locale",
                "value": "en-US",
                "description": "User interface language",
                "category": "localization",
                "updated_at": datetime.utcnow()
            },
            {
                "key": "timezone",
                "value": "America/New_York",
                "description": "User timezone",
                "category": "localization",
                "updated_at": datetime.utcnow()
            }
        ]
        
        return [UserPreferenceResponse(**pref) for pref in preferences]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user preferences: {str(e)}"
        )

@router.put("/preferences/{preference_key}")
async def update_user_preference(
    preference_key: str,
    preference_data: UserPreferenceUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a user preference."""
    try:
        # Simulate preference update
        result = {
            "key": preference_key,
            "old_value": "previous_value",
            "new_value": preference_data.value,
            "user_id": current_user["id"],
            "updated_at": datetime.utcnow(),
            "message": f"Preference {preference_key} updated successfully"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user preference: {str(e)}"
        )

# API Key Management
@router.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    service: Optional[str] = Query(None, description="Filter by service"),
    current_user: Dict[str, Any] = Depends(require_permission("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Get API keys."""
    try:
        # Simulate API keys
        api_keys = [
            {
                "id": f"key_{i}",
                "name": ["Stripe Production", "Razorpay Test", "SendGrid", "Slack Webhook", "Firebase"][i-1],
                "service": ["stripe", "razorpay", "sendgrid", "slack", "firebase"][i-1],
                "description": f"API key for {['payment processing', 'payment gateway', 'email service', 'notifications', 'analytics'][i-1]}",
                "permissions": [["payments.read", "payments.write"], ["payments.read"], ["notifications.send"], ["notifications.send"], ["analytics.read"]][i-1],
                "key_preview": f"sk_...{uuid4().hex[-8:]}",
                "is_active": i != 3,  # Make SendGrid inactive
                "created_at": datetime.utcnow() - timedelta(days=i*10),
                "expires_at": datetime.utcnow() + timedelta(days=365) if i <= 3 else None,
                "last_used": datetime.utcnow() - timedelta(hours=i*2)
            }
            for i in range(1, 6)
        ]
        
        if service:
            api_keys = [key for key in api_keys if key["service"] == service]
        
        return [APIKeyResponse(**key) for key in api_keys]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch API keys: {str(e)}"
        )

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: Dict[str, Any] = Depends(require_permission("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key."""
    try:
        # Simulate API key creation
        key_id = f"key_{uuid4().hex[:8]}"
        api_key = f"sk_{uuid4().hex}"
        
        result = {
            "id": key_id,
            "name": key_data.name,
            "service": key_data.service,
            "description": key_data.description,
            "permissions": key_data.permissions,
            "key_preview": f"sk_...{api_key[-8:]}",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "expires_at": key_data.expires_at,
            "last_used": None
        }
        
        return APIKeyResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create API key: {str(e)}"
        )

@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: Dict[str, Any] = Depends(require_permission("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key."""
    try:
        # Simulate API key deletion
        result = {
            "key_id": key_id,
            "deleted_at": datetime.utcnow(),
            "deleted_by": current_user["email"],
            "message": "API key deleted successfully"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete API key: {str(e)}"
        )

# Notification Settings Management
@router.get("/notifications", response_model=List[NotificationSettingResponse])
async def get_notification_settings(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get notification settings."""
    try:
        # Simulate notification settings
        settings = [
            {
                "type": "payment_success",
                "enabled": True,
                "channels": ["email", "webhook"],
                "frequency": "immediate",
                "conditions": {"amount_threshold": 1000.0},
                "description": "Notifications for successful payments",
                "updated_at": datetime.utcnow()
            },
            {
                "type": "payment_failed",
                "enabled": True,
                "channels": ["email", "slack", "webhook"],
                "frequency": "immediate",
                "conditions": {},
                "description": "Notifications for failed payments",
                "updated_at": datetime.utcnow()
            },
            {
                "type": "fraud_detected",
                "enabled": True,
                "channels": ["email", "slack", "sms"],
                "frequency": "immediate",
                "conditions": {"risk_score_threshold": 75.0},
                "description": "Notifications for fraud detection",
                "updated_at": datetime.utcnow()
            },
            {
                "type": "system_health",
                "enabled": True,
                "channels": ["slack", "webhook"],
                "frequency": "hourly",
                "conditions": {"health_score_threshold": 95.0},
                "description": "System health monitoring alerts",
                "updated_at": datetime.utcnow()
            },
            {
                "type": "subscription_renewal",
                "enabled": True,
                "channels": ["email"],
                "frequency": "daily",
                "conditions": {"days_before_renewal": 7},
                "description": "Subscription renewal reminders",
                "updated_at": datetime.utcnow()
            },
            {
                "type": "chargeback_received",
                "enabled": True,
                "channels": ["email", "slack"],
                "frequency": "immediate",
                "conditions": {},
                "description": "Chargeback notifications",
                "updated_at": datetime.utcnow()
            }
        ]
        
        return [NotificationSettingResponse(**setting) for setting in settings]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notification settings: {str(e)}"
        )

@router.put("/notifications/{notification_type}")
async def update_notification_setting(
    notification_type: str,
    setting_data: NotificationSettingUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update notification setting."""
    try:
        # Simulate notification setting update
        result = {
            "type": notification_type,
            "enabled": setting_data.enabled,
            "channels": setting_data.channels,
            "frequency": setting_data.frequency,
            "conditions": setting_data.conditions,
            "updated_by": current_user["email"],
            "updated_at": datetime.utcnow(),
            "message": f"Notification setting for {notification_type} updated successfully"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification setting: {str(e)}"
        )

@router.post("/notifications/test/{notification_type}")
async def test_notification(
    notification_type: str,
    channels: List[str] = Query(..., description="Channels to test"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Test notification delivery."""
    try:
        # Simulate notification test
        test_results = []
        for channel in channels:
            test_results.append({
                "channel": channel,
                "status": "success" if channel != "sms" else "failed",  # Simulate SMS failure
                "message": f"Test notification sent successfully via {channel}" if channel != "sms" else "SMS delivery failed: Invalid phone number",
                "delivery_time": 1.2 if channel == "email" else 0.5,
                "timestamp": datetime.utcnow()
            })
        
        result = {
            "notification_type": notification_type,
            "test_results": test_results,
            "overall_status": "partial_success" if any(r["status"] == "failed" for r in test_results) else "success",
            "tested_at": datetime.utcnow(),
            "tested_by": current_user["email"]
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test notification: {str(e)}"
        )

# Configuration Export/Import
@router.get("/export")
async def export_configuration(
    include_sensitive: bool = Query(False, description="Include sensitive settings"),
    current_user: Dict[str, Any] = Depends(require_permission("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Export system configuration."""
    try:
        # Simulate configuration export
        config = {
            "exported_at": datetime.utcnow(),
            "exported_by": current_user["email"],
            "version": "1.0",
            "system_settings": {
                "payment_processing": {
                    "default_currency": "USD",
                    "transaction_timeout": 30
                },
                "security": {
                    "max_login_attempts": 5,
                    "session_timeout": 3600
                }
            },
            "notification_settings": {
                "payment_success": {"enabled": True, "channels": ["email"]},
                "fraud_detected": {"enabled": True, "channels": ["email", "slack"]}
            }
        }
        
        if include_sensitive:
            config["api_keys"] = {
                "stripe": "sk_...REDACTED",
                "sendgrid": "SG....REDACTED"
            }
        
        return config
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export configuration: {str(e)}"
        )

@router.post("/import")
async def import_configuration(
    config_data: Dict[str, Any],
    dry_run: bool = Query(False, description="Perform dry run without applying changes"),
    current_user: Dict[str, Any] = Depends(require_permission("admin")),
    db: AsyncSession = Depends(get_db)
):
    """Import system configuration."""
    try:
        # Simulate configuration import
        changes = []
        
        # Analyze changes
        if "system_settings" in config_data:
            for category, settings in config_data["system_settings"].items():
                for key, value in settings.items():
                    changes.append({
                        "type": "system_setting",
                        "key": f"{category}.{key}",
                        "old_value": "current_value",
                        "new_value": value,
                        "action": "update"
                    })
        
        result = {
            "dry_run": dry_run,
            "changes_detected": len(changes),
            "changes": changes,
            "applied": not dry_run,
            "imported_at": datetime.utcnow() if not dry_run else None,
            "imported_by": current_user["email"],
            "message": f"Configuration {'would be' if dry_run else 'has been'} imported successfully"
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import configuration: {str(e)}"
        ) 