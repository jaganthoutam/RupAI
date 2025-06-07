"""
RBI-Compliant Razorpay Payment Integration

This module provides Razorpay payment integration with full RBI compliance including:
- UPI, IMPS, NEFT, RTGS support
- Transaction limits validation
- KYC compliance checks
- AML monitoring
- Audit trail logging
- Indian payment method support
"""

import asyncio
import logging
import hashlib
import hmac
from decimal import Decimal
from typing import Any, Dict, Optional
from datetime import datetime
import aiohttp
import json
import base64

from ..models import Payment, PaymentStatus
from ..config.settings import settings
from ..compliance.rbi_rules import RBIComplianceEngine, TransactionType, rbi_compliant


logger = logging.getLogger(__name__)


class RazorpayPaymentError(Exception):
    """Razorpay payment specific errors."""
    
    def __init__(self, message: str, error_code: str = None, field: str = None):
        self.message = message
        self.error_code = error_code
        self.field = field
        super().__init__(message)


class RazorpayClient:
    """
    RBI-Compliant Razorpay Payment Client
    
    Handles all Razorpay payment operations with full RBI compliance including:
    - UPI payments
    - Net banking (IMPS, NEFT, RTGS)
    - Card payments
    - Wallet payments
    - QR code payments
    - Compliance validation
    - Audit logging
    """

    def __init__(self):
        self.base_url = "https://api.razorpay.com/v1"
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        self.compliance_engine = RBIComplianceEngine()
        
        # RBI-specific configuration
        self.max_retry_attempts = 3
        self.timeout_seconds = 30
        self.supported_currencies = ["INR"]  # Razorpay primarily supports INR
        
        # Indian payment methods supported by Razorpay
        self.indian_payment_methods = {
            "upi": {"limit": Decimal("100000"), "available_24x7": True},
            "netbanking": {"limit": Decimal("1000000"), "available_24x7": False},
            "card": {"limit": Decimal("500000"), "available_24x7": True},
            "wallet": {"limit": Decimal("100000"), "available_24x7": True},
            "emi": {"limit": Decimal("500000"), "available_24x7": True},
            "paylater": {"limit": Decimal("200000"), "available_24x7": True}
        }
        
    @rbi_compliant
    async def create_payment(
        self,
        amount: Decimal,
        currency: str,
        customer_id: str,
        payment_method: str,
        description: str = None,
        metadata: Optional[Dict[str, Any]] = None,
        customer_data: Optional[Dict[str, Any]] = None,
        upi_id: Optional[str] = None,
        bank_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new payment with RBI compliance validation.
        
        Args:
            amount: Payment amount in INR
            currency: Currency code (must be INR for domestic)
            customer_id: Unique customer identifier
            payment_method: Payment method (upi, netbanking, card, wallet)
            description: Payment description
            metadata: Additional payment metadata
            customer_data: Customer KYC and compliance data
            upi_id: UPI ID for UPI payments
            bank_code: Bank code for net banking
            
        Returns:
            Dict containing payment result and compliance information
        """
        
        # Step 1: RBI Compliance Validation
        compliance_result = await self._validate_rbi_compliance(
            amount, currency, payment_method, customer_data or {}
        )
        
        if not compliance_result["is_compliant"]:
            logger.warning(f"RBI compliance failed for payment: {compliance_result}")
            raise ValueError(f"RBI compliance violation: {compliance_result['violations']}")
        
        # Step 2: Validate payment method specific requirements
        method_validation = await self._validate_payment_method_requirements(
            payment_method, amount, upi_id, bank_code
        )
        
        if not method_validation["valid"]:
            raise ValueError(f"Payment method validation failed: {method_validation['error']}")
        
        # Step 3: Create Razorpay order
        order_data = {
            "amount": int(amount * 100),  # Razorpay expects amount in paise
            "currency": currency,
            "receipt": f"order_{customer_id}_{int(datetime.utcnow().timestamp())}",
            "notes": {
                **(metadata or {}),
                "customer_id": customer_id,
                "payment_method": payment_method,
                "rbi_compliance_score": str(compliance_result["compliance_score"]),
                "transaction_type": "p2m",
                "created_by": "mcp_payments_server",
                "compliance_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Add payment method specific data
        if payment_method == "upi" and upi_id:
            order_data["notes"]["upi_id"] = upi_id
        elif payment_method == "netbanking" and bank_code:
            order_data["notes"]["bank_code"] = bank_code
        
        try:
            # Step 4: Create order with Razorpay
            order_result = await self._execute_with_retry(
                self._create_razorpay_order,
                order_data
            )
            
            # Step 5: Log for RBI audit trail
            await self._log_payment_audit(
                "order_created",
                {
                    "razorpay_order_id": order_result.get("id"),
                    "amount": amount,
                    "currency": currency,
                    "customer_id": customer_id,
                    "payment_method": payment_method,
                    "compliance_result": compliance_result,
                    "status": order_result.get("status")
                }
            )
            
            return {
                "success": True,
                "order_id": order_result.get("id"),
                "status": order_result.get("status"),
                "amount": amount,
                "currency": currency,
                "payment_method": payment_method,
                "compliance_result": compliance_result,
                "created_at": datetime.utcnow().isoformat(),
                "razorpay_key_id": self.key_id  # Frontend needs this
            }
            
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            
            # Log failure for RBI audit
            await self._log_payment_audit(
                "order_failed",
                {
                    "amount": amount,
                    "currency": currency,
                    "customer_id": customer_id,
                    "payment_method": payment_method,
                    "error": str(e),
                    "compliance_result": compliance_result
                }
            )
            
            raise RazorpayPaymentError(f"Order creation failed: {str(e)}")
    
    async def verify_payment(self, payment_id: str, order_id: str, signature: str) -> Dict[str, Any]:
        """
        Verify payment signature and status with Razorpay.
        
        Args:
            payment_id: Razorpay payment ID
            order_id: Razorpay order ID
            signature: Payment signature for verification
            
        Returns:
            Dict containing payment verification result
        """
        try:
            # Step 1: Verify payment signature
            signature_valid = self._verify_payment_signature(payment_id, order_id, signature)
            
            if not signature_valid:
                raise RazorpayPaymentError("Invalid payment signature")
            
            # Step 2: Fetch payment details from Razorpay
            payment_details = await self._execute_with_retry(
                self._fetch_payment_details,
                payment_id
            )
            
            # Step 3: Map Razorpay status to our payment status
            status_mapping = {
                "created": PaymentStatus.PENDING,
                "authorized": PaymentStatus.PROCESSING,
                "captured": PaymentStatus.COMPLETED,
                "refunded": PaymentStatus.REFUNDED,
                "failed": PaymentStatus.FAILED
            }
            
            payment_status = status_mapping.get(payment_details.get("status"), PaymentStatus.FAILED)
            
            # Step 4: Log verification for RBI audit
            await self._log_payment_audit(
                "payment_verified",
                {
                    "razorpay_payment_id": payment_id,
                    "razorpay_order_id": order_id,
                    "status": payment_status,
                    "amount": Decimal(str(payment_details.get("amount", 0))) / 100,
                    "method": payment_details.get("method"),
                    "signature_valid": signature_valid
                }
            )
            
            return {
                "success": True,
                "payment_id": payment_id,
                "order_id": order_id,
                "status": payment_status,
                "amount": Decimal(str(payment_details.get("amount", 0))) / 100,
                "currency": payment_details.get("currency", "").upper(),
                "method": payment_details.get("method"),
                "razorpay_status": payment_details.get("status"),
                "bank": payment_details.get("bank"),
                "wallet": payment_details.get("wallet"),
                "vpa": payment_details.get("vpa"),  # UPI VPA
                "verified_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            raise RazorpayPaymentError(f"Payment verification failed: {str(e)}")
    
    @rbi_compliant
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        notes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process payment refund with RBI compliance.
        
        Args:
            payment_id: Razorpay payment ID
            amount: Refund amount (if partial refund)
            notes: Additional refund notes
            
        Returns:
            Dict containing refund result
        """
        try:
            # Step 1: Get payment details
            payment_details = await self._fetch_payment_details(payment_id)
            
            if payment_details.get("status") != "captured":
                raise RazorpayPaymentError("Cannot refund: Payment not captured")
            
            # Step 2: Prepare refund data
            refund_data = {
                "notes": {
                    **(notes or {}),
                    "refund_timestamp": datetime.utcnow().isoformat(),
                    "processed_by": "mcp_payments_server"
                }
            }
            
            if amount:
                refund_data["amount"] = int(amount * 100)  # Convert to paise
            
            # Step 3: Execute refund
            refund_result = await self._execute_with_retry(
                self._create_razorpay_refund,
                payment_id,
                refund_data
            )
            
            # Step 4: Log for RBI audit trail
            await self._log_payment_audit(
                "refund_processed",
                {
                    "razorpay_refund_id": refund_result.get("id"),
                    "razorpay_payment_id": payment_id,
                    "refund_amount": amount or Decimal(str(payment_details.get("amount", 0))) / 100,
                    "status": refund_result.get("status")
                }
            )
            
            return {
                "success": True,
                "refund_id": refund_result.get("id"),
                "payment_id": payment_id,
                "status": refund_result.get("status"),
                "amount": Decimal(str(refund_result.get("amount", 0))) / 100,
                "currency": refund_result.get("currency", "").upper(),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Refund processing failed: {str(e)}")
            raise RazorpayPaymentError(f"Refund processing failed: {str(e)}")
    
    async def handle_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """
        Handle Razorpay webhook events with RBI compliance logging.
        
        Args:
            payload: Webhook payload
            signature: Razorpay signature header
            
        Returns:
            Dict containing webhook processing result
        """
        try:
            # Step 1: Verify webhook signature
            if not self._verify_webhook_signature(payload, signature):
                raise RazorpayPaymentError("Invalid webhook signature")
            
            # Step 2: Parse webhook data
            event_data = json.loads(payload)
            
            event_type = event_data.get("event")
            payment_entity = event_data.get("payload", {}).get("payment", {}).get("entity", {})
            
            # Step 3: Log webhook for RBI audit
            await self._log_payment_audit(
                f"webhook_{event_type}",
                {
                    "event_type": event_type,
                    "payment_id": payment_entity.get("id"),
                    "order_id": payment_entity.get("order_id"),
                    "amount": payment_entity.get("amount"),
                    "status": payment_entity.get("status"),
                    "method": payment_entity.get("method"),
                    "webhook_received_at": datetime.utcnow().isoformat()
                }
            )
            
            # Step 4: Process specific event types
            if event_type == "payment.captured":
                await self._handle_payment_captured(payment_entity)
            elif event_type == "payment.failed":
                await self._handle_payment_failed(payment_entity)
            elif event_type == "refund.created":
                await self._handle_refund_created(payment_entity)
            
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
    
    async def create_upi_qr_code(
        self,
        amount: Decimal,
        customer_id: str,
        description: str = None,
        customer_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create UPI QR code for payment with RBI compliance.
        
        Args:
            amount: Payment amount in INR
            customer_id: Customer identifier
            description: Payment description
            customer_data: Customer KYC data
            
        Returns:
            Dict containing QR code details
        """
        
        # Validate RBI compliance for UPI
        compliance_result = await self._validate_rbi_compliance(
            amount, "INR", "upi", customer_data or {}
        )
        
        if not compliance_result["is_compliant"]:
            raise ValueError(f"RBI compliance violation: {compliance_result['violations']}")
        
        try:
            qr_data = {
                "type": "upi_qr",
                "name": f"Payment for {customer_id}",
                "usage": "single_use",
                "fixed_amount": True,
                "payment_amount": int(amount * 100),
                "description": description or f"Payment for customer {customer_id}",
                "notes": {
                    "customer_id": customer_id,
                    "compliance_score": str(compliance_result["compliance_score"]),
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            
            qr_result = await self._execute_with_retry(
                self._create_razorpay_qr_code,
                qr_data
            )
            
            await self._log_payment_audit(
                "upi_qr_created",
                {
                    "qr_code_id": qr_result.get("id"),
                    "amount": amount,
                    "customer_id": customer_id,
                    "compliance_result": compliance_result
                }
            )
            
            return {
                "success": True,
                "qr_code_id": qr_result.get("id"),
                "qr_code_url": qr_result.get("image_url"),
                "amount": amount,
                "compliance_result": compliance_result,
                "expires_at": qr_result.get("close_by"),
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"UPI QR code creation failed: {str(e)}")
            raise RazorpayPaymentError(f"UPI QR code creation failed: {str(e)}")
    
    async def _validate_rbi_compliance(
        self,
        amount: Decimal,
        currency: str,
        payment_method: str,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate transaction against RBI compliance rules."""
        
        # Get customer's KYC level and monthly volume
        kyc_level = customer_data.get("kyc_level", "minimum_kyc")
        monthly_volume = Decimal(str(customer_data.get("monthly_volume", 0)))
        
        # Determine transaction type based on payment method
        transaction_type = TransactionType.P2M
        if payment_method == "upi":
            transaction_type = TransactionType.P2P  # UPI can be P2P or P2M
        
        # Validate with RBI compliance engine
        return self.compliance_engine.validate_transaction(
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            customer_kyc_level=kyc_level,
            customer_monthly_volume=monthly_volume,
            transaction_type=transaction_type,
            customer_data=customer_data
        )
    
    async def _validate_payment_method_requirements(
        self,
        payment_method: str,
        amount: Decimal,
        upi_id: Optional[str] = None,
        bank_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate payment method specific requirements."""
        
        method_info = self.indian_payment_methods.get(payment_method)
        if not method_info:
            return {"valid": False, "error": f"Unsupported payment method: {payment_method}"}
        
        # Check amount limits
        if amount > method_info["limit"]:
            return {
                "valid": False,
                "error": f"{payment_method.upper()} amount limit exceeded. Max: ₹{method_info['limit']}"
            }
        
        # UPI specific validations
        if payment_method == "upi":
            if upi_id and not self._validate_upi_id(upi_id):
                return {"valid": False, "error": "Invalid UPI ID format"}
        
        # Net banking specific validations
        elif payment_method == "netbanking":
            if bank_code and not self._validate_bank_code(bank_code):
                return {"valid": False, "error": "Invalid bank code"}
            
            # Check if it's business hours for NEFT/RTGS
            current_hour = datetime.now().hour
            if not method_info["available_24x7"] and (current_hour < 9 or current_hour > 17):
                return {
                    "valid": False,
                    "error": "Net banking not available outside business hours"
                }
        
        return {"valid": True}
    
    def _validate_upi_id(self, upi_id: str) -> bool:
        """Validate UPI ID format."""
        # Basic UPI ID validation: should contain @ and valid characters
        import re
        upi_pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$'
        return bool(re.match(upi_pattern, upi_id))
    
    def _validate_bank_code(self, bank_code: str) -> bool:
        """Validate bank code format."""
        # Basic bank code validation
        return len(bank_code) >= 3 and bank_code.isalnum()
    
    def _verify_payment_signature(self, payment_id: str, order_id: str, signature: str) -> bool:
        """Verify Razorpay payment signature."""
        try:
            payload = f"{order_id}|{payment_id}"
            expected_signature = hmac.new(
                self.key_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False
    
    def _verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Razorpay webhook signature."""
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False
    
    async def _create_razorpay_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Razorpay order."""
        auth_header = base64.b64encode(f"{self.key_id}:{self.key_secret}".encode()).decode()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as session:
            async with session.post(
                f"{self.base_url}/orders",
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/json"
                },
                json=order_data
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise RazorpayPaymentError(
                        error_data.get('error', {}).get('description', 'Unknown error'),
                        error_data.get('error', {}).get('code'),
                        error_data.get('error', {}).get('field')
                    )
    
    async def _fetch_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Fetch payment details from Razorpay."""
        auth_header = base64.b64encode(f"{self.key_id}:{self.key_secret}".encode()).decode()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as session:
            async with session.get(
                f"{self.base_url}/payments/{payment_id}",
                headers={"Authorization": f"Basic {auth_header}"}
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise RazorpayPaymentError(
                        error_data.get('error', {}).get('description', 'Unknown error'),
                        error_data.get('error', {}).get('code')
                    )
    
    async def _create_razorpay_refund(self, payment_id: str, refund_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Razorpay refund."""
        auth_header = base64.b64encode(f"{self.key_id}:{self.key_secret}".encode()).decode()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as session:
            async with session.post(
                f"{self.base_url}/payments/{payment_id}/refund",
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/json"
                },
                json=refund_data
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise RazorpayPaymentError(
                        error_data.get('error', {}).get('description', 'Unknown error'),
                        error_data.get('error', {}).get('code')
                    )
    
    async def _create_razorpay_qr_code(self, qr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Razorpay QR code."""
        auth_header = base64.b64encode(f"{self.key_id}:{self.key_secret}".encode()).decode()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_seconds)) as session:
            async with session.post(
                f"{self.base_url}/payments/qr_codes",
                headers={
                    "Authorization": f"Basic {auth_header}",
                    "Content-Type": "application/json"
                },
                json=qr_data
            ) as response:
                
                if response.status == 200:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise RazorpayPaymentError(
                        error_data.get('error', {}).get('description', 'Unknown error'),
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
            "provider": "razorpay",
            "data": data,
            "compliance_logged": True
        }
        
        # In production, this would write to audit database
        logger.info(f"RBI Audit Log: {json.dumps(audit_entry)}")
    
    async def _handle_payment_captured(self, payment_entity: Dict[str, Any]):
        """Handle payment captured webhook."""
        logger.info(f"Payment captured: {payment_entity.get('id')}")
        # Update payment status in database
        # Send confirmation notifications
        # Update customer transaction history
    
    async def _handle_payment_failed(self, payment_entity: Dict[str, Any]):
        """Handle payment failed webhook."""
        logger.warning(f"Payment failed: {payment_entity.get('id')}")
        # Update payment status in database
        # Send failure notifications
        # Log for fraud analysis if needed
    
    async def _handle_refund_created(self, refund_entity: Dict[str, Any]):
        """Handle refund created webhook."""
        logger.info(f"Refund created: {refund_entity.get('id')}")
        # Update refund status in database
        # Send refund notifications
        # Update customer transaction history
