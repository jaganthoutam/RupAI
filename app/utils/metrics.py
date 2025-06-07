"""Metrics collection utilities for monitoring and observability."""

from typing import Dict, List, Optional, Any
from datetime import datetime
import time
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry


class MetricsCollector:
    """Production-grade metrics collector for system monitoring."""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        Initialize metrics collector.
        
        Args:
            registry: Optional Prometheus registry (uses default if None)
        """
        self.registry = registry
        self._counters: Dict[str, Counter] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._gauges: Dict[str, Gauge] = {}
        
    def increment_counter(
        self,
        metric_name: str,
        tags: Optional[Dict[str, str]] = None,
        amount: float = 1.0
    ) -> None:
        """
        Increment a counter metric.
        
        Args:
            metric_name: Name of the counter metric
            tags: Optional tags/labels for the metric
            amount: Amount to increment by (default: 1.0)
        """
        try:
            # Get or create counter
            if metric_name not in self._counters:
                label_names = list(tags.keys()) if tags else []
                self._counters[metric_name] = Counter(
                    metric_name,
                    f'Counter metric: {metric_name}',
                    labelnames=label_names,
                    registry=self.registry
                )
            
            # Increment counter
            counter = self._counters[metric_name]
            if tags:
                counter.labels(**tags).inc(amount)
            else:
                counter.inc(amount)
                
        except Exception as e:
            # Don't let metrics collection break the application
            print(f"Error incrementing counter {metric_name}: {e}")
    
    def record_histogram(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a value in a histogram metric.
        
        Args:
            metric_name: Name of the histogram metric
            value: Value to record
            tags: Optional tags/labels for the metric
        """
        try:
            # Get or create histogram
            if metric_name not in self._histograms:
                label_names = list(tags.keys()) if tags else []
                
                # Define buckets based on metric type
                buckets = self._get_default_buckets(metric_name)
                
                self._histograms[metric_name] = Histogram(
                    metric_name,
                    f'Histogram metric: {metric_name}',
                    labelnames=label_names,
                    buckets=buckets,
                    registry=self.registry
                )
            
            # Record value
            histogram = self._histograms[metric_name]
            if tags:
                histogram.labels(**tags).observe(value)
            else:
                histogram.observe(value)
                
        except Exception as e:
            print(f"Error recording histogram {metric_name}: {e}")
    
    def set_gauge(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Set a gauge metric value.
        
        Args:
            metric_name: Name of the gauge metric
            value: Value to set
            tags: Optional tags/labels for the metric
        """
        try:
            # Get or create gauge
            if metric_name not in self._gauges:
                label_names = list(tags.keys()) if tags else []
                self._gauges[metric_name] = Gauge(
                    metric_name,
                    f'Gauge metric: {metric_name}',
                    labelnames=label_names,
                    registry=self.registry
                )
            
            # Set gauge value
            gauge = self._gauges[metric_name]
            if tags:
                gauge.labels(**tags).set(value)
            else:
                gauge.set(value)
                
        except Exception as e:
            print(f"Error setting gauge {metric_name}: {e}")
    
    def time_function(self, metric_name: str, tags: Optional[Dict[str, str]] = None):
        """
        Decorator/context manager to time function execution.
        
        Args:
            metric_name: Name of the timing metric
            tags: Optional tags/labels for the metric
            
        Returns:
            Context manager for timing
        """
        return TimingContext(self, metric_name, tags)
    
    def record_payment_metrics(
        self,
        payment_method: str,
        currency: str,
        amount: float,
        status: str,
        processing_time: float
    ) -> None:
        """
        Record payment-specific metrics.
        
        Args:
            payment_method: Payment method used
            currency: Currency of the payment
            amount: Payment amount
            status: Payment status (success/failed)
            processing_time: Time taken to process payment
        """
        # Count payments by method and status
        self.increment_counter(
            'payments_total',
            tags={
                'method': payment_method,
                'currency': currency,
                'status': status
            }
        )
        
        # Record payment amounts
        self.record_histogram(
            'payment_amount',
            amount,
            tags={'method': payment_method, 'currency': currency}
        )
        
        # Record processing times
        self.record_histogram(
            'payment_processing_time_seconds',
            processing_time,
            tags={'method': payment_method}
        )
    
    def record_api_metrics(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float
    ) -> None:
        """
        Record API request metrics.
        
        Args:
            endpoint: API endpoint called
            method: HTTP method
            status_code: HTTP status code
            response_time: Response time in seconds
        """
        # Count API requests
        self.increment_counter(
            'api_requests_total',
            tags={
                'endpoint': endpoint,
                'method': method,
                'status': str(status_code)
            }
        )
        
        # Record response times
        self.record_histogram(
            'api_response_time_seconds',
            response_time,
            tags={'endpoint': endpoint, 'method': method}
        )
    
    def record_database_metrics(
        self,
        operation: str,
        table: str,
        duration: float,
        success: bool
    ) -> None:
        """
        Record database operation metrics.
        
        Args:
            operation: Database operation (select/insert/update/delete)
            table: Table name
            duration: Operation duration in seconds
            success: Whether operation was successful
        """
        # Count database operations
        self.increment_counter(
            'database_operations_total',
            tags={
                'operation': operation,
                'table': table,
                'success': str(success).lower()
            }
        )
        
        # Record operation duration
        self.record_histogram(
            'database_operation_duration_seconds',
            duration,
            tags={'operation': operation, 'table': table}
        )
    
    def _get_default_buckets(self, metric_name: str) -> List[float]:
        """Get default buckets for histogram based on metric name."""
        
        if 'response_time' in metric_name or 'duration' in metric_name:
            # Time-based metrics (in seconds)
            return [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        elif 'amount' in metric_name:
            # Amount-based metrics
            return [1, 10, 100, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
        else:
            # Default buckets
            return [0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0, 100.0]


class TimingContext:
    """Context manager for timing operations."""
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        metric_name: str,
        tags: Optional[Dict[str, str]] = None
    ):
        self.metrics_collector = metrics_collector
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.metrics_collector.record_histogram(
                self.metric_name,
                duration,
                self.tags
            ) 