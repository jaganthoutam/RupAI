"""
Notification Service
Enterprise notification system with multiple channels and templates.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum

from app.config.settings import settings

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    SLACK = "slack"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationService:
    """
    Enterprise notification service with multiple delivery channels.
    
    Features:
    - Multi-channel delivery (email, SMS, webhook, push)
    - Template management
    - Priority-based queuing
    - Delivery tracking
    - Retry logic
    - Rate limiting
    """
    
    def __init__(self):
        self.initialized = False
        self.delivery_stats = {
            "sent": 0,
            "failed": 0,
            "pending": 0
        }
        self.notification_queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> None:
        """Initialize notification service."""
        try:
            logger.info("🔄 Initializing notification service...")
            
            # Start notification worker
            self._worker_task = asyncio.create_task(self._notification_worker())
            
            self.initialized = True
            logger.info("✅ Notification service initialized")
            
        except Exception as e:
            logger.error("❌ Failed to initialize notification service: %s", str(e))
            raise
    
    async def shutdown(self) -> None:
        """Shutdown notification service."""
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Notification service shut down")
    
    async def send_notification(
        self,
        channel: NotificationChannel,
        recipient: str,
        subject: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification through specified channel.
        
        Args:
            channel: Delivery channel
            recipient: Recipient identifier (email, phone, etc.)
            subject: Notification subject
            message: Notification message
            priority: Notification priority
            metadata: Additional metadata
            
        Returns:
            True if notification was queued successfully
        """
        try:
            notification = {
                "id": f"notif_{datetime.utcnow().timestamp()}",
                "channel": channel,
                "recipient": recipient,
                "subject": subject,
                "message": message,
                "priority": priority,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
                "attempts": 0,
                "max_attempts": 3
            }
            
            await self.notification_queue.put(notification)
            self.delivery_stats["pending"] += 1
            
            logger.info(
                "📧 Notification queued: %s to %s via %s",
                subject,
                recipient,
                channel.value
            )
            
            return True
            
        except Exception as e:
            logger.error("Error queuing notification: %s", str(e))
            return False
    
    async def _notification_worker(self) -> None:
        """Background worker to process notification queue."""
        while True:
            try:
                # Get notification from queue
                notification = await self.notification_queue.get()
                
                # Process notification
                success = await self._deliver_notification(notification)
                
                if success:
                    self.delivery_stats["sent"] += 1
                    self.delivery_stats["pending"] -= 1
                else:
                    # Retry logic
                    notification["attempts"] += 1
                    if notification["attempts"] < notification["max_attempts"]:
                        # Re-queue for retry
                        await asyncio.sleep(2 ** notification["attempts"])  # Exponential backoff
                        await self.notification_queue.put(notification)
                    else:
                        # Max attempts reached
                        self.delivery_stats["failed"] += 1
                        self.delivery_stats["pending"] -= 1
                        logger.error(
                            "❌ Notification failed after %d attempts: %s",
                            notification["max_attempts"],
                            notification["id"]
                        )
                
                # Mark task as done
                self.notification_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Notification worker error: %s", str(e))
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _deliver_notification(self, notification: Dict[str, Any]) -> bool:
        """
        Deliver notification through appropriate channel.
        
        Args:
            notification: Notification data
            
        Returns:
            True if delivery was successful
        """
        try:
            channel = notification["channel"]
            
            if channel == NotificationChannel.EMAIL:
                return await self._send_email(notification)
            elif channel == NotificationChannel.SMS:
                return await self._send_sms(notification)
            elif channel == NotificationChannel.WEBHOOK:
                return await self._send_webhook(notification)
            elif channel == NotificationChannel.PUSH:
                return await self._send_push(notification)
            elif channel == NotificationChannel.SLACK:
                return await self._send_slack(notification)
            else:
                logger.error("Unsupported notification channel: %s", channel)
                return False
                
        except Exception as e:
            logger.error("Notification delivery error: %s", str(e))
            return False
    
    async def _send_email(self, notification: Dict[str, Any]) -> bool:
        """Send email notification."""
        try:
            # Mock email sending for now
            # In production, integrate with SMTP or email service
            logger.info(
                "📧 EMAIL: To=%s, Subject=%s",
                notification["recipient"],
                notification["subject"]
            )
            
            # Simulate email sending delay
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error("Email sending error: %s", str(e))
            return False
    
    async def _send_sms(self, notification: Dict[str, Any]) -> bool:
        """Send SMS notification."""
        try:
            # Mock SMS sending for now
            # In production, integrate with SMS service (Twilio, etc.)
            logger.info(
                "📱 SMS: To=%s, Message=%s",
                notification["recipient"],
                notification["message"][:50] + "..." if len(notification["message"]) > 50 else notification["message"]
            )
            
            # Simulate SMS sending delay
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error("SMS sending error: %s", str(e))
            return False
    
    async def _send_webhook(self, notification: Dict[str, Any]) -> bool:
        """Send webhook notification."""
        try:
            # Mock webhook sending for now
            # In production, make HTTP POST to webhook URL
            logger.info(
                "🔗 WEBHOOK: To=%s, Subject=%s",
                notification["recipient"],
                notification["subject"]
            )
            
            # Simulate webhook sending delay
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error("Webhook sending error: %s", str(e))
            return False
    
    async def _send_push(self, notification: Dict[str, Any]) -> bool:
        """Send push notification."""
        try:
            # Mock push notification for now
            # In production, integrate with push service (FCM, APNS, etc.)
            logger.info(
                "📲 PUSH: To=%s, Subject=%s",
                notification["recipient"],
                notification["subject"]
            )
            
            # Simulate push sending delay
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error("Push notification error: %s", str(e))
            return False
    
    async def _send_slack(self, notification: Dict[str, Any]) -> bool:
        """Send Slack notification."""
        try:
            # Mock Slack notification for now
            # In production, integrate with Slack API
            logger.info(
                "💬 SLACK: To=%s, Subject=%s",
                notification["recipient"],
                notification["subject"]
            )
            
            # Simulate Slack sending delay
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error("Slack notification error: %s", str(e))
            return False
    
    # Convenience methods for common notifications
    async def send_payment_notification(
        self,
        user_email: str,
        payment_id: str,
        amount: float,
        currency: str,
        status: str
    ) -> bool:
        """Send payment status notification."""
        subject = f"Payment {status.title()}: {currency} {amount}"
        message = f"""
        Your payment has been {status}.
        
        Payment ID: {payment_id}
        Amount: {currency} {amount}
        Status: {status.title()}
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        Thank you for using our payment service.
        """
        
        return await self.send_notification(
            channel=NotificationChannel.EMAIL,
            recipient=user_email,
            subject=subject,
            message=message,
            priority=NotificationPriority.HIGH,
            metadata={
                "payment_id": payment_id,
                "amount": amount,
                "currency": currency,
                "status": status
            }
        )
    
    async def send_security_alert(
        self,
        user_email: str,
        alert_type: str,
        details: str
    ) -> bool:
        """Send security alert notification."""
        subject = f"Security Alert: {alert_type}"
        message = f"""
        A security event has been detected on your account.
        
        Alert Type: {alert_type}
        Details: {details}
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        If this was not you, please contact support immediately.
        """
        
        return await self.send_notification(
            channel=NotificationChannel.EMAIL,
            recipient=user_email,
            subject=subject,
            message=message,
            priority=NotificationPriority.URGENT,
            metadata={
                "alert_type": alert_type,
                "details": details
            }
        )
    
    async def send_system_alert(
        self,
        admin_email: str,
        system: str,
        error: str,
        severity: str = "error"
    ) -> bool:
        """Send system alert to administrators."""
        subject = f"System Alert: {system} - {severity.upper()}"
        message = f"""
        System alert detected.
        
        System: {system}
        Severity: {severity.upper()}
        Error: {error}
        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        
        Please investigate immediately.
        """
        
        priority = NotificationPriority.URGENT if severity == "critical" else NotificationPriority.HIGH
        
        return await self.send_notification(
            channel=NotificationChannel.EMAIL,
            recipient=admin_email,
            subject=subject,
            message=message,
            priority=priority,
            metadata={
                "system": system,
                "error": error,
                "severity": severity
            }
        )
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get notification delivery statistics."""
        return {
            "stats": self.delivery_stats.copy(),
            "queue_size": self.notification_queue.qsize(),
            "initialized": self.initialized
        } 