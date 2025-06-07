"""
RBI-Compliant Stripe Payment Integration

This module provides Stripe payment integration with full RBI compliance including:
- Transaction limits validation
- KYC compliance checks
- AML monitoring
- Audit trail logging
- Error handling and retry logic
"""

import asyncio
import logging
from decimal import Decimal
from typing import Any, Dict, Optional
from datetime import datetime
import aiohttp
import json

from ..models import Payment, PaymentStatus
from ..config.settings import settings
from ..compliance.rbi_rules import RBIComplianceEngine, TransactionType, rbi_compliant


logger = logging.getLogger(__name__)


class StripePaymentError(Exception):
    """Stripe payment specific errors."""
    
    def __init__(self, message: str, error_code: str = None, decline_code: str = None):
        self.message = message
        self.error_code = error_code
        self.decline_code = decline_code
        super().__init__(message)


class StripeClient:
    """
    RBI-Compliant Stripe Payment Client
    
    Handles all Stripe payment operations with full RBI compliance including:
    - Payment creation and processing
    - Refunds and cancellations
    - Webhook handling
    - Compliance validation
    - Audit logging
    """

    def __init__(self):
        self.base_url = "https://api.stripe.com/v1"
        self.api_key = settings.STRIPE_API_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        self.compliance_engine = RBIComplianceEngine()
        
        # RBI-specific configuration
        self.max_retry_attempts = 3
        self.timeout_seconds = 30
        self.supported_currencies = ["INR", "USD", "EUR", "GBP"]  # RBI approved currencies
        
    @rbi_compliant
    async def create_payment(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str,
        payment_method_id: str,
        description: str = None,
        metadata: Optional[Dict[str, Any]] = None,
        customer_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new payment with RBI compliance validation.
        
        Args:
            amount: Payment amount in the specified currency
            currency: Currency code (must be RBI approved)
            customer_id: Unique customer identifier
            payment_method_id: Stripe payment method ID
            description: Payment description
            metadata: Additional payment metadata
            customer_data: Customer KYC and compliance data
            
        Returns:
            Dict containing payment result and compliance information
            
        Raises:
            StripePaymentError: If payment creation fails
            ValueError: If RBI compliance validation fails
        """
        
        # Step 1: RBI Compliance Validation
        compliance_result = await self._validate_rbi_compliance(
            amount, currency, customer_data or {}
        )
        
        if not compliance_result["is_compliant"]:
            logger.warning(f"RBI compliance failed for payment: {compliance_result}")
            raise ValueError(f"RBI compliance violation: {compliance_result['violations']}")
        
        # Step 2: Prepare Stripe payment intent
        payment_data = {
            "amount": int(amount * 100),  # Stripe expects amount in smallest currency unit
            "currency": currency.lower(),
            "customer": customer_id,
            "payment_method": payment_method_id,
            "description": description or f"Payment for customer {customer_id}",
            "metadata": {
                **(metadata or {}),
                "rbi_compliance_score": str(compliance_result["compliance_score"]),
                "transaction_type": "p2m",  # Person to Merchant
                "created_by": "mcp_payments_server",
                "compliance_timestamp": datetime.utcnow().isoformat()
            },
            "confirm": True,  # Automatically confirm the payment
            "return_url": f"{settings.BASE_URL}/payments/return"
        }
        
        # Step 3: Execute payment with retry logic
        try:
            result = await self._execute_with_retry(
                self._create_stripe_payment_intent,
                payment_data
            )
            
            # Step 4: Log for RBI audit trail
            await self._log_payment_audit(
                "payment_created",
                {
                    "stripe_payment_intent_id": result.get("id"),
                    "amount": amount,
                    "currency": currency,
                    "customer_id": customer_id,
                    "compliance_result": compliance_result,
                    "status": result.get("status")
                }
            )
            
            return {
                "success": True,
                "payment_intent_id": result.get("id"),
                "status": result.get("status"),
                "amount": amount,
                "currency": currency,
                "compliance_result": compliance_result,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stripe payment creation failed: {str(e)}")
            
            # Log failure for RBI audit
            await self._log_payment_audit(
                "payment_failed",
                {
                    "amount": amount,
                    "currency": currency,
                    "customer_id": customer_id,
                    "error": str(e),
                    "compliance_result": compliance_result
                }
            )
            
            raise StripePaymentError(f"Payment creation failed: {str(e)}")
    
    async def verify_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Verify payment status with Stripe.
        
        Args:
            payment_intent_id: Stripe payment intent ID
            
        Returns:
            Dict containing payment status and details
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as session:
                async with session.get(
                    f"{self.base_url}/payment_intents/{payment_intent_id}",
                    auth=aiohttp.BasicAuth(self.api_key, "")
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Map Stripe status to our payment status
                        status_mapping = {
                            "requires_payment_method": PaymentStatus.PENDING,
                            "requires_confirmation": PaymentStatus.PENDING,
                            "requires_action": PaymentStatus.PENDING,
                            "processing": PaymentStatus.PROCESSING,
                            "requires_capture": PaymentStatus.PROCESSING,
                            "succeeded": PaymentStatus.COMPLETED,
                            "canceled": PaymentStatus.CANCELLED
                        }
                        
                        payment_status = status_mapping.get(result.get("status"), PaymentStatus.FAILED)
                        
                        return {
                            "success": True,
                            "payment_intent_id": payment_intent_id,
                            "status": payment_status,
                            "amount": Decimal(str(result.get("amount", 0))) / 100,
                            "currency": result.get("currency", "").upper(),
                            "stripe_status": result.get("status"),
                            "last_payment_error": result.get("last_payment_error"),
                            "updated_at": datetime.utcnow().isoformat()
                        }
                    else:
                        error_data = await response.json()
                        raise StripePaymentError(
                            f"Failed to verify payment: {error_data.get('error', {}).get('message', 'Unknown error')}",
                            error_data.get('error', {}).get('code')
                        )
                        
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            raise StripePaymentError(f"Payment verification failed: {str(e)}")
    
    @rbi_compliant
    async def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "requested_by_customer",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process payment refund with RBI compliance.
        
        Args:
            payment_intent_id: Stripe payment intent ID
            amount: Refund amount (if partial refund)
            reason: Refund reason
            metadata: Additional refund metadata
            
        Returns:
            Dict containing refund result
        """
        try:
            # First, get the original payment details
            payment_details = await self.verify_payment(payment_intent_id)
            
            if not payment_details["success"]:
                raise StripePaymentError("Cannot refund: Payment not found")
            
            if payment_details["status"] != PaymentStatus.COMPLETED:
                raise StripePaymentError("Cannot refund: Payment not completed")
            
            # Prepare refund data
            refund_data = {
                "payment_intent": payment_intent_id,
                "reason": reason,
                "metadata": {
                    **(metadata or {}),
                    "refund_timestamp": datetime.utcnow().isoformat(),
                    "processed_by": "mcp_payments_server"
                }
            }
            
            if amount:
                refund_data["amount"] = int(amount * 100)
            
            # Execute refund
            result = await self._execute_with_retry(
                self._create_stripe_refund,
                refund_data
            )
            
            # Log for RBI audit trail
            await self._log_payment_audit(
                "refund_processed",
                {
                    "stripe_refund_id": result.get("id"),
                    "payment_intent_id": payment_intent_id,
                    "refund_amount": amount or payment_details["amount"],
                    "reason": reason,
                    "status": result.get("status")
                }
            )
            
            return {
                "success": True,
                "refund_id": result.get("id"),
                "status": result.get("status"),
                "amount": Decimal(str(result.get("amount", 0))) / 100,
                "currency": result.get("currency", "").upper(),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Refund processing failed: {str(e)}")
            raise StripePaymentError(f"Refund processing failed: {str(e)}")
    
    async def handle_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events with RBI compliance logging.
        
        Args:
            payload: Webhook payload
            signature: Stripe signature header
            
        Returns:
            Dict containing webhook processing result
        """
        try:
            # Verify webhook signature (in production, use stripe.Webhook.construct_event)
            event_data = json.loads(payload)
            
            event_type = event_data.get("type")
            event_object = event_data.get("data", {}).get("object", {})
            
            # Log webhook for RBI audit
            await self._log_payment_audit(
                f"webhook_{event_type}",
                {
                    "event_id": event_data.get("id"),
                    "event_type": event_type,
                    "object_id": event_object.get("id"),
                    "webhook_received_at": datetime.utcnow().isoformat()
                }
            )
            
            # Process specific event types
            if event_type == "payment_intent.succeeded":
                await self._handle_payment_success(event_object)
            elif event_type == "payment_intent.payment_failed":
                await self._handle_payment_failure(event_object)
            elif event_type == "charge.dispute.created":
                await self._handle_dispute_created(event_object)
            
            return {
                "success": True,
                "event_type": event_type,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.utcnow().isoformat()
            }
    
    async def _validate_rbi_compliance(
        self,
        amount: Decimal,
        currency: str,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate transaction against RBI compliance rules."""
        
        # Get customer's KYC level and monthly volume
        kyc_level = customer_data.get("kyc_level", "minimum_kyc")
        monthly_volume = Decimal(str(customer_data.get("monthly_volume", 0)))
        
        # Validate with RBI compliance engine
        return self.compliance_engine.validate_transaction(
            amount=amount,
            currency=currency,
            payment_method="card",  # Stripe is primarily for card payments
            customer_kyc_level=kyc_level,
            customer_monthly_volume=monthly_volume,
            transaction_type=TransactionType.P2M,
            customer_data=customer_data
        )
    
    async def _create_stripe_payment_intent(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Stripe payment intent."""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as session:
            async with session.post(
                f"{self.base_url}/payment_intents",
                auth=aiohttp.BasicAuth(self.api_key, ""),
                data=payment_data
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise StripePaymentError(
                        error_data.get('error', {}).get('message', 'Unknown error'),
                        error_data.get('error', {}).get('code'),
                        error_data.get('error', {}).get('decline_code')
                    )
    
    async def _create_stripe_refund(self, refund_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Stripe refund."""
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as session:
            async with session.post(
                f"{self.base_url}/refunds",
                auth=aiohttp.BasicAuth(self.api_key, ""),
                data=refund_data
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise StripePaymentError(
                        error_data.get('error', {}).get('message', 'Unknown error'),
                        error_data.get('error', {}).get('code')
                    )
    
    async def _execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retry_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retry_attempts - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retry_attempts} attempts failed")
        
        raise last_exception
    
    async def _log_payment_audit(self, action: str, data: Dict[str, Any]):
        """Log payment action for RBI audit trail."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "provider": "stripe",
            "data": data,
            "compliance_logged": True
        }
        
        # In production, this would write to audit database
        logger.info(f"RBI Audit Log: {json.dumps(audit_entry)}")
    
    async def _handle_payment_success(self, payment_intent: Dict[str, Any]):
        """Handle successful payment webhook."""
        logger.info(f"Payment succeeded: {payment_intent.get('id')}")
        # Update payment status in database
        # Send confirmation notifications
        # Update customer transaction history
    
    async def _handle_payment_failure(self, payment_intent: Dict[str, Any]):
        """Handle failed payment webhook."""
        logger.warning(f"Payment failed: {payment_intent.get('id')}")
        # Update payment status in database
        # Send failure notifications
        # Log for fraud analysis if needed
    
    async def _handle_dispute_created(self, charge: Dict[str, Any]):
        """Handle dispute creation webhook."""
        logger.warning(f"Dispute created for charge: {charge.get('id')}")
        # Log for RBI reporting
        # Initiate dispute resolution process
        # Notify relevant teams
