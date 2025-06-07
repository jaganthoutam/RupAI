"""
Enterprise MCP Payments - Background Tasks Package

This package contains all Celery background tasks for the MCP Payments system.
Implements enterprise-grade async processing with RabbitMQ and Redis.

Package Structure:
- celery_app.py: Celery application configuration and initialization
- payment_tasks.py: Payment processing, verification, and reconciliation tasks  
- analytics_tasks.py: Data aggregation, reporting, and AI analytics tasks
- compliance_tasks.py: Audit logging, regulatory reporting, and compliance tasks
- notification_tasks.py: Multi-channel notifications (email, SMS, webhook)
- monitoring_tasks.py: System health monitoring, alerts, and performance tasks
- utils.py: Shared task utilities, decorators, and helpers

Features:
- Async task processing with retry logic and exponential backoff
- Multi-queue routing for different task types
- Dead letter queue handling for failed tasks
- Task monitoring and metrics collection
- Integration with existing service layer
- Event-driven architecture support
"""

from .celery_app import app as celery_app

__all__ = ['celery_app'] 