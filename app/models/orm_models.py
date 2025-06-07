"""SQLAlchemy ORM models for database operations."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, 
    Text, ForeignKey, Index, JSON, Float, Numeric
)
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.sql import func

from .base import Base


class PaymentORM(Base):
    """SQLAlchemy model for payments."""
    
    __tablename__ = "payments"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Basic payment information
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    method = Column(String(50), nullable=False, index=True)
    
    # Customer and provider information
    customer_id = Column(PgUUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)
    provider_transaction_id = Column(String(255), index=True)
    
    # Additional information
    description = Column(Text)
    payment_metadata = Column(JSON)  # Renamed from metadata to avoid conflict
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_payments_customer_status', 'customer_id', 'status'),
        Index('idx_payments_provider_method', 'provider', 'method'),
        Index('idx_payments_created_at', 'created_at'),
    )


class UserORM(Base):
    """SQLAlchemy model for users."""
    
    __tablename__ = "users"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Basic user information
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='user', index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_role', 'role'),
    )


class WalletORM(Base):
    """SQLAlchemy model for wallets."""
    
    __tablename__ = "wallets"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Wallet information
    user_id = Column(PgUUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    balance = Column(Numeric(15, 2), default=0, nullable=False)
    currency = Column(String(3), nullable=False, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_wallets_user_currency', 'user_id', 'currency'),
        Index('idx_wallets_active', 'is_active'),
    )


class WalletTransactionORM(Base):
    """SQLAlchemy model for wallet transactions."""
    
    __tablename__ = "wallet_transactions"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Transaction information
    wallet_id = Column(PgUUID(as_uuid=True), ForeignKey('wallets.id'), nullable=False, index=True)
    transaction_type = Column(String(20), nullable=False, index=True)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Balance tracking
    balance_before = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    
    # Reference information
    reference_id = Column(PgUUID(as_uuid=True), index=True)
    description = Column(Text)
    transaction_metadata = Column(JSON)  # Renamed from metadata to avoid conflict
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_wallet_transactions_wallet_type', 'wallet_id', 'transaction_type'),
        Index('idx_wallet_transactions_created_at', 'created_at'),
    )


class AuditLogORM(Base):
    """SQLAlchemy model for audit logs."""
    
    __tablename__ = "audit_logs"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Audit information
    user_id = Column(PgUUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    
    # Details
    old_values = Column(JSON)
    new_values = Column(JSON)
    audit_metadata = Column(JSON)  # Renamed from metadata to avoid conflict
    
    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_audit_logs_action_resource', 'action', 'resource_type'),
        Index('idx_audit_logs_user_time', 'user_id', 'created_at'),
        Index('idx_audit_logs_resource_id', 'resource_id'),
    ) 