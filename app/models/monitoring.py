"""Monitoring models for system health, alerts, and performance tracking."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, 
    Text, ForeignKey, Index, JSON, Float
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class HealthStatus(str, Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status enumeration."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLOSED = "closed"


class HealthCheck(Base):
    """System health check results."""
    
    __tablename__ = "health_checks"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    checked_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Service identification
    service_name = Column(String(100), nullable=False, index=True)
    instance_id = Column(String(100), nullable=False, index=True)
    environment = Column(String(20), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    
    # Health status
    status = Column(String(20), nullable=False, index=True)  # HealthStatus enum
    overall_health_score = Column(Float, default=0, nullable=False)  # 0-100
    
    # Component health checks
    database_status = Column(String(20), nullable=False)
    database_response_time = Column(Float, default=0, nullable=False)  # milliseconds
    database_connection_count = Column(Integer, default=0, nullable=False)
    
    cache_status = Column(String(20), nullable=False)
    cache_response_time = Column(Float, default=0, nullable=False)
    cache_hit_rate = Column(Float, default=0, nullable=False)
    
    queue_status = Column(String(20), nullable=False)
    queue_size = Column(Integer, default=0, nullable=False)
    queue_processing_rate = Column(Float, default=0, nullable=False)
    
    # External service checks
    payment_providers_status = Column(JSON)  # Status of each payment provider
    third_party_services_status = Column(JSON)  # Status of external dependencies
    
    # System resources
    cpu_usage = Column(Float, default=0, nullable=False)
    memory_usage = Column(Float, default=0, nullable=False)
    disk_usage = Column(Float, default=0, nullable=False)
    network_latency = Column(Float, default=0, nullable=False)
    
    # Application metrics
    active_connections = Column(Integer, default=0, nullable=False)
    requests_in_queue = Column(Integer, default=0, nullable=False)
    error_rate_last_hour = Column(Float, default=0, nullable=False)
    
    # Additional details
    health_details = Column(JSON)  # Detailed health information
    warnings = Column(JSON)  # List of warnings
    errors = Column(JSON)  # List of errors
    
    __table_args__ = (
        Index('idx_health_checks_service_time', 'service_name', 'checked_at'),
        Index('idx_health_checks_status_env', 'status', 'environment'),
    )


class SystemAlert(Base):
    """System alerts and notifications."""
    
    __tablename__ = "system_alerts"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    triggered_at = Column(DateTime(timezone=True), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Alert identification
    alert_id = Column(String(100), nullable=False, unique=True, index=True)
    alert_name = Column(String(200), nullable=False)
    alert_type = Column(String(50), nullable=False, index=True)  # performance, error, security, etc.
    
    # Alert details
    severity = Column(String(20), nullable=False, index=True)  # AlertSeverity enum
    status = Column(String(20), nullable=False, index=True)  # AlertStatus enum
    priority = Column(Integer, default=0, nullable=False)  # 0-10, higher is more urgent
    
    # Source information
    service_name = Column(String(100), nullable=False, index=True)
    instance_id = Column(String(100), nullable=False)
    environment = Column(String(20), nullable=False, index=True)
    component = Column(String(100), nullable=False)  # database, cache, payment_provider, etc.
    
    # Alert content
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    message = Column(Text)
    
    # Metrics and thresholds
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    threshold_value = Column(Float, nullable=False)
    comparison_operator = Column(String(10), nullable=False)  # >, <, >=, <=, ==, !=
    
    # Context information
    tags = Column(JSON)  # Key-value pairs for categorization
    alert_metadata = Column(JSON)  # Additional context data
    affected_users = Column(Integer, default=0, nullable=False)
    estimated_impact = Column(String(100))  # Low, Medium, High impact description
    
    # Resolution information
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(PgUUID(as_uuid=True), ForeignKey('users.id'))
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(PgUUID(as_uuid=True), ForeignKey('users.id'))
    resolution_notes = Column(Text)
    
    # Escalation
    escalated = Column(Boolean, default=False, nullable=False)
    escalated_at = Column(DateTime(timezone=True))
    escalation_level = Column(Integer, default=0, nullable=False)
    
    # Notification tracking
    notifications_sent = Column(JSON)  # Track which notifications were sent
    notification_channels = Column(JSON)  # email, slack, pagerduty, etc.
    
    __table_args__ = (
        Index('idx_system_alerts_service_severity', 'service_name', 'severity'),
        Index('idx_system_alerts_status_priority', 'status', 'priority'),
        Index('idx_system_alerts_type_environment', 'alert_type', 'environment'),
    )


class PerformanceMetric(Base):
    """Detailed performance metrics and benchmarks."""
    
    __tablename__ = "performance_metrics"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Service identification
    service_name = Column(String(100), nullable=False, index=True)
    instance_id = Column(String(100), nullable=False)
    environment = Column(String(20), nullable=False, index=True)
    
    # Metric identification
    metric_category = Column(String(50), nullable=False, index=True)  # api, database, cache, etc.
    metric_name = Column(String(100), nullable=False, index=True)
    metric_type = Column(String(20), nullable=False)  # counter, gauge, histogram, timer
    
    # Metric values
    value = Column(Float, nullable=False)
    min_value = Column(Float)
    max_value = Column(Float)
    avg_value = Column(Float)
    
    # Statistical measures
    p50_value = Column(Float)  # Median
    p95_value = Column(Float)
    p99_value = Column(Float)
    std_deviation = Column(Float)
    
    # Contextual information
    endpoint = Column(String(200))  # For API metrics
    operation = Column(String(100))  # Database operation, cache operation, etc.
    user_segment = Column(String(50))  # premium, standard, free, etc.
    
    # Performance indicators
    response_time = Column(Float)  # milliseconds
    throughput = Column(Float)  # requests/transactions per second
    error_rate = Column(Float)  # percentage
    success_rate = Column(Float)  # percentage
    
    # Resource utilization
    cpu_usage = Column(Float)  # percentage
    memory_usage = Column(Float)  # percentage
    io_usage = Column(Float)  # percentage
    network_usage = Column(Float)  # bytes/second
    
    # Business metrics
    concurrent_users = Column(Integer)
    active_sessions = Column(Integer)
    queue_depth = Column(Integer)
    
    # Additional metadata
    tags = Column(JSON)  # Key-value pairs for filtering/grouping
    dimensions = Column(JSON)  # Additional dimensional data
    
    __table_args__ = (
        Index('idx_performance_metrics_service_category', 'service_name', 'metric_category'),
        Index('idx_performance_metrics_name_timestamp', 'metric_name', 'timestamp'),
        Index('idx_performance_metrics_environment_type', 'environment', 'metric_type'),
    )


class ErrorLog(Base):
    """Comprehensive error logging and tracking."""
    
    __tablename__ = "error_logs"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Error identification
    error_id = Column(String(100), nullable=False, index=True)  # Unique error identifier
    correlation_id = Column(String(100), nullable=False, index=True)  # Request correlation ID
    trace_id = Column(String(100), nullable=False, index=True)  # Distributed tracing ID
    
    # Service information
    service_name = Column(String(100), nullable=False, index=True)
    instance_id = Column(String(100), nullable=False)
    environment = Column(String(20), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    
    # Error details
    error_type = Column(String(100), nullable=False, index=True)  # Exception type
    error_category = Column(String(50), nullable=False, index=True)  # system, business, validation, etc.
    severity_level = Column(String(20), nullable=False, index=True)  # debug, info, warning, error, critical
    
    # Error content
    error_message = Column(Text, nullable=False)
    error_code = Column(String(50))  # Application-specific error code
    stack_trace = Column(Text)
    
    # Context information
    endpoint = Column(String(200))  # API endpoint
    http_method = Column(String(10))  # GET, POST, etc.
    http_status_code = Column(Integer)
    user_id = Column(PgUUID(as_uuid=True), ForeignKey('users.id'))
    session_id = Column(String(100))
    
    # Request details
    request_url = Column(String(500))
    request_headers = Column(JSON)
    request_body = Column(Text)  # Sanitized request body
    response_body = Column(Text)  # Error response body
    
    # Client information
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    referer = Column(String(500))
    
    # Performance impact
    response_time = Column(Float)  # milliseconds
    memory_usage = Column(Float)  # MB
    cpu_usage = Column(Float)  # percentage
    
    # Error tracking
    first_occurrence = Column(DateTime(timezone=True), nullable=False)
    last_occurrence = Column(DateTime(timezone=True), nullable=False)
    occurrence_count = Column(Integer, default=1, nullable=False)
    
    # Resolution tracking
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(PgUUID(as_uuid=True), ForeignKey('users.id'))
    resolution_notes = Column(Text)
    
    # Classification
    is_known_issue = Column(Boolean, default=False, nullable=False)
    is_regression = Column(Boolean, default=False, nullable=False)
    impact_level = Column(String(20))  # low, medium, high, critical
    
    # Additional metadata
    tags = Column(JSON)  # Custom tags for categorization
    custom_fields = Column(JSON)  # Additional custom data
    
    __table_args__ = (
        Index('idx_error_logs_service_category', 'service_name', 'error_category'),
        Index('idx_error_logs_severity_time', 'severity_level', 'occurred_at'),
        Index('idx_error_logs_correlation_trace', 'correlation_id', 'trace_id'),
        Index('idx_error_logs_type_resolved', 'error_type', 'resolved'),
    ) 