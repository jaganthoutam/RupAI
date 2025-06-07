"""
Monitoring and Metrics Collection
Enterprise-grade observability with Prometheus integration.
"""

import asyncio
import logging
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque

from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, REGISTRY
import psutil
from prometheus_client.metrics import MetricWrapperBase

from app.config.settings import settings

logger = logging.getLogger(__name__)

# Global metrics registry to prevent duplicates
_metrics_registry = {}

def get_or_create_metric(metric_class, name, description, labelnames=None, registry=REGISTRY):
    """Get existing metric or create new one to prevent duplicates."""
    key = f"{metric_class.__name__}_{name}"
    if key not in _metrics_registry:
        try:
            if labelnames:
                _metrics_registry[key] = metric_class(name, description, labelnames, registry=registry)
            else:
                _metrics_registry[key] = metric_class(name, description, registry=registry)
        except ValueError as e:
            # Metric already exists, try to get it from registry
            for collector in registry._collector_to_names:
                if hasattr(collector, '_name') and collector._name == name:
                    _metrics_registry[key] = collector
                    break
            else:
                # If we can't find it, create with a unique name
                unique_name = f"{name}_{id(metric_class)}"
                if labelnames:
                    _metrics_registry[key] = metric_class(unique_name, description, labelnames, registry=registry)
                else:
                    _metrics_registry[key] = metric_class(unique_name, description, registry=registry)
    return _metrics_registry[key]


class MetricsCollector:
    """
    Enterprise metrics collector with Prometheus integration.
    
    Features:
    - Request/response metrics
    - Performance monitoring
    - Business metrics
    - System resource tracking
    - Custom metric registration
    """
    
    def __init__(self):
        # Prometheus metrics - use singleton pattern to prevent duplicates
        self.request_counter = get_or_create_metric(
            Counter,
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.request_duration = get_or_create_metric(
            Histogram,
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        
        self.payment_counter = get_or_create_metric(
            Counter,
            'payments_total',
            'Total payments processed',
            ['method', 'currency', 'status', 'provider']
        )
        
        self.payment_amount = get_or_create_metric(
            Histogram,
            'payment_amount',
            'Payment amounts',
            ['currency', 'method']
        )
        
        self.wallet_balance = get_or_create_metric(
            Gauge,
            'wallet_balance_total',
            'Current wallet balances',
            ['currency', 'user_type']
        )
        
        self.active_connections = get_or_create_metric(
            Gauge,
            'active_connections',
            'Active database/Redis connections',
            ['type']
        )
        
        self.error_counter = get_or_create_metric(
            Counter,
            'errors_total',
            'Total errors',
            ['type', 'service', 'severity']
        )
        
        self.system_info = get_or_create_metric(
            Info,
            'system_info',
            'System information'
        )
        
        # System metrics
        self.cpu_usage = get_or_create_metric(Gauge, 'cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = get_or_create_metric(Gauge, 'memory_usage_percent', 'Memory usage percentage')
        self.disk_usage = get_or_create_metric(Gauge, 'disk_usage_percent', 'Disk usage percentage')
        
        # Business metrics
        self.business_metrics = {
            'daily_transactions': defaultdict(int),
            'revenue_by_currency': defaultdict(float),
            'user_activity': defaultdict(int),
            'error_rates': defaultdict(float)
        }
        
        # Performance tracking
        self.response_times = deque(maxlen=1000)
        self.error_log = deque(maxlen=100)
        
        # State
        self.initialized = False
        self.start_time = datetime.utcnow()
        self._monitoring_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize metrics collector."""
        try:
            logger.info("🔄 Initializing metrics collector...")
            
            # Set system info
            try:
                self.system_info.info({
                    'version': settings.SERVER_VERSION,
                    'environment': settings.ENVIRONMENT,
                    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    'start_time': self.start_time.isoformat()
                })
            except Exception as e:
                logger.warning("Could not set system info: %s", str(e))
            
            # Start monitoring task
            if settings.ENABLE_METRICS:
                self._monitoring_task = asyncio.create_task(self._monitor_system())
            
            self.initialized = True
            logger.info("✅ Metrics collector initialized")
            
        except Exception as e:
            logger.error("❌ Failed to initialize metrics collector: %s", str(e))
            raise
    
    async def shutdown(self) -> None:
        """Shutdown metrics collector."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Metrics collector shut down")
    
    # Request Metrics
    async def record_request(self, method: str, endpoint: str = "unknown") -> None:
        """Record HTTP request."""
        try:
            # This will be called by middleware with actual status code
            pass
        except Exception as e:
            logger.error("Error recording request metric: %s", str(e))
    
    async def record_request_complete(
        self, 
        method: str, 
        endpoint: str, 
        status_code: int, 
        duration: float
    ) -> None:
        """Record completed HTTP request."""
        try:
            self.request_counter.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            self.request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            # Track response times
            self.response_times.append({
                'timestamp': datetime.utcnow(),
                'duration': duration,
                'endpoint': endpoint
            })
            
        except Exception as e:
            logger.error("Error recording request completion metric: %s", str(e))
    
    async def record_request_duration(self, method: str, duration: float) -> None:
        """Record request duration (simplified version)."""
        try:
            self.request_duration.labels(
                method=method,
                endpoint="mcp"
            ).observe(duration)
        except Exception as e:
            logger.error("Error recording request duration: %s", str(e))
    
    # Payment Metrics
    async def record_payment(
        self,
        amount: float,
        currency: str,
        method: str,
        status: str,
        provider: str = "unknown"
    ) -> None:
        """Record payment transaction."""
        try:
            self.payment_counter.labels(
                method=method,
                currency=currency,
                status=status,
                provider=provider
            ).inc()
            
            if status == "completed":
                self.payment_amount.labels(
                    currency=currency,
                    method=method
                ).observe(amount)
                
                # Update business metrics
                today = datetime.utcnow().date().isoformat()
                self.business_metrics['daily_transactions'][today] += 1
                self.business_metrics['revenue_by_currency'][currency] += amount
            
        except Exception as e:
            logger.error("Error recording payment metric: %s", str(e))
    
    async def update_wallet_balance(
        self, 
        currency: str, 
        balance: float, 
        user_type: str = "regular"
    ) -> None:
        """Update wallet balance metric."""
        try:
            self.wallet_balance.labels(
                currency=currency,
                user_type=user_type
            ).set(balance)
        except Exception as e:
            logger.error("Error updating wallet balance metric: %s", str(e))
    
    async def record_performance(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record performance metrics for operations."""
        try:
            # Record operation duration
            self.request_duration.labels(
                method="performance",
                endpoint=operation
            ).observe(duration)
            
            # Record operation count
            status = "success" if success else "failed"
            self.request_counter.labels(
                method="performance",
                endpoint=operation,
                status_code=status
            ).inc()
            
            # Track in response times for analytics
            self.response_times.append({
                'timestamp': datetime.utcnow(),
                'duration': duration,
                'endpoint': operation,
                'success': success,
                'metadata': metadata or {}
            })
            
        except Exception as e:
            logger.error("Error recording performance metric: %s", str(e))
    
    # Error Metrics
    async def record_error(
        self, 
        error_type: str, 
        service: str, 
        severity: str = "error",
        details: Optional[str] = None
    ) -> None:
        """Record error occurrence."""
        try:
            self.error_counter.labels(
                type=error_type,
                service=service,
                severity=severity
            ).inc()
            
            # Store in error log for analysis
            self.error_log.append({
                'timestamp': datetime.utcnow().isoformat(),
                'type': error_type,
                'service': service,
                'severity': severity,
                'details': details
            })
            
            # Update business metrics
            self.business_metrics['error_rates'][error_type] += 1
            
        except Exception as e:
            logger.error("Error recording error metric: %s", str(e))
    
    async def record_tool_call(self, tool_type: str, tool_name: str) -> None:
        """Record MCP tool call."""
        try:
            # Use existing payment counter for tool calls
            self.payment_counter.labels(
                method=tool_name,
                currency="N/A",
                status="called",
                provider=tool_type
            ).inc()
        except Exception as e:
            logger.error("Error recording tool call metric: %s", str(e))
    
    # Connection Metrics
    async def update_connection_count(self, connection_type: str, count: int) -> None:
        """Update active connection count."""
        try:
            self.active_connections.labels(type=connection_type).set(count)
        except Exception as e:
            logger.error("Error updating connection metric: %s", str(e))
    
    # System Monitoring
    async def _monitor_system(self) -> None:
        """Background task to monitor system resources."""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_usage.set(cpu_percent)
                
                # Memory usage
                memory = psutil.virtual_memory()
                self.memory_usage.set(memory.percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.disk_usage.set(disk_percent)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("System monitoring error: %s", str(e))
                await asyncio.sleep(60)  # Wait longer on error
    
    # Analytics Methods
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        if not self.response_times:
            return {"status": "no_data"}
        
        times = [r['duration'] for r in self.response_times]
        times.sort()
        
        count = len(times)
        return {
            "request_count": count,
            "avg_response_time": sum(times) / count,
            "p50_response_time": times[int(count * 0.5)],
            "p95_response_time": times[int(count * 0.95)],
            "p99_response_time": times[int(count * 0.99)],
            "max_response_time": max(times),
            "min_response_time": min(times)
        }
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """Get business metrics summary."""
        return {
            "daily_transactions": dict(self.business_metrics['daily_transactions']),
            "revenue_by_currency": dict(self.business_metrics['revenue_by_currency']),
            "user_activity": dict(self.business_metrics['user_activity']),
            "total_transactions": sum(self.business_metrics['daily_transactions'].values()),
            "total_revenue": sum(self.business_metrics['revenue_by_currency'].values())
        }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error metrics summary."""
        if not self.error_log:
            return {"status": "no_errors"}
        
        recent_errors = [e for e in self.error_log if e['timestamp'] > datetime.utcnow() - timedelta(hours=1)]
        
        error_types = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for error in recent_errors:
            error_types[error['type']] += 1
            severity_counts[error['severity']] += 1
        
        return {
            "total_errors_last_hour": len(recent_errors),
            "error_types": dict(error_types),
            "severity_distribution": dict(severity_counts),
            "recent_errors": list(self.error_log)[-10:]  # Last 10 errors
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        try:
            # Get current system stats
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent if hasattr(psutil.disk_usage('/'), 'percent') else 0
            
            # Determine health status
            status = "healthy"
            issues = []
            
            if cpu > 80:
                status = "warning"
                issues.append("High CPU usage")
            
            if memory > 85:
                status = "warning" if status == "healthy" else "critical"
                issues.append("High memory usage")
            
            if disk > 90:
                status = "critical"
                issues.append("High disk usage")
            
            return {
                "status": status,
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "system": {
                    "cpu_percent": cpu,
                    "memory_percent": memory,
                    "disk_percent": disk
                },
                "issues": issues,
                "performance": self.get_performance_summary(),
                "errors": self.get_error_summary()
            }
            
        except Exception as e:
            logger.error("Error getting health status: %s", str(e))
            return {
                "status": "unknown",
                "error": str(e)
            }

# Global instance
metrics_collector = MetricsCollector()

def log_event(event_type: str, details: Dict[str, Any] = None) -> None:
    """
    Log an event for monitoring purposes.
    
    Args:
        event_type: Type of event (e.g., 'payment_processed', 'task_started')
        details: Additional event details
    """
    try:
        if details is None:
            details = {}
        
        logger.info(f"Event: {event_type} - {details}")
        
        # Record as error metric if it's an error event
        if 'error' in event_type.lower() or 'failed' in event_type.lower():
            asyncio.create_task(metrics_collector.record_error(
                error_type=event_type,
                service=details.get('service', 'unknown'),
                severity=details.get('severity', 'info')
            ))
    except Exception as e:
        logger.error(f"Error logging event {event_type}: {str(e)}")

def track_performance(func_or_duration=None, *, duration=None):
    """
    Track performance of function execution or log performance data.
    
    Can be used as:
    1. A decorator: @track_performance
    2. A decorator with duration: @track_performance(duration=5.0)
    3. A function call: track_performance("operation", 5.0)
    
    Args:
        func_or_duration: Function to decorate or duration value
        duration: Explicit duration parameter when used as decorator
    """
    import functools
    import time
    from typing import Union, Callable, Any
    
    # Case 1: Used as @track_performance (without parentheses)
    if callable(func_or_duration):
        func = func_or_duration
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log performance
                logger.info(f"Performance: {func.__name__} completed in {execution_time:.3f}s")
                
                # Record as performance metric
                try:
                    asyncio.create_task(metrics_collector.record_performance(
                        operation=func.__name__,
                        duration=execution_time,
                        success=True
                    ))
                except Exception as e:
                    logger.warning(f"Failed to record performance metrics: {e}")
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Performance: {func.__name__} failed in {execution_time:.3f}s - {e}")
                
                # Record as failed performance metric
                try:
                    asyncio.create_task(metrics_collector.record_performance(
                        operation=func.__name__,
                        duration=execution_time,
                        success=False
                    ))
                except Exception:
                    pass
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"Performance: {func.__name__} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Performance: {func.__name__} failed in {execution_time:.3f}s - {e}")
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    # Case 2: Used as @track_performance() or @track_performance(duration=5.0)
    elif func_or_duration is None or isinstance(func_or_duration, (int, float)):
        def decorator(func):
            return track_performance(func)
        return decorator
    
    # Case 3: Used as function call track_performance("operation", 5.0)
    else:
        operation_name = func_or_duration
        execution_time = duration or 0.0
        
        try:
            logger.info(f"Performance: {operation_name} - {execution_time:.3f}s")
            
            # Record as performance metric
            asyncio.create_task(metrics_collector.record_performance(
                operation=operation_name,
                duration=execution_time,
                success=True
            ))
        except Exception as e:
            logger.warning(f"Failed to log performance for {operation_name}: {e}")
        
        return None 