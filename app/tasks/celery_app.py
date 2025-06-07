"""
Enterprise MCP Payments - Celery Application Configuration

Celery application setup with enterprise-grade configuration for:
- RabbitMQ message broker integration
- Redis result backend
- Multi-queue task routing
- Dead letter queue handling
- Task monitoring and metrics
- Auto-discovery of task modules
"""

import os
from celery import Celery
from kombu import Queue, Exchange
from typing import Dict, Any

# Import configuration
from app.config.settings import get_settings

settings = get_settings()

# Celery application initialization
app = Celery('mcp_payments')

# Broker and backend configuration
BROKER_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# Define exchanges and queues
default_exchange = Exchange('mcp_payments', type='topic')

# Queue configuration with routing
CELERY_QUEUES = [
    Queue('payments', exchange=default_exchange, routing_key='payment.*'),
    Queue('analytics', exchange=default_exchange, routing_key='analytics.*'),
    Queue('compliance', exchange=default_exchange, routing_key='compliance.*'),
    Queue('notifications', exchange=default_exchange, routing_key='notification.*'),
    Queue('monitoring', exchange=default_exchange, routing_key='monitoring.*'),
    Queue('default', exchange=default_exchange, routing_key='default.*'),
]

# Celery configuration
CELERY_CONFIG: Dict[str, Any] = {
    # Broker settings
    'broker_url': BROKER_URL,
    'result_backend': RESULT_BACKEND,
    
    # Serialization
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    
    # Beat scheduler using Redis (avoid file permission issues)
    'beat_scheduler': 'redbeat.RedBeatScheduler',
    'redbeat_redis_url': os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
    
    # Task routing
    'task_routes': {
        'app.tasks.payment_tasks.*': {'queue': 'payments'},
        'app.tasks.analytics_tasks.*': {'queue': 'analytics'},
        'app.tasks.compliance_tasks.*': {'queue': 'compliance'},
        'app.tasks.notification_tasks.*': {'queue': 'notifications'},
        'app.tasks.monitoring_tasks.*': {'queue': 'monitoring'},
    },
    
    # Queue configuration
    'task_queues': CELERY_QUEUES,
    'task_default_queue': 'default',
    'task_default_exchange': 'mcp_payments',
    'task_default_exchange_type': 'topic',
    'task_default_routing_key': 'default.task',
    
    # Task execution settings
    'task_acks_late': True,
    'worker_prefetch_multiplier': 1,
    'task_reject_on_worker_lost': True,
    
    # Retry settings
    'task_autoretry_for': (Exception,),
    'task_retry_jitter': True,
    'task_max_retries': 3,
    'task_default_retry_delay': 60,
    
    # Result settings
    'result_expires': 3600,  # 1 hour
    'result_persistent': True,
    
    # Monitoring
    'worker_send_task_events': True,
    'task_send_sent_event': True,
    
    # Security
    'worker_hijack_root_logger': False,
    'worker_log_color': False,
    
    # Beat schedule for periodic tasks
    'beat_schedule': {
        'analytics-aggregation': {
            'task': 'app.tasks.analytics_tasks.aggregate_daily_analytics',
            'schedule': 300.0,  # Every 5 minutes for demo
        },
        'compliance-audit': {
            'task': 'app.tasks.compliance_tasks.process_audit_logs',
            'schedule': 600.0,  # Every 10 minutes
        },
        'monitoring-health-check': {
            'task': 'app.tasks.monitoring_tasks.system_health_check',
            'schedule': 60.0,  # Every minute
        },
        'notification-cleanup': {
            'task': 'app.tasks.notification_tasks.cleanup_old_notifications',
            'schedule': 3600.0,  # Every hour
        },
    },
    
    # Worker settings
    'worker_max_tasks_per_child': 1000,
    'worker_disable_rate_limits': False,
    'worker_enable_remote_control': True,
}

# Configure Celery with settings
app.config_from_object('app.tasks.celery_app:CELERY_CONFIG')

# Auto-discover tasks from all task modules
app.autodiscover_tasks([
    'app.tasks.payment_tasks',
    'app.tasks.analytics_tasks', 
    'app.tasks.compliance_tasks',
    'app.tasks.notification_tasks',
    'app.tasks.monitoring_tasks',
])

# Task base class with common functionality
class BaseTask(app.Task):
    """Base task class with common functionality"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        print(f'Task {task_id} failed: {exc}')
        # Log to monitoring service
        # Could add alerting here
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        print(f'Task {task_id} completed successfully')
        # Log to monitoring service
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry"""
        print(f'Task {task_id} retrying: {exc}')
        # Log to monitoring service

# Set base task class
app.Task = BaseTask

# Health check function
@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery functionality"""
    return f'Request: {self.request!r}'

# Connection test
def test_connection():
    """Test Celery broker connection"""
    try:
        inspect = app.control.inspect()
        stats = inspect.stats()
        return bool(stats)
    except Exception as e:
        print(f"Celery connection test failed: {e}")
        return False

if __name__ == '__main__':
    app.start() 