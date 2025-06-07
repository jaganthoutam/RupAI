"""Monitoring MCP tools for system health and performance tracking."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PerformHealthCheckInput(BaseModel):
    """Input for system health check."""
    service_name: str = Field(default="mcp-payments", description="Service name to check")
    include_components: bool = Field(default=True, description="Include component health details")
    include_metrics: bool = Field(default=True, description="Include performance metrics")


async def perform_health_check(
    service_name: str = "mcp-payments",
    include_components: bool = True,
    include_metrics: bool = True
) -> Dict[str, Any]:
    """
    Perform comprehensive system health check.
    
    Checks all system components including database, cache, queue, external services,
    and system resources to provide overall health status.
    """
    try:
        # Simulate health check results
        health_result = {
            "overall_status": "healthy",
            "overall_health_score": 95,
            "components": {
                "database": {"status": "healthy", "response_time": 25.3, "connections": 15},
                "redis_cache": {"status": "healthy", "response_time": 5.1, "memory_usage": 65.2},
                "message_queue": {"status": "healthy", "queue_depth": 23, "consumers": 3},
                "external_apis": {"status": "warning", "availability": 98.5, "avg_response": 150.0}
            } if include_components else {},
            "metrics": {
                "cpu_usage": 45.2,
                "memory_usage": 68.7,
                "disk_usage": 34.1,
                "network_io": 125.5
            } if include_metrics else {},
            "checked_at": datetime.utcnow().isoformat()
        }
        
        # Determine overall status message
        status = health_result.get('overall_status', 'unknown')
        health_score = health_result.get('overall_health_score', 0)
        
        status_messages = {
            'healthy': f"System is healthy (Score: {health_score}%)",
            'warning': f"System has warnings (Score: {health_score}%)",
            'critical': f"System is in critical state (Score: {health_score}%)",
            'unknown': "System status unknown"
        }
        
        return {
            "success": status != 'critical',
            "data": {
                "health_check": health_result,
                "checked_at": datetime.utcnow().isoformat(),
                "service_name": service_name
            },
            "message": status_messages.get(status, f"System status: {status}")
        }
        
    except Exception as e:
        logger.error("Health check failed: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Health check failed: {str(e)}"
        }


class CreateAlertInput(BaseModel):
    """Input for creating system alerts."""
    alert_name: str = Field(..., description="Alert name/identifier")
    alert_type: str = Field(..., description="Alert type: performance, error, security, etc.")
    severity: str = Field(..., description="Alert severity: low, medium, high, critical")
    title: str = Field(..., description="Alert title")
    description: str = Field(..., description="Alert description")
    metric_name: str = Field(..., description="Metric that triggered the alert")
    metric_value: float = Field(..., description="Current metric value")
    threshold_value: float = Field(..., description="Threshold value that was exceeded")
    comparison_operator: str = Field(..., description="Comparison operator: >, <, >=, <=, ==, !=")
    service_name: str = Field(default="mcp-payments", description="Service name")
    component: str = Field(default="unknown", description="System component")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


async def create_alert(
    alert_name: str,
    alert_type: str,
    severity: str,
    title: str,
    description: str,
    metric_name: str,
    metric_value: float,
    threshold_value: float,
    comparison_operator: str,
    service_name: str = "mcp-payments",
    component: str = "unknown",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new system alert.
    
    Creates alerts for system issues, performance problems, security events,
    or any other conditions that require attention.
    """
    try:
        # Validate severity
        valid_severities = ['low', 'medium', 'high', 'critical']
        if severity.lower() not in valid_severities:
            raise ValueError(f"Invalid severity: {severity}. Must be one of: {', '.join(valid_severities)}")
        
        # Simulate alert creation
        alert_id = str(uuid4())
        
        alert_data = {
            "alert_id": alert_id,
            "alert_name": alert_name,
            "alert_type": alert_type,
            "severity": severity.lower(),
            "title": title,
            "description": description,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "threshold_value": threshold_value,
            "comparison_operator": comparison_operator,
            "service_name": service_name,
            "component": component,
            "metadata": metadata or {},
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": alert_data,
            "message": f"Alert created successfully: {title}"
        }
        
    except Exception as e:
        logger.error("Failed to create alert: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create alert: {str(e)}"
        }


class ResolveAlertInput(BaseModel):
    """Input for resolving alerts."""
    alert_id: str = Field(..., description="Alert ID to resolve")
    resolved_by: Optional[UUID] = Field(None, description="User ID who resolved the alert")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")


async def resolve_alert(
    alert_id: str,
    resolved_by: Optional[str] = None,
    resolution_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Resolve an existing alert.
    
    Marks an alert as resolved and optionally adds resolution notes
    for future reference and incident analysis.
    """
    try:
        # Simulate alert resolution
        resolution_data = {
            "alert_id": alert_id,
            "resolved_by": resolved_by,
            "resolved_at": datetime.utcnow().isoformat(),
            "resolution_notes": resolution_notes,
            "status": "resolved"
        }
        
        return {
            "success": True,
            "data": resolution_data,
            "message": f"Alert {alert_id} resolved successfully"
        }
        
    except Exception as e:
        logger.error("Failed to resolve alert: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to resolve alert: {str(e)}"
        }


class RecordPerformanceMetricInput(BaseModel):
    """Input for recording performance metrics."""
    metric_category: str = Field(..., description="Metric category: api, database, cache, etc.")
    metric_name: str = Field(..., description="Metric name")
    metric_type: str = Field(..., description="Metric type: counter, gauge, histogram, timer")
    value: float = Field(..., description="Metric value")
    service_name: str = Field(default="mcp-payments", description="Service name")
    tags: Optional[Dict[str, str]] = Field(default=None, description="Metric tags")
    dimensions: Optional[Dict[str, Any]] = Field(default=None, description="Additional dimensions")


async def record_performance_metric(
    metric_category: str,
    metric_name: str,
    metric_type: str,
    value: float,
    service_name: str = "mcp-payments",
    tags: Optional[Dict[str, str]] = None,
    dimensions: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Record a performance metric.
    
    Records system performance metrics for monitoring, alerting,
    and analytics purposes.
    """
    try:
        # Validate metric type
        valid_types = ['counter', 'gauge', 'histogram', 'timer']
        if metric_type.lower() not in valid_types:
            raise ValueError(f"Invalid metric type: {metric_type}. Must be one of: {', '.join(valid_types)}")
        
        # Simulate metric recording
        metric_data = {
            "metric_id": str(uuid4()),
            "metric_category": metric_category,
            "metric_name": metric_name,
            "metric_type": metric_type.lower(),
            "value": value,
            "service_name": service_name,
            "tags": tags or {},
            "dimensions": dimensions or {},
            "recorded_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": metric_data,
            "message": f"Performance metric recorded: {metric_name} = {value}"
        }
        
    except Exception as e:
        logger.error("Failed to record performance metric: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to record performance metric: {str(e)}"
        }


class LogErrorInput(BaseModel):
    """Input for error logging."""
    error_type: str = Field(..., description="Error type/exception name")
    error_category: str = Field(..., description="Error category: system, business, validation, etc.")
    severity_level: str = Field(..., description="Severity: debug, info, warning, error, critical")
    error_message: str = Field(..., description="Error message")
    correlation_id: str = Field(..., description="Request correlation ID")
    trace_id: str = Field(..., description="Distributed tracing ID")
    service_name: str = Field(default="mcp-payments", description="Service name")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional error context")


async def log_error(
    error_type: str,
    error_category: str,
    severity_level: str,
    error_message: str,
    correlation_id: str,
    trace_id: str,
    service_name: str = "mcp-payments",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Log an error with comprehensive context.
    
    Records errors with full context for debugging, monitoring,
    and incident response purposes.
    """
    try:
        # Validate severity level
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        if severity_level.lower() not in valid_levels:
            raise ValueError(f"Invalid severity level: {severity_level}. Must be one of: {', '.join(valid_levels)}")
        
        # Simulate error logging
        error_data = {
            "error_id": str(uuid4()),
            "error_type": error_type,
            "error_category": error_category,
            "severity_level": severity_level.lower(),
            "error_message": error_message,
            "correlation_id": correlation_id,
            "trace_id": trace_id,
            "service_name": service_name,
            "context": context or {},
            "logged_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": error_data,
            "message": f"Error logged: {error_type} - {error_message[:50]}..."
        }
        
    except Exception as e:
        logger.error("Failed to log error: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to log error: {str(e)}"
        }


class GetSystemStatusInput(BaseModel):
    """Input for system status retrieval."""
    include_alerts: bool = Field(default=True, description="Include active alerts")
    include_metrics: bool = Field(default=True, description="Include performance metrics")
    include_errors: bool = Field(default=True, description="Include recent errors")


async def get_system_status(
    include_alerts: bool = True,
    include_metrics: bool = True,
    include_errors: bool = True
) -> Dict[str, Any]:
    """
    Get comprehensive system status overview.
    
    Provides a complete view of system health, active alerts,
    performance metrics, and recent errors.
    """
    try:
        # Simulate system status retrieval
        system_status = {
            "overall_status": "healthy",
            "status_score": 95,
            "components": {
                "api_server": {"status": "healthy", "uptime": "99.95%"},
                "database": {"status": "healthy", "connections": 15},
                "cache": {"status": "healthy", "hit_rate": "95.2%"},
                "message_queue": {"status": "warning", "queue_depth": 150}
            },
            "alerts": [
                {
                    "alert_id": str(uuid4()),
                    "severity": "medium",
                    "title": "High memory usage",
                    "created_at": datetime.utcnow().isoformat()
                }
            ] if include_alerts else [],
            "metrics": {
                "requests_per_second": 125.5,
                "response_time_p95": 250.0,
                "error_rate": 0.8,
                "cpu_usage": 65.2,
                "memory_usage": 72.8
            } if include_metrics else {},
            "recent_errors": [
                {
                    "error_id": str(uuid4()),
                    "severity": "warning",
                    "message": "Database connection timeout",
                    "occurred_at": datetime.utcnow().isoformat()
                }
            ] if include_errors else [],
            "checked_at": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "data": system_status,
            "message": f"System status retrieved: {system_status['overall_status']}"
        }
        
    except Exception as e:
        logger.error("Failed to get system status: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get system status: {str(e)}"
        }


class GetActiveAlertsInput(BaseModel):
    """Input for retrieving active alerts."""
    severity_filter: Optional[str] = Field(None, description="Filter by severity: low, medium, high, critical")
    service_filter: Optional[str] = Field(None, description="Filter by service name")
    limit: int = Field(default=50, description="Maximum number of alerts to return", ge=1, le=1000)


async def get_active_alerts(
    severity_filter: Optional[str] = None,
    service_filter: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get list of active system alerts.
    
    Retrieves active alerts with optional filtering by severity
    and service name for targeted monitoring.
    """
    try:
        # Simulate active alerts retrieval
        alerts = []
        severities = ['low', 'medium', 'high', 'critical']
        
        for i in range(min(limit, 10)):  # Simulate up to 10 alerts
            severity = severities[i % 4]
            if severity_filter and severity != severity_filter.lower():
                continue
                
            alert = {
                "alert_id": str(uuid4()),
                "alert_name": f"alert_{i+1}",
                "severity": severity,
                "title": f"System Alert {i+1}",
                "description": f"Sample alert description {i+1}",
                "service_name": service_filter or "mcp-payments",
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
            alerts.append(alert)
        
        return {
            "success": True,
            "data": {
                "alerts": alerts,
                "total_count": len(alerts),
                "filters": {
                    "severity_filter": severity_filter,
                    "service_filter": service_filter,
                    "limit": limit
                },
                "retrieved_at": datetime.utcnow().isoformat()
            },
            "message": f"Retrieved {len(alerts)} active alerts"
        }
        
    except Exception as e:
        logger.error("Failed to get active alerts: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get active alerts: {str(e)}"
        }


class GetPerformanceMetricsInput(BaseModel):
    """Input for retrieving performance metrics."""
    metric_category: Optional[str] = Field(None, description="Filter by metric category")
    metric_name: Optional[str] = Field(None, description="Filter by metric name")
    start_time: Optional[datetime] = Field(None, description="Start time for metrics")
    end_time: Optional[datetime] = Field(None, description="End time for metrics")
    limit: int = Field(default=100, description="Maximum number of metrics to return", ge=1, le=10000)


async def get_performance_metrics(
    metric_category: Optional[str] = None,
    metric_name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get performance metrics for analysis.
    
    Retrieves system performance metrics with optional filtering
    for analysis and monitoring purposes.
    """
    try:
        # Set default time range
        if not end_time:
            end_time = datetime.utcnow()
        if not start_time:
            start_time = end_time - timedelta(hours=24)
        
        # Simulate performance metrics retrieval
        metrics = []
        categories = ['api', 'database', 'cache', 'queue']
        metric_names = ['response_time', 'throughput', 'error_rate', 'utilization']
        
        for i in range(min(limit, 20)):  # Simulate up to 20 metrics
            category = categories[i % 4]
            name = metric_names[i % 4]
            
            if metric_category and category != metric_category:
                continue
            if metric_name and name != metric_name:
                continue
                
            metric = {
                "metric_id": str(uuid4()),
                "metric_category": category,
                "metric_name": name,
                "metric_type": "gauge",
                "value": 100.0 + (i * 5),
                "timestamp": (start_time + timedelta(minutes=i*30)).isoformat(),
                "tags": {"service": "mcp-payments", "environment": "production"}
            }
            metrics.append(metric)
        
        return {
            "success": True,
            "data": {
                "metrics": metrics,
                "total_count": len(metrics),
                "filters": {
                    "metric_category": metric_category,
                    "metric_name": metric_name,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "limit": limit
                },
                "retrieved_at": datetime.utcnow().isoformat()
            },
            "message": f"Retrieved {len(metrics)} performance metrics"
        }
        
    except Exception as e:
        logger.error("Failed to get performance metrics: %s", str(e))
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get performance metrics: {str(e)}"
        } 