"""
Enterprise MCP Payments - Task Utilities

Shared utilities, decorators, and helper functions for background tasks.
Provides common functionality for error handling, database sessions, monitoring, and async task processing.

Features:
- Async task decorator for Celery
- Database session management for tasks
- Error handling and retry logic
- Task monitoring and metrics
- Shared utility functions
"""

import asyncio
import logging
import functools
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from celery.exceptions import Retry

from app.db.session import async_session_factory
from app.utils.monitoring import log_event, track_performance
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

# Async task decorator for Celery
def async_task(func: Callable) -> Callable:
    """
    Decorator to enable async function support in Celery tasks
    
    Args:
        func: Async function to wrap
        
    Returns:
        Wrapped function that can be used as Celery task
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper function that runs async function in event loop"""
        # Always create a new event loop for Celery tasks to avoid conflicts
        # This is especially important with fork workers where loops can get corrupted
        loop = None
        try:
            # Check if there's an existing loop and if it's closed
            try:
                current_loop = asyncio.get_event_loop()
                if current_loop.is_closed():
                    raise RuntimeError("Current loop is closed")
                loop = current_loop
            except RuntimeError:
                # Create a new event loop for this task
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async function
            return loop.run_until_complete(func(*args, **kwargs))
            
        except Exception as e:
            logger.error(f"Async task {func.__name__} failed: {e}")
            raise
        finally:
            # Only close the loop if we created it and it's not running
            try:
                if loop and not loop.is_running() and not loop.is_closed():
                    # Close the loop we created
                    loop.close()
                    # Clear the event loop from the thread
                    asyncio.set_event_loop(None)
            except Exception as cleanup_error:
                logger.warning(f"Error during event loop cleanup: {cleanup_error}")
    
    return wrapper

# Database session context manager for tasks
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions in tasks
    
    Yields:
        AsyncSession: Database session for task operations
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error in task: {e}")
            raise
        finally:
            await session.close()

# Task error handler
async def handle_task_error(
    task_instance: Any,
    error: Exception,
    context: Dict[str, Any] = None,
    max_retries: int = 3,
    countdown: int = 60
) -> None:
    """
    Handle task errors with retry logic and notification
    
    Args:
        task_instance: Celery task instance
        error: Exception that occurred
        context: Additional context for debugging
        max_retries: Maximum number of retries
        countdown: Seconds to wait before retry
    """
    try:
        # Log error with context
        error_data = {
            'task_name': task_instance.name,
            'task_id': task_instance.request.id,
            'error': str(error),
            'error_type': type(error).__name__,
            'retry_count': task_instance.request.retries,
            'context': context or {}
        }
        
        log_event('task_error', error_data)
        
        # Check if we should retry
        if task_instance.request.retries < max_retries:
            # Calculate exponential backoff
            retry_countdown = countdown * (2 ** task_instance.request.retries)
            
            logger.warning(
                f"Task {task_instance.name} failed, retrying in {retry_countdown}s. "
                f"Attempt {task_instance.request.retries + 1}/{max_retries}. Error: {error}"
            )
            
            # Retry the task
            raise task_instance.retry(countdown=retry_countdown, exc=error)
        else:
            # Max retries reached, send alert
            logger.error(
                f"Task {task_instance.name} failed permanently after {max_retries} retries. "
                f"Error: {error}"
            )
            
            # Send failure notification
            try:
                notification_service = NotificationService()
                await notification_service.send_task_failure_alert(
                    task_instance.name,
                    task_instance.request.id,
                    str(error),
                    context
                )
            except Exception as notification_error:
                logger.error(f"Failed to send task failure notification: {notification_error}")
            
            # Log final failure
            log_event('task_failed_permanently', error_data)
            
    except Retry:
        # Re-raise retry exception
        raise
    except Exception as handler_error:
        logger.error(f"Error in task error handler: {handler_error}")

# Task monitoring decorator
def monitor_task(func: Callable) -> Callable:
    """
    Decorator to add monitoring and metrics to tasks
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with monitoring
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        task_name = func.__name__
        start_time = datetime.utcnow()
        
        # Log task start
        log_event('task_started', {
            'task_name': task_name,
            'start_time': start_time.isoformat(),
            'args_count': len(args),
            'kwargs_keys': list(kwargs.keys()) if kwargs else []
        })
        
        try:
            # Execute task
            result = await func(*args, **kwargs)
            
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Log task success
            log_event('task_completed', {
                'task_name': task_name,
                'duration_seconds': duration,
                'success': True
            })
            
            return result
            
        except Exception as e:
            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            # Log task failure
            log_event('task_failed', {
                'task_name': task_name,
                'duration_seconds': duration,
                'error': str(e),
                'error_type': type(e).__name__,
                'success': False
            })
            
            raise
    
    return wrapper

# Data serialization utilities
def serialize_task_data(data: Any) -> str:
    """
    Serialize data for task storage/transmission
    
    Args:
        data: Data to serialize
        
    Returns:
        JSON string of serialized data
    """
    try:
        return json.dumps(data, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Data serialization failed: {e}")
        return json.dumps({'error': 'serialization_failed', 'original_error': str(e)})

def deserialize_task_data(data_str: str) -> Any:
    """
    Deserialize data from task storage/transmission
    
    Args:
        data_str: JSON string to deserialize
        
    Returns:
        Deserialized data
    """
    try:
        return json.loads(data_str)
    except Exception as e:
        logger.error(f"Data deserialization failed: {e}")
        return {'error': 'deserialization_failed', 'original_error': str(e)}

# Task result utilities
def create_task_result(
    success: bool,
    data: Dict[str, Any] = None,
    error: str = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create standardized task result format
    
    Args:
        success: Whether task completed successfully
        data: Task result data
        error: Error message if failed
        metadata: Additional metadata
        
    Returns:
        Standardized task result dictionary
    """
    result = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data or {},
        'metadata': metadata or {}
    }
    
    if error:
        result['error'] = error
    
    return result

# Batch processing utilities
async def process_batch(
    items: list,
    processor: Callable,
    batch_size: int = 100,
    max_concurrent: int = 10
) -> Dict[str, Any]:
    """
    Process items in batches with concurrency control
    
    Args:
        items: List of items to process
        processor: Async function to process each item
        batch_size: Number of items per batch
        max_concurrent: Maximum concurrent operations
        
    Returns:
        Dict with processing results
    """
    results = {
        'total_items': len(items),
        'processed': 0,
        'failed': 0,
        'batches': 0,
        'errors': []
    }
    
    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_item_with_semaphore(item):
        async with semaphore:
            try:
                result = await processor(item)
                results['processed'] += 1
                return result
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'item': str(item),
                    'error': str(e)
                })
                logger.error(f"Batch item processing failed: {e}")
                return None
    
    # Process items in batches
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        results['batches'] += 1
        
        # Process batch concurrently
        batch_tasks = [process_item_with_semaphore(item) for item in batch]
        await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Log batch progress
        logger.info(f"Processed batch {results['batches']}, items: {len(batch)}")
    
    return results

# Cache utilities for tasks
class TaskCache:
    """Simple cache for task data using Redis"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached data"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(f"task_cache:{key}")
            return deserialize_task_data(data) if data else None
        except Exception as e:
            logger.error(f"Cache get failed for {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set cached data with TTL"""
        if not self.redis_client:
            return False
        
        try:
            data = serialize_task_data(value)
            await self.redis_client.setex(f"task_cache:{key}", ttl, data)
            return True
        except Exception as e:
            logger.error(f"Cache set failed for {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached data"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(f"task_cache:{key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete failed for {key}: {e}")
            return False

# Task scheduling utilities
def schedule_delayed_task(task_func: Callable, delay_seconds: int, *args, **kwargs):
    """
    Schedule a task to run after a delay
    
    Args:
        task_func: Celery task function
        delay_seconds: Delay in seconds
        args: Task arguments
        kwargs: Task keyword arguments
        
    Returns:
        AsyncResult: Celery task result
    """
    return task_func.apply_async(args=args, kwargs=kwargs, countdown=delay_seconds)

def schedule_periodic_task(task_func: Callable, interval_seconds: int, *args, **kwargs):
    """
    Schedule a task to run periodically (for beat scheduler)
    
    Args:
        task_func: Celery task function
        interval_seconds: Interval in seconds
        args: Task arguments
        kwargs: Task keyword arguments
        
    Returns:
        Task configuration for beat scheduler
    """
    return {
        'task': task_func.name,
        'schedule': interval_seconds,
        'args': args,
        'kwargs': kwargs
    }

# Health check utilities
async def check_task_health() -> Dict[str, Any]:
    """
    Check health of task system
    
    Returns:
        Dict with health status
    """
    from app.tasks.celery_app import app
    
    health = {
        'celery_status': 'unknown',
        'workers_active': 0,
        'queues_status': {},
        'recent_failures': 0,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        # Check Celery status
        inspect = app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            health['celery_status'] = 'healthy'
            health['workers_active'] = len(stats)
            
            # Check queue lengths
            active_queues = inspect.active_queues()
            for worker, queues in (active_queues or {}).items():
                for queue_info in queues:
                    queue_name = queue_info.get('name')
                    if queue_name:
                        health['queues_status'][queue_name] = 'active'
        else:
            health['celery_status'] = 'no_workers'
            
    except Exception as e:
        health['celery_status'] = 'error'
        health['error'] = str(e)
        logger.error(f"Task health check failed: {e}")
    
    return health 