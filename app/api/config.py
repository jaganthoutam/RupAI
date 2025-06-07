"""
Configuration API endpoints for frontend dynamic configuration.
Provides runtime configuration without hardcoded values.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.config.dynamic_settings import get_dynamic_config


router = APIRouter(prefix="/config", tags=["Configuration"])


class ConfigResponse(BaseModel):
    """Configuration response model."""
    server: Dict[str, Any]
    business_rules: Dict[str, Any]
    feature_flags: Dict[str, Any]
    ui_settings: Dict[str, Any]
    api_endpoints: Dict[str, str]


class FeatureFlagsResponse(BaseModel):
    """Feature flags response model."""
    analytics: bool
    fraud_detection: bool
    webhooks: bool
    audit_logging: bool
    real_time_monitoring: bool


@router.get("/", response_model=ConfigResponse)
async def get_configuration(
    current_user: dict = Depends(get_current_user)
):
    """Get complete configuration for frontend."""
    try:
        config = get_dynamic_config()
        
        return ConfigResponse(
            server={
                "name": config.mcp_server_name,
                "version": config.mcp_server_version,
                "mcp_version": config.mcp_version,
                "host": config.server_host,
                "port": config.server_port,
                "debug": config.debug_mode
            },
            business_rules={
                "min_payment_amount": float(config.business_rules.min_payment_amount),
                "max_payment_amount": float(config.business_rules.max_payment_amount),
                "supported_currencies": config.business_rules.supported_currencies,
                "payment_methods": config.business_rules.payment_methods,
                "fraud_threshold": config.business_rules.fraud_threshold,
                "rate_limit_per_hour": config.business_rules.rate_limit_per_hour
            },
            feature_flags={
                "analytics": config.feature_flags.enable_analytics,
                "fraud_detection": config.feature_flags.enable_fraud_detection,
                "webhooks": config.feature_flags.enable_webhooks,
                "audit_logging": config.feature_flags.enable_audit_logging,
                "real_time_monitoring": config.feature_flags.enable_real_time_monitoring
            },
            ui_settings={
                "theme": "light",
                "refresh_interval": 30000,  # 30 seconds
                "pagination_size": 50,
                "chart_animation": True,
                "notifications_enabled": True
            },
            api_endpoints={
                "base_url": f"http://{config.server_host}:{config.server_port}",
                "mcp_endpoint": "/mcp",
                "analytics_endpoint": "/analytics",
                "payments_endpoint": "/payments",
                "wallets_endpoint": "/wallets",
                "monitoring_endpoint": "/monitoring"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")


@router.get("/feature-flags", response_model=FeatureFlagsResponse)
async def get_feature_flags(
    current_user: dict = Depends(get_current_user)
):
    """Get feature flags for conditional UI rendering."""
    try:
        config = get_dynamic_config()
        
        return FeatureFlagsResponse(
            analytics=config.feature_flags.enable_analytics,
            fraud_detection=config.feature_flags.enable_fraud_detection,
            webhooks=config.feature_flags.enable_webhooks,
            audit_logging=config.feature_flags.enable_audit_logging,
            real_time_monitoring=config.feature_flags.enable_real_time_monitoring
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get feature flags: {str(e)}")


@router.get("/business-rules")
async def get_business_rules(
    current_user: dict = Depends(get_current_user)
):
    """Get business rules configuration."""
    try:
        config = get_dynamic_config()
        
        return {
            "payment_limits": {
                "min_amount": float(config.business_rules.min_payment_amount),
                "max_amount": float(config.business_rules.max_payment_amount)
            },
            "supported_currencies": config.business_rules.supported_currencies,
            "payment_methods": config.business_rules.payment_methods,
            "fraud_settings": {
                "threshold": config.business_rules.fraud_threshold,
                "enabled": config.feature_flags.enable_fraud_detection
            },
            "rate_limiting": {
                "requests_per_hour": config.business_rules.rate_limit_per_hour
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get business rules: {str(e)}")


@router.get("/data-sources")
async def get_data_sources(
    current_user: dict = Depends(get_current_user)
):
    """Get data source configuration for analytics."""
    try:
        config = get_dynamic_config()
        
        return {
            "revenue": {
                "base_amount": config.data_provider.base_revenue,
                "growth_rate": config.data_provider.revenue_growth_rate,
                "currencies": config.data_provider.currencies
            },
            "users": {
                "base_count": config.data_provider.base_user_count,
                "growth_rate": config.data_provider.user_growth_rate,
                "segments": config.data_provider.user_segments
            },
            "payments": {
                "base_count": config.data_provider.base_payment_count,
                "success_rate": config.data_provider.payment_success_rate,
                "methods": config.data_provider.payment_methods
            },
            "fraud": {
                "rate": config.data_provider.fraud_rate,
                "detection_enabled": config.feature_flags.enable_fraud_detection
            },
            "geographic": {
                "countries": config.data_provider.countries
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data sources: {str(e)}")


@router.get("/external-services")
async def get_external_services(
    current_user: dict = Depends(get_current_user)
):
    """Get external services configuration."""
    try:
        config = get_dynamic_config()
        
        return {
            "monitoring": {
                "url": config.external_services.monitoring_service_url,
                "enabled": config.feature_flags.enable_real_time_monitoring
            },
            "analytics": {
                "url": config.external_services.analytics_service_url,
                "enabled": config.feature_flags.enable_analytics
            },
            "notifications": {
                "url": config.external_services.notification_service_url,
                "enabled": True
            },
            "observability": {
                "endpoint": config.external_services.observability_endpoint,
                "enabled": True
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get external services: {str(e)}")


@router.post("/reload")
async def reload_configuration(
    current_user: dict = Depends(get_current_user)
):
    """Reload configuration from environment variables."""
    try:
        # Check if user has admin permissions
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        from app.config.dynamic_settings import reload_config
        new_config = reload_config()
        
        return {
            "message": "Configuration reloaded successfully",
            "timestamp": new_config.data_provider.base_revenue,  # Just to verify reload
            "server_info": {
                "name": new_config.mcp_server_name,
                "version": new_config.mcp_server_version
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload configuration: {str(e)}") 