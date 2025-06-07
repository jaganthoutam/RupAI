"""
Enterprise MCP Payments - Payment Background Tasks

Background tasks for payment processing, verification, reconciliation, and fraud detection.
Integrates with existing payment service and provides async processing capabilities.

Features:
- Async payment verification and status updates
- Payment reconciliation and settlement
- Fraud detection and risk assessment
- Refund processing and validation
- Payment provider webhook handling
- Failed payment retry logic
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal

from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.celery_app import app
from app.tasks.utils import async_task, get_db_session, handle_task_error
from app.services.payment_service import PaymentService
from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService
from app.db.session import get_session
from app.models.payment import Payment, PaymentStatus
from app.utils.monitoring import track_performance, log_event

logger = logging.getLogger(__name__)

# Payment verification task
@app.task(bind=True, name='app.tasks.payment_tasks.verify_payment_status')
@async_task
@track_performance
async def verify_payment_status(self, payment_id: str) -> Dict[str, Any]:
    """
    Verify payment status with provider and update database
    
    Args:
        payment_id: Unique payment identifier
        
    Returns:
        Dict with verification results and updated status
    """
    try:
        async with get_db_session() as session:
            payment_service = PaymentService(session)
            notification_service = NotificationService()
            
            # Get payment from database
            payment = await payment_service.get_payment(payment_id)
            if not payment:
                raise ValueError(f"Payment {payment_id} not found")
            
            # Verify with payment provider
            provider_status = await payment_service.verify_with_provider(
                payment.provider, payment.provider_payment_id
            )
            
            # Update payment status if changed
            if provider_status['status'] != payment.status:
                old_status = payment.status
                await payment_service.update_payment_status(
                    payment_id, provider_status['status']
                )
                
                # Log status change
                log_event('payment_status_changed', {
                    'payment_id': payment_id,
                    'old_status': old_status,
                    'new_status': provider_status['status'],
                    'provider': payment.provider
                })
                
                # Send notification for important status changes
                if provider_status['status'] in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]:
                    await notification_service.send_payment_notification(
                        payment.user_id,
                        payment_id,
                        provider_status['status']
                    )
            
            return {
                'payment_id': payment_id,
                'status': provider_status['status'],
                'updated': provider_status['status'] != payment.status,
                'provider_data': provider_status.get('provider_data', {})
            }
            
    except Exception as e:
        logger.error(f"Payment verification failed for {payment_id}: {e}")
        await handle_task_error(self, e, {'payment_id': payment_id})
        raise

@app.task(bind=True, name='app.tasks.payment_tasks.process_payment_reconciliation')
@async_task
@track_performance  
async def process_payment_reconciliation(self, date: str = None) -> Dict[str, Any]:
    """
    Process payment reconciliation for a specific date
    
    Args:
        date: Date to reconcile (YYYY-MM-DD), defaults to yesterday
        
    Returns:
        Dict with reconciliation results and statistics
    """
    try:
        if not date:
            date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        async with get_db_session() as session:
            payment_service = PaymentService(session)
            analytics_service = AnalyticsService(session)
            
            # Get payments for reconciliation
            payments = await payment_service.get_payments_for_date(date)
            
            reconciliation_results = {
                'date': date,
                'total_payments': len(payments),
                'reconciled': 0,
                'discrepancies': 0,
                'total_amount': Decimal('0'),
                'discrepancy_amount': Decimal('0'),
                'errors': []
            }
            
            for payment in payments:
                try:
                    # Verify payment with provider
                    provider_data = await payment_service.get_provider_transaction(
                        payment.provider, payment.provider_payment_id
                    )
                    
                    # Check for discrepancies
                    if provider_data['amount'] != payment.amount:
                        reconciliation_results['discrepancies'] += 1
                        reconciliation_results['discrepancy_amount'] += abs(
                            provider_data['amount'] - payment.amount
                        )
                        reconciliation_results['errors'].append({
                            'payment_id': payment.id,
                            'type': 'amount_mismatch',
                            'db_amount': float(payment.amount),
                            'provider_amount': float(provider_data['amount'])
                        })
                    else:
                        reconciliation_results['reconciled'] += 1
                    
                    reconciliation_results['total_amount'] += payment.amount
                    
                except Exception as e:
                    reconciliation_results['errors'].append({
                        'payment_id': payment.id,
                        'type': 'verification_error',
                        'error': str(e)
                    })
            
            # Update analytics with reconciliation data
            await analytics_service.update_reconciliation_metrics(reconciliation_results)
            
            log_event('payment_reconciliation_completed', reconciliation_results)
            
            return reconciliation_results
            
    except Exception as e:
        logger.error(f"Payment reconciliation failed for {date}: {e}")
        await handle_task_error(self, e, {'date': date})
        raise

@app.task(bind=True, name='app.tasks.payment_tasks.process_failed_payments')
@async_task
@track_performance
async def process_failed_payments(self) -> Dict[str, Any]:
    """
    Process failed payments and attempt retry if eligible
    
    Returns:
        Dict with retry results and statistics
    """
    try:
        async with get_db_session() as session:
            payment_service = PaymentService(session)
            
            # Get failed payments eligible for retry
            failed_payments = await payment_service.get_failed_payments_for_retry()
            
            retry_results = {
                'total_failed': len(failed_payments),
                'retry_attempted': 0,
                'retry_successful': 0,
                'retry_failed': 0,
                'permanently_failed': 0
            }
            
            for payment in failed_payments:
                try:
                    # Check retry eligibility
                    if payment.retry_count >= 3:
                        # Mark as permanently failed
                        await payment_service.mark_payment_permanently_failed(payment.id)
                        retry_results['permanently_failed'] += 1
                        continue
                    
                    # Attempt retry
                    retry_results['retry_attempted'] += 1
                    retry_result = await payment_service.retry_payment(payment.id)
                    
                    if retry_result['success']:
                        retry_results['retry_successful'] += 1
                        
                        # Schedule verification task
                        verify_payment_status.delay(payment.id)
                    else:
                        retry_results['retry_failed'] += 1
                        
                except Exception as e:
                    logger.error(f"Failed payment retry error for {payment.id}: {e}")
                    retry_results['retry_failed'] += 1
            
            log_event('failed_payments_processed', retry_results)
            
            return retry_results
            
    except Exception as e:
        logger.error(f"Failed payments processing error: {e}")
        await handle_task_error(self, e, {})
        raise

@app.task(bind=True, name='app.tasks.payment_tasks.detect_fraud_patterns')
@async_task
@track_performance
async def detect_fraud_patterns(self, user_id: str = None, hours: int = 24) -> Dict[str, Any]:
    """
    Detect fraud patterns in recent payments
    
    Args:
        user_id: Specific user to analyze, or None for all users
        hours: Number of hours to look back
        
    Returns:
        Dict with fraud detection results
    """
    try:
        async with get_db_session() as session:
            analytics_service = AnalyticsService(session)
            notification_service = NotificationService()
            
            # Get recent payments for analysis
            start_time = datetime.utcnow() - timedelta(hours=hours)
            fraud_analysis = await analytics_service.detect_fraud_patterns(
                user_id=user_id,
                start_time=start_time
            )
            
            fraud_results = {
                'analysis_period': f'{hours} hours',
                'user_id': user_id,
                'high_risk_transactions': len(fraud_analysis.get('high_risk', [])),
                'medium_risk_transactions': len(fraud_analysis.get('medium_risk', [])),
                'patterns_detected': fraud_analysis.get('patterns', []),
                'total_risk_score': fraud_analysis.get('total_risk_score', 0),
                'actions_taken': []
            }
            
            # Process high-risk transactions
            for transaction in fraud_analysis.get('high_risk', []):
                try:
                    # Flag transaction for review
                    await analytics_service.flag_transaction_for_review(
                        transaction['payment_id'],
                        'high_fraud_risk',
                        transaction['risk_factors']
                    )
                    
                    # Send alert notification
                    await notification_service.send_fraud_alert(
                        transaction['payment_id'],
                        transaction['risk_score'],
                        transaction['risk_factors']
                    )
                    
                    fraud_results['actions_taken'].append({
                        'payment_id': transaction['payment_id'],
                        'action': 'flagged_and_alerted'
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing high-risk transaction {transaction.get('payment_id')}: {e}")
            
            log_event('fraud_detection_completed', fraud_results)
            
            return fraud_results
            
    except Exception as e:
        logger.error(f"Fraud detection failed: {e}")
        await handle_task_error(self, e, {'user_id': user_id, 'hours': hours})
        raise

@app.task(bind=True, name='app.tasks.payment_tasks.process_refund_requests')
@async_task
@track_performance
async def process_refund_requests(self) -> Dict[str, Any]:
    """
    Process pending refund requests
    
    Returns:
        Dict with refund processing results
    """
    try:
        async with get_db_session() as session:
            payment_service = PaymentService(session)
            notification_service = NotificationService()
            
            # Get pending refund requests
            pending_refunds = await payment_service.get_pending_refunds()
            
            refund_results = {
                'total_pending': len(pending_refunds),
                'processed': 0,
                'failed': 0,
                'total_amount': Decimal('0')
            }
            
            for refund in pending_refunds:
                try:
                    # Process refund with provider
                    refund_result = await payment_service.process_refund(
                        refund.payment_id,
                        refund.amount,
                        refund.reason
                    )
                    
                    if refund_result['success']:
                        refund_results['processed'] += 1
                        refund_results['total_amount'] += refund.amount
                        
                        # Send confirmation notification
                        await notification_service.send_refund_notification(
                            refund.user_id,
                            refund.payment_id,
                            refund.amount,
                            'completed'
                        )
                    else:
                        refund_results['failed'] += 1
                        
                        # Send failure notification
                        await notification_service.send_refund_notification(
                            refund.user_id,
                            refund.payment_id,
                            refund.amount,
                            'failed'
                        )
                        
                except Exception as e:
                    logger.error(f"Refund processing error for {refund.id}: {e}")
                    refund_results['failed'] += 1
            
            log_event('refund_requests_processed', refund_results)
            
            return refund_results
            
    except Exception as e:
        logger.error(f"Refund processing failed: {e}")
        await handle_task_error(self, e, {})
        raise

@app.task(bind=True, name='app.tasks.payment_tasks.cleanup_expired_payments')
@async_task  
@track_performance
async def cleanup_expired_payments(self) -> Dict[str, Any]:
    """
    Clean up expired pending payments
    
    Returns:
        Dict with cleanup results
    """
    try:
        async with get_db_session() as session:
            payment_service = PaymentService(session)
            
            # Get expired payments
            expiry_time = datetime.utcnow() - timedelta(hours=24)
            expired_payments = await payment_service.get_expired_payments(expiry_time)
            
            cleanup_results = {
                'total_expired': len(expired_payments),
                'cleaned_up': 0,
                'errors': 0
            }
            
            for payment in expired_payments:
                try:
                    # Mark as expired and cleanup
                    await payment_service.mark_payment_expired(payment.id)
                    cleanup_results['cleaned_up'] += 1
                    
                except Exception as e:
                    logger.error(f"Payment cleanup error for {payment.id}: {e}")
                    cleanup_results['errors'] += 1
            
            log_event('expired_payments_cleaned', cleanup_results)
            
            return cleanup_results
            
    except Exception as e:
        logger.error(f"Payment cleanup failed: {e}")
        await handle_task_error(self, e, {})
        raise

# Webhook processing task
@app.task(bind=True, name='app.tasks.payment_tasks.process_webhook')
@async_task
@track_performance
async def process_webhook(self, provider: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process payment provider webhook
    
    Args:
        provider: Payment provider name
        webhook_data: Webhook payload data
        
    Returns:
        Dict with processing results
    """
    try:
        async with get_db_session() as session:
            payment_service = PaymentService(session)
            
            # Validate webhook signature
            is_valid = await payment_service.validate_webhook(provider, webhook_data)
            if not is_valid:
                raise ValueError(f"Invalid webhook signature from {provider}")
            
            # Process webhook based on event type
            event_type = webhook_data.get('type') or webhook_data.get('event_type')
            payment_id = webhook_data.get('payment_id') or webhook_data.get('transaction_id')
            
            webhook_result = await payment_service.process_webhook_event(
                provider, event_type, payment_id, webhook_data
            )
            
            # Schedule verification if needed
            if webhook_result.get('requires_verification'):
                verify_payment_status.delay(payment_id)
            
            log_event('webhook_processed', {
                'provider': provider,
                'event_type': event_type,
                'payment_id': payment_id,
                'result': webhook_result
            })
            
            return webhook_result
            
    except Exception as e:
        logger.error(f"Webhook processing failed for {provider}: {e}")
        await handle_task_error(self, e, {'provider': provider, 'webhook_data': webhook_data})
        raise 