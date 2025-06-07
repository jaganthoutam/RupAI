"""
Enterprise MCP Payments - Notification Background Tasks

Background tasks for multi-channel notifications, email processing, and messaging.
Handles async notification delivery with retry logic and delivery tracking.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.tasks.celery_app import app
from app.tasks.utils import async_task, get_db_session, handle_task_error, process_batch
from app.services.notification_service import NotificationService
from app.utils.monitoring import track_performance, log_event

logger = logging.getLogger(__name__)

@app.task(bind=True, name='app.tasks.notification_tasks.send_notification')
@async_task
@track_performance
async def send_notification(
    self,
    notification_type: str,
    recipient: str,
    subject: str,
    message: str,
    channel: str = 'email',
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Send individual notification through specified channel"""
    try:
        async with get_db_session() as session:
            notification_service = NotificationService()
            
            # Send notification
            result = await notification_service.send_notification(
                notification_type=notification_type,
                recipient=recipient,
                subject=subject,
                message=message,
                channel=channel,
                metadata=metadata or {}
            )
            
            log_event('notification_sent', {
                'type': notification_type,
                'channel': channel,
                'success': result.get('success', False),
                'recipient_hash': hash(recipient) % 10000  # Hash for privacy
            })
            
            return result
            
    except Exception as e:
        logger.error(f"Notification sending failed: {e}")
        await handle_task_error(self, e, {
            'notification_type': notification_type,
            'channel': channel
        })
        raise

@app.task(bind=True, name='app.tasks.notification_tasks.process_notification_queue')
@async_task
@track_performance
async def process_notification_queue(self) -> Dict[str, Any]:
    """Process pending notifications in the queue"""
    try:
        async with get_db_session() as session:
            notification_service = NotificationService()
            
            # Get pending notifications
            pending_notifications = await notification_service.get_pending_notifications()
            
            # Process notifications in batches
            async def process_single_notification(notification):
                return await notification_service.process_notification(notification)
            
            results = await process_batch(
                items=pending_notifications,
                processor=process_single_notification,
                batch_size=50,
                max_concurrent=10
            )
            
            processing_results = {
                'total_notifications': len(pending_notifications),
                'processed': results['processed'],
                'failed': results['failed'],
                'errors': results['errors'],
                'processing_timestamp': datetime.utcnow().isoformat()
            }
            
            log_event('notification_queue_processed', {
                'total_notifications': len(pending_notifications),
                'processed': results['processed'],
                'failed': results['failed']
            })
            
            return processing_results
            
    except Exception as e:
        logger.error(f"Notification queue processing failed: {e}")
        await handle_task_error(self, e, {})
        raise

@app.task(bind=True, name='app.tasks.notification_tasks.send_bulk_notifications')
@async_task
@track_performance
async def send_bulk_notifications(
    self,
    notification_type: str,
    recipients: List[str],
    subject: str,
    message: str,
    channel: str = 'email'
) -> Dict[str, Any]:
    """Send notifications to multiple recipients"""
    try:
        async with get_db_session() as session:
            notification_service = NotificationService()
            
            # Process bulk notifications
            async def send_to_recipient(recipient):
                return await notification_service.send_notification(
                    notification_type=notification_type,
                    recipient=recipient,
                    subject=subject,
                    message=message,
                    channel=channel
                )
            
            results = await process_batch(
                items=recipients,
                processor=send_to_recipient,
                batch_size=100,
                max_concurrent=20
            )
            
            bulk_results = {
                'notification_type': notification_type,
                'channel': channel,
                'total_recipients': len(recipients),
                'sent': results['processed'],
                'failed': results['failed'],
                'errors': results['errors'],
                'sent_timestamp': datetime.utcnow().isoformat()
            }
            
            log_event('bulk_notifications_sent', {
                'type': notification_type,
                'channel': channel,
                'total_recipients': len(recipients),
                'sent': results['processed'],
                'failed': results['failed']
            })
            
            return bulk_results
            
    except Exception as e:
        logger.error(f"Bulk notification sending failed: {e}")
        await handle_task_error(self, e, {
            'notification_type': notification_type,
            'channel': channel,
            'recipient_count': len(recipients)
        })
        raise

@app.task(bind=True, name='app.tasks.notification_tasks.retry_failed_notifications')
@async_task
@track_performance
async def retry_failed_notifications(self) -> Dict[str, Any]:
    """Retry failed notifications with exponential backoff"""
    try:
        async with get_db_session() as session:
            notification_service = NotificationService()
            
            # Get failed notifications eligible for retry
            failed_notifications = await notification_service.get_failed_notifications_for_retry()
            
            retry_results = {
                'total_failed': len(failed_notifications),
                'retry_attempted': 0,
                'retry_successful': 0,
                'retry_failed': 0,
                'permanently_failed': 0
            }
            
            for notification in failed_notifications:
                try:
                    # Check retry limit
                    if notification.retry_count >= 3:
                        await notification_service.mark_notification_permanently_failed(notification.id)
                        retry_results['permanently_failed'] += 1
                        continue
                    
                    # Attempt retry
                    retry_results['retry_attempted'] += 1
                    retry_result = await notification_service.retry_notification(notification.id)
                    
                    if retry_result['success']:
                        retry_results['retry_successful'] += 1
                    else:
                        retry_results['retry_failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Notification retry error for {notification.id}: {e}")
                    retry_results['retry_failed'] += 1
            
            log_event('failed_notifications_retried', {
                'total_failed': len(failed_notifications),
                'retry_successful': retry_results['retry_successful'],
                'permanently_failed': retry_results['permanently_failed']
            })
            
            return retry_results
            
    except Exception as e:
        logger.error(f"Failed notification retry failed: {e}")
        await handle_task_error(self, e, {})
        raise

@app.task(bind=True, name='app.tasks.notification_tasks.cleanup_old_notifications')
@async_task
@track_performance
async def cleanup_old_notifications(self, retention_days: int = 30) -> Dict[str, Any]:
    """Clean up old notification records"""
    try:
        async with get_db_session() as session:
            notification_service = NotificationService()
            
            # Clean up notifications older than retention period
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            cleanup_result = await notification_service.cleanup_old_notifications(cutoff_date)
            
            cleanup_results = {
                'retention_days': retention_days,
                'cutoff_date': cutoff_date.strftime('%Y-%m-%d'),
                'notifications_deleted': cleanup_result.get('deleted_count', 0),
                'size_freed_mb': cleanup_result.get('size_freed_mb', 0),
                'cleanup_timestamp': datetime.utcnow().isoformat()
            }
            
            log_event('old_notifications_cleaned', {
                'retention_days': retention_days,
                'notifications_deleted': cleanup_result.get('deleted_count', 0)
            })
            
            return cleanup_results
            
    except Exception as e:
        logger.error(f"Notification cleanup failed: {e}")
        await handle_task_error(self, e, {'retention_days': retention_days})
        raise

@app.task(bind=True, name='app.tasks.notification_tasks.generate_notification_analytics')
@async_task
@track_performance
async def generate_notification_analytics(self, period_days: int = 7) -> Dict[str, Any]:
    """Generate notification delivery analytics"""
    try:
        async with get_db_session() as session:
            notification_service = NotificationService()
            
            # Generate analytics for specified period
            start_date = datetime.utcnow() - timedelta(days=period_days)
            analytics = await notification_service.generate_notification_analytics(
                start_date, datetime.utcnow()
            )
            
            analytics_results = {
                'period_days': period_days,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': datetime.utcnow().strftime('%Y-%m-%d'),
                'total_sent': analytics.get('total_sent', 0),
                'delivery_rate': analytics.get('delivery_rate', 0),
                'channel_breakdown': analytics.get('channel_breakdown', {}),
                'type_breakdown': analytics.get('type_breakdown', {}),
                'failure_reasons': analytics.get('failure_reasons', {}),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            log_event('notification_analytics_generated', {
                'period_days': period_days,
                'total_sent': analytics.get('total_sent', 0),
                'delivery_rate': analytics.get('delivery_rate', 0)
            })
            
            return analytics_results
            
    except Exception as e:
        logger.error(f"Notification analytics generation failed: {e}")
        await handle_task_error(self, e, {'period_days': period_days})
        raise 