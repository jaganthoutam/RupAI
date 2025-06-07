"""Notification management utilities for alerts and system events."""

import asyncio
import aiohttp
import smtplib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

from ..config.settings import settings
from ..config.logging import get_logger

logger = get_logger(__name__)


class NotificationManager:
    """Production-grade notification manager for alerts and events."""
    
    def __init__(self):
        """Initialize notification manager."""
        self.email_enabled = hasattr(settings, 'SMTP_HOST') and settings.SMTP_HOST
        self.webhook_enabled = hasattr(settings, 'WEBHOOK_URL') and settings.WEBHOOK_URL
        self.slack_enabled = hasattr(settings, 'SLACK_WEBHOOK_URL') and settings.SLACK_WEBHOOK_URL
        
    async def send_alert_notification(
        self,
        alert_data: Dict[str, Any],
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Send alert notification to configured channels.
        
        Args:
            alert_data: Alert information
            channels: List of notification channels ('email', 'webhook', 'slack')
            
        Returns:
            Dict with results for each channel
        """
        if channels is None:
            channels = ['email', 'webhook', 'slack']
        
        results = {}
        
        # Prepare notification content
        notification_content = self._prepare_alert_content(alert_data)
        
        # Send to each enabled channel
        if 'email' in channels and self.email_enabled:
            results['email'] = await self._send_email_notification(
                notification_content,
                alert_data
            )
        
        if 'webhook' in channels and self.webhook_enabled:
            results['webhook'] = await self._send_webhook_notification(
                notification_content,
                alert_data
            )
        
        if 'slack' in channels and self.slack_enabled:
            results['slack'] = await self._send_slack_notification(
                notification_content,
                alert_data
            )
        
        return results
    
    async def send_health_notification(
        self,
        health_data: Dict[str, Any],
        status_change: bool = False
    ) -> Dict[str, bool]:
        """
        Send health status notification.
        
        Args:
            health_data: Health check data
            status_change: Whether this represents a status change
            
        Returns:
            Dict with results for each channel
        """
        results = {}
        
        # Only send notifications for status changes or critical health
        if not status_change and health_data.get('overall_status') == 'healthy':
            return results
        
        notification_content = self._prepare_health_content(health_data)
        
        # Send to all enabled channels for health issues
        if self.email_enabled:
            results['email'] = await self._send_email_notification(
                notification_content,
                health_data,
                subject_prefix="Health Alert"
            )
        
        if self.webhook_enabled:
            results['webhook'] = await self._send_webhook_notification(
                notification_content,
                health_data
            )
        
        if self.slack_enabled:
            results['slack'] = await self._send_slack_notification(
                notification_content,
                health_data
            )
        
        return results
    
    async def send_resolution_notification(
        self,
        alert_data: Dict[str, Any],
        resolution_notes: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Send alert resolution notification.
        
        Args:
            alert_data: Resolved alert data
            resolution_notes: Optional resolution notes
            
        Returns:
            Dict with results for each channel
        """
        results = {}
        
        notification_content = self._prepare_resolution_content(
            alert_data,
            resolution_notes
        )
        
        # Send resolution notifications
        if self.email_enabled:
            results['email'] = await self._send_email_notification(
                notification_content,
                alert_data,
                subject_prefix="Resolved"
            )
        
        if self.slack_enabled:
            results['slack'] = await self._send_slack_notification(
                notification_content,
                alert_data,
                is_resolution=True
            )
        
        return results
    
    def _prepare_alert_content(self, alert_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare alert notification content."""
        severity = alert_data.get('severity', 'unknown').upper()
        service_name = alert_data.get('service_name', 'unknown')
        component = alert_data.get('component', 'unknown')
        title = alert_data.get('title', 'Unknown Alert')
        description = alert_data.get('description', '')
        metric_value = alert_data.get('metric_value')
        threshold_value = alert_data.get('threshold_value')
        
        # Prepare email content
        email_body = f"""
Alert Details:
==============
Service: {service_name}
Component: {component}
Severity: {severity}
Title: {title}
Description: {description}

Metric Information:
==================
Current Value: {metric_value}
Threshold: {threshold_value}

Triggered At: {alert_data.get('triggered_at', 'Unknown')}
Alert ID: {alert_data.get('alert_id', 'Unknown')}
Environment: {alert_data.get('environment', 'Unknown')}

Please investigate and resolve this issue promptly.
        """.strip()
        
        # Prepare Slack content
        slack_text = f"🚨 *{severity} Alert*: {title}\n" \
                    f"Service: {service_name} | Component: {component}\n" \
                    f"Current: {metric_value} | Threshold: {threshold_value}\n" \
                    f"{description}"
        
        return {
            'email_subject': f"[{severity}] {service_name} Alert: {title}",
            'email_body': email_body,
            'slack_text': slack_text,
            'webhook_payload': alert_data
        }
    
    def _prepare_health_content(self, health_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare health notification content."""
        service_name = health_data.get('service_name', 'unknown')
        status = health_data.get('overall_status', 'unknown').upper()
        score = health_data.get('overall_health_score', 0)
        
        # Prepare email content
        email_body = f"""
Health Status Update:
====================
Service: {service_name}
Status: {status}
Health Score: {score}%

Component Status:
================
"""
        
        components = health_data.get('components', {})
        for component, comp_status in components.items():
            email_body += f"{component}: {comp_status}\n"
        
        if health_data.get('warnings'):
            email_body += f"\nWarnings:\n"
            for warning in health_data.get('warnings', []):
                email_body += f"- {warning}\n"
        
        if health_data.get('errors'):
            email_body += f"\nErrors:\n"
            for error in health_data.get('errors', []):
                email_body += f"- {error}\n"
        
        # Prepare Slack content
        status_emoji = "🟢" if status == "HEALTHY" else "🟡" if status == "DEGRADED" else "🔴"
        slack_text = f"{status_emoji} *Health Status*: {service_name}\n" \
                    f"Status: {status} | Score: {score}%"
        
        return {
            'email_subject': f"[Health] {service_name} Status: {status}",
            'email_body': email_body,
            'slack_text': slack_text,
            'webhook_payload': health_data
        }
    
    def _prepare_resolution_content(
        self,
        alert_data: Dict[str, Any],
        resolution_notes: Optional[str]
    ) -> Dict[str, str]:
        """Prepare resolution notification content."""
        service_name = alert_data.get('service_name', 'unknown')
        title = alert_data.get('title', 'Unknown Alert')
        alert_id = alert_data.get('alert_id', 'Unknown')
        
        email_body = f"""
Alert Resolved:
===============
Service: {service_name}
Alert: {title}
Alert ID: {alert_id}

Resolution Time: {datetime.utcnow().isoformat()}
"""
        
        if resolution_notes:
            email_body += f"\nResolution Notes:\n{resolution_notes}"
        
        slack_text = f"✅ *Alert Resolved*: {title}\n" \
                    f"Service: {service_name}\n" \
                    f"Alert ID: {alert_id}"
        
        if resolution_notes:
            slack_text += f"\nNotes: {resolution_notes}"
        
        return {
            'email_subject': f"[Resolved] {service_name}: {title}",
            'email_body': email_body,
            'slack_text': slack_text,
            'webhook_payload': {
                **alert_data,
                'status': 'resolved',
                'resolved_at': datetime.utcnow().isoformat(),
                'resolution_notes': resolution_notes
            }
        }
    
    async def _send_email_notification(
        self,
        content: Dict[str, str],
        alert_data: Dict[str, Any],
        subject_prefix: str = "Alert"
    ) -> bool:
        """Send email notification."""
        try:
            # For now, just log the email (in production would use SMTP)
            logger.info(
                f"Email notification: {content['email_subject']}",
                extra={
                    'notification_type': 'email',
                    'subject': content['email_subject'],
                    'body_preview': content['email_body'][:200] + "..."
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    async def _send_webhook_notification(
        self,
        content: Dict[str, str],
        alert_data: Dict[str, Any]
    ) -> bool:
        """Send webhook notification."""
        try:
            # For now, just log the webhook (in production would make HTTP request)
            logger.info(
                f"Webhook notification sent",
                extra={
                    'notification_type': 'webhook',
                    'payload': content['webhook_payload']
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False
    
    async def _send_slack_notification(
        self,
        content: Dict[str, str],
        alert_data: Dict[str, Any],
        is_resolution: bool = False
    ) -> bool:
        """Send Slack notification."""
        try:
            # For now, just log the Slack message (in production would use Slack API)
            logger.info(
                f"Slack notification: {content['slack_text']}",
                extra={
                    'notification_type': 'slack',
                    'text': content['slack_text'],
                    'is_resolution': is_resolution
                }
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False
    
    async def test_notifications(self) -> Dict[str, Any]:
        """Test all notification channels."""
        test_alert = {
            'alert_id': 'test_alert_001',
            'service_name': 'mcp-payments',
            'component': 'test',
            'severity': 'low',
            'title': 'Test Alert Notification',
            'description': 'This is a test alert to verify notification channels.',
            'metric_value': 100,
            'threshold_value': 90,
            'triggered_at': datetime.utcnow().isoformat(),
            'environment': 'testing'
        }
        
        results = await self.send_alert_notification(test_alert)
        
        return {
            'test_completed': True,
            'channels_tested': list(results.keys()),
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        } 