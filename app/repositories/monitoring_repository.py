"""Monitoring repository for handling monitoring and alerting data operations."""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, or_

from ..models.orm_models import UserORM
from ..models.monitoring import (
    HealthCheck, SystemAlert, PerformanceMetric, ErrorLog,
    HealthStatus, AlertSeverity, AlertStatus
)


class MonitoringRepository:
    """Repository for monitoring data operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def get_active_alert(
        self,
        alert_name: str,
        service_name: str,
        component: str
    ) -> Optional[Dict[str, Any]]:
        """Get active alert for the same component."""
        
        # For now, return None - no active alerts
        # In real implementation, this would query the alerts table
        return None
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> str:
        """Create a new alert record."""
        
        try:
            # In real implementation, this would insert into alerts table
            # For now, just log the alert
            print(f"Creating alert: {alert_data['alert_id']} - {alert_data['title']}")
            return alert_data['alert_id']
            
        except Exception as e:
            print(f"Failed to create alert: {e}")
            raise
    
    async def update_alert_occurrence(
        self,
        alert_id: str,
        metric_value: float
    ) -> bool:
        """Update alert occurrence with new metric value."""
        
        try:
            # In real implementation, this would update the alert record
            print(f"Updating alert {alert_id} with metric value: {metric_value}")
            return True
            
        except Exception as e:
            print(f"Failed to update alert: {e}")
            return False
    
    async def resolve_alert(
        self,
        alert_id: str,
        resolved_by: Optional[UUID] = None,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Mark alert as resolved."""
        
        try:
            # In real implementation, this would update the alert status
            print(f"Resolving alert {alert_id} by {resolved_by}: {resolution_notes}")
            return True
            
        except Exception as e:
            print(f"Failed to resolve alert: {e}")
            return False
    
    async def store_health_check(self, health_data: Dict[str, Any]) -> str:
        """Store health check result."""
        
        try:
            # In real implementation, this would insert into health_checks table
            check_id = f"health_{int(datetime.utcnow().timestamp())}"
            print(f"Storing health check: {check_id} - Status: {health_data.get('overall_status')}")
            return check_id
            
        except Exception as e:
            print(f"Failed to store health check: {e}")
            raise
    
    async def record_performance_metric(
        self,
        metric_data: Dict[str, Any]
    ) -> str:
        """Record performance metric."""
        
        try:
            # In real implementation, this would insert into performance_metrics table
            metric_id = f"metric_{int(datetime.utcnow().timestamp())}"
            print(f"Recording metric: {metric_data.get('metric_name')} = {metric_data.get('value')}")
            return metric_id
            
        except Exception as e:
            print(f"Failed to record performance metric: {e}")
            raise
    
    async def log_error(
        self,
        error_data: Dict[str, Any]
    ) -> str:
        """Log error record."""
        
        try:
            # In real implementation, this would insert into error_logs table
            error_id = f"error_{int(datetime.utcnow().timestamp())}"
            print(f"Logging error: {error_data.get('error_type')} - {error_data.get('error_message')}")
            return error_id
            
        except Exception as e:
            print(f"Failed to log error: {e}")
            raise
    
    async def get_health_history(
        self,
        service_name: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get health check history for a service."""
        
        # Return mock health history data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        history = []
        for i in range(hours):
            check_time = start_time + timedelta(hours=i)
            history.append({
                'checked_at': check_time.isoformat(),
                'service_name': service_name,
                'overall_status': 'healthy' if i % 10 != 0 else 'degraded',
                'overall_health_score': 98.5 if i % 10 != 0 else 85.2,
                'components': {
                    'database': 'healthy',
                    'cache': 'healthy',
                    'queue': 'healthy' if i % 15 != 0 else 'degraded'
                }
            })
        
        return history
    
    async def get_active_alerts(
        self,
        service_name: Optional[str] = None,
        severity: Optional[AlertSeverity] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get active alerts."""
        
        # Return mock active alerts
        return [
            {
                'alert_id': 'alert_001',
                'alert_name': 'high_response_time',
                'severity': 'medium',
                'status': 'open',
                'service_name': service_name or 'mcp-payments',
                'component': 'api',
                'title': 'High API Response Time',
                'description': 'API response time exceeded threshold',
                'metric_value': 250.5,
                'threshold_value': 200.0,
                'triggered_at': (datetime.utcnow() - timedelta(minutes=15)).isoformat()
            },
            {
                'alert_id': 'alert_002',
                'alert_name': 'database_connections',
                'severity': 'low',
                'status': 'open',
                'service_name': service_name or 'mcp-payments',
                'component': 'database',
                'title': 'Database Connection Pool Usage High',
                'description': 'Database connection pool usage is above 80%',
                'metric_value': 85.2,
                'threshold_value': 80.0,
                'triggered_at': (datetime.utcnow() - timedelta(minutes=5)).isoformat()
            }
        ]
    
    async def get_error_summary(
        self,
        service_name: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get error summary for a service."""
        
        return {
            'total_errors': 15,
            'error_rate': 0.12,  # 0.12% error rate
            'error_categories': {
                'validation_error': 8,
                'external_service_error': 4,
                'database_error': 2,
                'network_error': 1
            },
            'top_errors': [
                {
                    'error_type': 'validation_error',
                    'count': 8,
                    'last_seen': (datetime.utcnow() - timedelta(minutes=10)).isoformat()
                },
                {
                    'error_type': 'stripe_timeout',
                    'count': 3,
                    'last_seen': (datetime.utcnow() - timedelta(minutes=25)).isoformat()
                }
            ],
            'period': {
                'start': (datetime.utcnow() - timedelta(hours=hours)).isoformat(),
                'end': datetime.utcnow().isoformat()
            }
        }
    
    async def get_performance_metrics(
        self,
        service_name: str,
        metric_names: List[str],
        hours: int = 24
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get performance metrics for a service."""
        
        metrics = {}
        for metric_name in metric_names:
            if metric_name == 'response_time':
                metrics[metric_name] = [
                    {
                        'timestamp': (datetime.utcnow() - timedelta(minutes=i*5)).isoformat(),
                        'value': 120 + (i % 10) * 5  # Simulate varying response times
                    }
                    for i in range(24)  # Last 2 hours in 5-minute intervals
                ]
            elif metric_name == 'throughput':
                metrics[metric_name] = [
                    {
                        'timestamp': (datetime.utcnow() - timedelta(minutes=i*5)).isoformat(),
                        'value': 85 + (i % 8) * 3  # Simulate varying throughput
                    }
                    for i in range(24)
                ]
            elif metric_name == 'error_rate':
                metrics[metric_name] = [
                    {
                        'timestamp': (datetime.utcnow() - timedelta(minutes=i*5)).isoformat(),
                        'value': 0.1 + (i % 5) * 0.02  # Simulate varying error rates
                    }
                    for i in range(24)
                ]
        
        return metrics
    
    async def cleanup_old_data(self, retention_days: int = 30) -> Dict[str, int]:
        """Clean up old monitoring data."""
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # In real implementation, this would delete old records
        return {
            'health_checks_deleted': 150,
            'performance_metrics_deleted': 5000,
            'error_logs_deleted': 75,
            'resolved_alerts_deleted': 25,
            'cutoff_date': cutoff_date.isoformat()
        } 