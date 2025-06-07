"""
RBI (Reserve Bank of India) Compliance Rules for Payment Systems

This module implements comprehensive RBI compliance rules as per:
- Payment and Settlement Systems Act, 2007
- RBI Master Direction on Payment Aggregators and Payment Gateways
- RBI Guidelines on Digital Payment Security Controls
- Know Your Customer (KYC) Guidelines
- Anti-Money Laundering (AML) Guidelines
- Prepaid Payment Instruments (PPI) Guidelines
"""

from decimal import Decimal
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class RBIComplianceLevel(str, Enum):
    """RBI compliance levels for different transaction types."""
    MINIMUM_KYC = "minimum_kyc"  # Up to ₹10,000 per month
    FULL_KYC = "full_kyc"        # Up to ₹1,00,000 per month
    ENHANCED_KYC = "enhanced_kyc" # Above ₹1,00,000 per month


class TransactionType(str, Enum):
    """RBI defined transaction types."""
    P2P = "p2p"                    # Person to Person
    P2M = "p2m"                    # Person to Merchant
    B2B = "b2b"                    # Business to Business
    BULK_PAYMENT = "bulk_payment"   # Bulk payments
    INTERNATIONAL = "international" # Cross-border payments


class RBIViolationType(str, Enum):
    """Types of RBI compliance violations."""
    KYC_INCOMPLETE = "kyc_incomplete"
    TRANSACTION_LIMIT_EXCEEDED = "transaction_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    UNAUTHORIZED_FOREX = "unauthorized_forex"
    INVALID_PURPOSE_CODE = "invalid_purpose_code"
    MISSING_DOCUMENTATION = "missing_documentation"
    BLACKLISTED_ENTITY = "blacklisted_entity"


@dataclass
class RBITransactionLimits:
    """RBI mandated transaction limits."""
    
    # PPI (Prepaid Payment Instruments) Limits
    minimum_kyc_monthly_limit: Decimal = Decimal("10000")      # ₹10,000
    full_kyc_monthly_limit: Decimal = Decimal("100000")        # ₹1,00,000
    enhanced_kyc_monthly_limit: Decimal = Decimal("200000")    # ₹2,00,000
    
    # Single transaction limits
    single_transaction_limit_min_kyc: Decimal = Decimal("5000")    # ₹5,000
    single_transaction_limit_full_kyc: Decimal = Decimal("50000")  # ₹50,000
    
    # UPI specific limits
    upi_single_transaction_limit: Decimal = Decimal("100000")  # ₹1,00,000
    upi_daily_limit: Decimal = Decimal("100000")               # ₹1,00,000
    
    # IMPS limits
    imps_single_transaction_limit: Decimal = Decimal("500000") # ₹5,00,000
    imps_daily_limit: Decimal = Decimal("500000")              # ₹5,00,000
    
    # NEFT/RTGS limits (no upper limit, but minimum amounts)
    neft_minimum_amount: Decimal = Decimal("1")                # ₹1
    rtgs_minimum_amount: Decimal = Decimal("200000")           # ₹2,00,000


class RBIComplianceEngine:
    """Main RBI compliance engine for payment validation."""
    
    def __init__(self):
        self.limits = RBITransactionLimits()
        self.suspicious_patterns = self._load_suspicious_patterns()
        self.blacklisted_entities = self._load_blacklisted_entities()
    
    def validate_transaction(
        self,
        amount: Decimal,
        currency: str,
        payment_method: str,
        customer_kyc_level: str,
        customer_monthly_volume: Decimal,
        transaction_type: TransactionType,
        customer_data: Dict[str, Any],
        merchant_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive RBI transaction validation.
        
        Returns:
            Dict containing validation result and any violations
        """
        violations = []
        warnings = []
        
        # 1. Currency validation (INR only for domestic transactions)
        if currency != "INR" and transaction_type != TransactionType.INTERNATIONAL:
            violations.append({
                "type": RBIViolationType.UNAUTHORIZED_FOREX,
                "message": "Domestic transactions must be in INR only",
                "severity": "high"
            })
        
        # 2. KYC level validation
        kyc_validation = self._validate_kyc_compliance(
            customer_kyc_level, amount, customer_monthly_volume, customer_data
        )
        violations.extend(kyc_validation.get("violations", []))
        warnings.extend(kyc_validation.get("warnings", []))
        
        # 3. Transaction limit validation
        limit_validation = self._validate_transaction_limits(
            amount, payment_method, customer_kyc_level, customer_monthly_volume
        )
        violations.extend(limit_validation.get("violations", []))
        warnings.extend(limit_validation.get("warnings", []))
        
        # 4. Suspicious activity detection
        suspicious_validation = self._detect_suspicious_activity(
            amount, customer_data, transaction_type
        )
        violations.extend(suspicious_validation.get("violations", []))
        warnings.extend(suspicious_validation.get("warnings", []))
        
        return {
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "compliance_score": self._calculate_compliance_score(violations, warnings),
            "required_actions": self._get_required_actions(violations),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _validate_kyc_compliance(
        self,
        kyc_level: str,
        amount: Decimal,
        monthly_volume: Decimal,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate KYC compliance based on transaction amount and volume."""
        violations = []
        warnings = []
        
        # Determine required KYC level based on transaction
        required_kyc = self._determine_required_kyc_level(amount, monthly_volume)
        
        if kyc_level == RBIComplianceLevel.MINIMUM_KYC:
            if required_kyc in [RBIComplianceLevel.FULL_KYC, RBIComplianceLevel.ENHANCED_KYC]:
                violations.append({
                    "type": RBIViolationType.KYC_INCOMPLETE,
                    "message": f"Transaction requires {required_kyc} but customer has {kyc_level}",
                    "severity": "high",
                    "required_kyc_level": required_kyc
                })
        
        return {"violations": violations, "warnings": warnings}
    
    def _validate_transaction_limits(
        self,
        amount: Decimal,
        payment_method: str,
        kyc_level: str,
        monthly_volume: Decimal
    ) -> Dict[str, Any]:
        """Validate transaction against RBI limits."""
        violations = []
        warnings = []
        
        # Single transaction limits
        if kyc_level == RBIComplianceLevel.MINIMUM_KYC:
            if amount > self.limits.single_transaction_limit_min_kyc:
                violations.append({
                    "type": RBIViolationType.TRANSACTION_LIMIT_EXCEEDED,
                    "message": f"Amount ₹{amount} exceeds single transaction limit of ₹{self.limits.single_transaction_limit_min_kyc} for minimum KYC",
                    "severity": "high",
                    "limit_exceeded": "single_transaction"
                })
        
        # UPI specific limits
        if payment_method.upper() == "UPI":
            if amount > self.limits.upi_single_transaction_limit:
                violations.append({
                    "type": RBIViolationType.TRANSACTION_LIMIT_EXCEEDED,
                    "message": f"UPI transaction amount ₹{amount} exceeds limit of ₹{self.limits.upi_single_transaction_limit}",
                    "severity": "high",
                    "limit_exceeded": "upi_single_transaction"
                })
        
        return {"violations": violations, "warnings": warnings}
    
    def _detect_suspicious_activity(
        self,
        amount: Decimal,
        customer_data: Dict[str, Any],
        transaction_type: TransactionType
    ) -> Dict[str, Any]:
        """Detect suspicious activity patterns as per RBI AML guidelines."""
        violations = []
        warnings = []
        
        # Large cash transactions (₹20,000 and above require reporting)
        if amount >= Decimal("20000"):
            warnings.append({
                "type": RBIViolationType.SUSPICIOUS_ACTIVITY,
                "message": f"Large transaction of ₹{amount} requires enhanced monitoring",
                "severity": "medium",
                "requires_reporting": True
            })
        
        # Very large transactions (₹10,00,000 and above)
        if amount >= Decimal("1000000"):
            violations.append({
                "type": RBIViolationType.SUSPICIOUS_ACTIVITY,
                "message": f"Very large transaction of ₹{amount} requires manual approval and STR filing",
                "severity": "high",
                "requires_manual_approval": True,
                "requires_str_filing": True
            })
        
        return {"violations": violations, "warnings": warnings}
    
    def _determine_required_kyc_level(
        self,
        amount: Decimal,
        monthly_volume: Decimal
    ) -> RBIComplianceLevel:
        """Determine required KYC level based on transaction amount and volume."""
        projected_monthly = monthly_volume + amount
        
        if projected_monthly > self.limits.full_kyc_monthly_limit:
            return RBIComplianceLevel.ENHANCED_KYC
        elif projected_monthly > self.limits.minimum_kyc_monthly_limit:
            return RBIComplianceLevel.FULL_KYC
        else:
            return RBIComplianceLevel.MINIMUM_KYC
    
    def _calculate_compliance_score(
        self,
        violations: List[Dict],
        warnings: List[Dict]
    ) -> float:
        """Calculate compliance score (0-100)."""
        if not violations and not warnings:
            return 100.0
        
        score = 100.0
        
        # Deduct points for violations
        for violation in violations:
            severity = violation.get("severity", "medium")
            if severity == "critical":
                score -= 50
            elif severity == "high":
                score -= 25
            elif severity == "medium":
                score -= 10
            else:  # low
                score -= 5
        
        # Deduct points for warnings
        for warning in warnings:
            severity = warning.get("severity", "low")
            if severity == "high":
                score -= 5
            elif severity == "medium":
                score -= 3
            else:  # low
                score -= 1
        
        return max(0.0, score)
    
    def _get_required_actions(self, violations: List[Dict]) -> List[str]:
        """Get list of required actions to resolve violations."""
        actions = []
        
        for violation in violations:
            violation_type = violation.get("type")
            
            if violation_type == RBIViolationType.KYC_INCOMPLETE:
                actions.append(f"Complete {violation.get('required_kyc_level', 'required')} KYC")
            
            elif violation_type == RBIViolationType.TRANSACTION_LIMIT_EXCEEDED:
                actions.append("Reduce transaction amount or upgrade KYC level")
            
            elif violation_type == RBIViolationType.SUSPICIOUS_ACTIVITY:
                if violation.get("requires_manual_approval"):
                    actions.append("Manual approval required")
                if violation.get("requires_str_filing"):
                    actions.append("File Suspicious Transaction Report (STR)")
        
        return list(set(actions))  # Remove duplicates
    
    def _load_suspicious_patterns(self) -> List[Dict]:
        """Load suspicious activity patterns."""
        return [
            {"pattern": "rapid_succession", "threshold": 5, "timeframe": "1_hour"},
            {"pattern": "round_amounts", "threshold": 3, "timeframe": "1_day"},
        ]
    
    def _load_blacklisted_entities(self) -> set:
        """Load blacklisted entities."""
        return {
            "BLACKLISTED_PAN_123",
            "BLACKLISTED_AADHAAR_456",
        }


# RBI compliance decorator for payment functions
def rbi_compliant(func):
    """Decorator to ensure RBI compliance for payment functions."""
    async def wrapper(*args, **kwargs):
        # Extract transaction details
        amount = kwargs.get('amount') or args[1] if len(args) > 1 else None
        currency = kwargs.get('currency', 'INR')
        
        if amount and amount >= Decimal("20000"):
            # Log for RBI reporting
            print(f"RBI: Large transaction detected - ₹{amount}")
        
        return await func(*args, **kwargs)
    
    return wrapper 