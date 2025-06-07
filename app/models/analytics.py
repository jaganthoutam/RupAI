"""Analytics models for comprehensive payment system monitoring and reporting."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import (
    Column, String, Integer, Numeric, DateTime, Boolean, 
    Text, ForeignKey, Index, JSON, Float
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class MetricType(str, Enum):
    """Types of metrics for categorization."""
    PAYMENT = "payment"
    USER = "user"
    SYSTEM = "system"
    REVENUE = "revenue"
    FRAUD = "fraud"


class PaymentMetrics(Base):
    """Payment transaction metrics and KPIs."""
    
    __tablename__ = "payment_metrics"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    hour = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    
    # Payment dimensions
    currency = Column(String(3), nullable=False, index=True)
    payment_method = Column(String(50), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    country_code = Column(String(2), index=True)
    
    # Volume metrics
    total_transactions = Column(Integer, default=0, nullable=False)
    successful_transactions = Column(Integer, default=0, nullable=False)
    failed_transactions = Column(Integer, default=0, nullable=False)
    pending_transactions = Column(Integer, default=0, nullable=False)
    
    # Amount metrics
    total_amount = Column(Numeric(15, 2), default=0, nullable=False)
    successful_amount = Column(Numeric(15, 2), default=0, nullable=False)
    failed_amount = Column(Numeric(15, 2), default=0, nullable=False)
    average_transaction_amount = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Performance metrics
    average_processing_time = Column(Float, default=0, nullable=False)  # in seconds
    p95_processing_time = Column(Float, default=0, nullable=False)
    p99_processing_time = Column(Float, default=0, nullable=False)
    
    # Success rates
    success_rate = Column(Float, default=0, nullable=False)  # percentage
    decline_rate = Column(Float, default=0, nullable=False)
    timeout_rate = Column(Float, default=0, nullable=False)
    
    # Additional metrics
    unique_customers = Column(Integer, default=0, nullable=False)
    repeat_customers = Column(Integer, default=0, nullable=False)
    new_customers = Column(Integer, default=0, nullable=False)
    
    __table_args__ = (
        Index('idx_payment_metrics_date_currency', 'date', 'currency'),
        Index('idx_payment_metrics_provider_method', 'provider', 'payment_method'),
    )


class UserMetrics(Base):
    """User behavior and engagement metrics."""
    
    __tablename__ = "user_metrics"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # User dimensions
    user_id = Column(PgUUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    user_segment = Column(String(50), index=True)  # premium, standard, new, etc.
    country_code = Column(String(2), index=True)
    
    # Engagement metrics
    total_sessions = Column(Integer, default=0, nullable=False)
    total_session_duration = Column(Integer, default=0, nullable=False)  # in seconds
    average_session_duration = Column(Float, default=0, nullable=False)
    
    # Activity metrics
    total_payments = Column(Integer, default=0, nullable=False)
    total_payment_amount = Column(Numeric(15, 2), default=0, nullable=False)
    wallet_balance = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Behavioral metrics
    days_since_last_payment = Column(Integer, default=0, nullable=False)
    payment_frequency_score = Column(Float, default=0, nullable=False)
    churn_risk_score = Column(Float, default=0, nullable=False)
    lifetime_value = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Preferences
    preferred_payment_method = Column(String(50))
    preferred_currency = Column(String(3))
    
    __table_args__ = (
        Index('idx_user_metrics_date_segment', 'date', 'user_segment'),
        Index('idx_user_metrics_churn_risk', 'churn_risk_score'),
    )


class SystemMetrics(Base):
    """System performance and health metrics."""
    
    __tablename__ = "system_metrics"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # System dimensions
    service_name = Column(String(100), nullable=False, index=True)
    instance_id = Column(String(100), nullable=False, index=True)
    environment = Column(String(20), nullable=False, index=True)
    
    # Performance metrics
    cpu_usage = Column(Float, default=0, nullable=False)  # percentage
    memory_usage = Column(Float, default=0, nullable=False)  # percentage
    disk_usage = Column(Float, default=0, nullable=False)  # percentage
    network_io = Column(Float, default=0, nullable=False)  # bytes/sec
    
    # Application metrics
    active_connections = Column(Integer, default=0, nullable=False)
    requests_per_second = Column(Float, default=0, nullable=False)
    average_response_time = Column(Float, default=0, nullable=False)  # milliseconds
    error_rate = Column(Float, default=0, nullable=False)  # percentage
    
    # Database metrics
    db_connections = Column(Integer, default=0, nullable=False)
    db_query_time = Column(Float, default=0, nullable=False)  # milliseconds
    db_slow_queries = Column(Integer, default=0, nullable=False)
    
    # Cache metrics
    cache_hit_rate = Column(Float, default=0, nullable=False)  # percentage
    cache_memory_usage = Column(Float, default=0, nullable=False)  # MB
    
    # Queue metrics
    queue_size = Column(Integer, default=0, nullable=False)
    queue_processing_rate = Column(Float, default=0, nullable=False)  # messages/sec
    
    __table_args__ = (
        Index('idx_system_metrics_timestamp_service', 'timestamp', 'service_name'),
        Index('idx_system_metrics_environment', 'environment'),
    )


class TransactionAnalytics(Base):
    """Advanced transaction analytics and patterns."""
    
    __tablename__ = "transaction_analytics"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    analysis_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Transaction dimensions
    transaction_id = Column(PgUUID(as_uuid=True), ForeignKey('payments.id'), nullable=False)
    user_id = Column(PgUUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Analysis results
    risk_score = Column(Float, default=0, nullable=False)  # 0-100
    fraud_indicators = Column(JSON)  # List of detected fraud indicators
    velocity_score = Column(Float, default=0, nullable=False)  # Transaction velocity analysis
    
    # Pattern analysis
    transaction_pattern = Column(String(50))  # normal, suspicious, high-velocity, etc.
    device_fingerprint = Column(String(255))
    ip_risk_score = Column(Float, default=0, nullable=False)
    geolocation_risk = Column(Float, default=0, nullable=False)
    
    # Behavioral analysis
    user_behavior_score = Column(Float, default=0, nullable=False)
    deviation_from_normal = Column(Float, default=0, nullable=False)
    
    # Recommendations
    recommended_action = Column(String(100))  # approve, review, decline, monitor
    confidence_score = Column(Float, default=0, nullable=False)
    
    # Additional context
    analysis_metadata = Column(JSON)
    
    __table_args__ = (
        Index('idx_transaction_analytics_date_risk', 'analysis_date', 'risk_score'),
        Index('idx_transaction_analytics_user_pattern', 'user_id', 'transaction_pattern'),
    )


class RevenueAnalytics(Base):
    """Revenue tracking and financial analytics."""
    
    __tablename__ = "revenue_analytics"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly
    
    # Revenue dimensions
    currency = Column(String(3), nullable=False, index=True)
    revenue_stream = Column(String(50), nullable=False, index=True)  # payments, subscriptions, fees
    product_category = Column(String(100), index=True)
    
    # Revenue metrics
    gross_revenue = Column(Numeric(15, 2), default=0, nullable=False)
    net_revenue = Column(Numeric(15, 2), default=0, nullable=False)
    processing_fees = Column(Numeric(15, 2), default=0, nullable=False)
    refunds = Column(Numeric(15, 2), default=0, nullable=False)
    chargebacks = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Volume metrics
    transaction_count = Column(Integer, default=0, nullable=False)
    unique_customers = Column(Integer, default=0, nullable=False)
    average_transaction_value = Column(Numeric(15, 2), default=0, nullable=False)
    
    # Growth metrics
    revenue_growth_rate = Column(Float, default=0, nullable=False)  # percentage
    customer_growth_rate = Column(Float, default=0, nullable=False)
    transaction_growth_rate = Column(Float, default=0, nullable=False)
    
    # Cohort analysis
    new_customer_revenue = Column(Numeric(15, 2), default=0, nullable=False)
    returning_customer_revenue = Column(Numeric(15, 2), default=0, nullable=False)
    customer_retention_rate = Column(Float, default=0, nullable=False)
    
    # Forecasting
    projected_revenue = Column(Numeric(15, 2), default=0, nullable=False)
    confidence_interval = Column(Float, default=0, nullable=False)
    
    __table_args__ = (
        Index('idx_revenue_analytics_date_stream', 'date', 'revenue_stream'),
        Index('idx_revenue_analytics_currency_period', 'currency', 'period_type'),
    )


class FraudDetection(Base):
    """Fraud detection and prevention analytics."""
    
    __tablename__ = "fraud_detection"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Time dimensions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    detected_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Transaction/User context
    transaction_id = Column(PgUUID(as_uuid=True), ForeignKey('payments.id'), nullable=True)
    user_id = Column(PgUUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Fraud detection
    fraud_type = Column(String(100), nullable=False, index=True)  # card_fraud, account_takeover, etc.
    risk_level = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    confidence_score = Column(Float, default=0, nullable=False)  # 0-100
    
    # Detection details
    detection_method = Column(String(100), nullable=False)  # rule_based, ml_model, manual_review
    triggered_rules = Column(JSON)  # List of fraud rules triggered
    risk_factors = Column(JSON)  # Specific risk factors identified
    
    # Context information
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    device_fingerprint = Column(String(255))
    geolocation = Column(JSON)  # lat, lng, country, city
    
    # Actions taken
    action_taken = Column(String(50), nullable=False)  # blocked, flagged, approved, manual_review
    manual_review_required = Column(Boolean, default=False, nullable=False)
    reviewed_by = Column(PgUUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    review_notes = Column(Text)
    
    # Resolution
    false_positive = Column(Boolean, default=False, nullable=False)
    confirmed_fraud = Column(Boolean, default=False, nullable=False)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime(timezone=True))
    
    # Financial impact
    potential_loss_amount = Column(Numeric(15, 2), default=0, nullable=False)
    actual_loss_amount = Column(Numeric(15, 2), default=0, nullable=False)
    prevented_loss_amount = Column(Numeric(15, 2), default=0, nullable=False)
    
    __table_args__ = (
        Index('idx_fraud_detection_date_type', 'detected_at', 'fraud_type'),
        Index('idx_fraud_detection_risk_level', 'risk_level'),
        Index('idx_fraud_detection_user_confidence', 'user_id', 'confidence_score'),
    ) 