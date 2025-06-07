#!/usr/bin/env python3
"""
Fraud Detection Data Generation Script

This script generates realistic transaction data with various fraud patterns
for testing the MCP Payments fraud detection system.

Run with: python scripts/generate_fraud_data.py --help
"""

import asyncio
import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse
import httpx
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import settings

@dataclass
class Customer:
    """Customer data for fraud testing."""
    id: str
    name: str
    email: str
    phone: str
    country: str
    region: str
    risk_profile: str  # low, medium, high
    account_age_days: int
    kyc_verified: bool
    total_transactions: int
    avg_transaction_amount: float

@dataclass
class Transaction:
    """Transaction data for fraud testing."""
    id: str
    customer_id: str
    amount: float
    currency: str
    payment_method: str
    merchant_id: str
    merchant_category: str
    timestamp: str
    ip_address: str
    device_id: str
    location: Dict[str, Any]
    risk_indicators: List[str]
    is_fraudulent: bool
    fraud_type: Optional[str] = None

class FraudDataGenerator:
    """Generate realistic fraud detection test data."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.customers: List[Customer] = []
        self.transactions: List[Transaction] = []
        
        # Pre-defined data for realistic generation
        self.countries = ["US", "CA", "GB", "DE", "FR", "AU", "IN", "BR", "JP", "CN"]
        self.payment_methods = ["card", "bank_transfer", "wallet", "upi", "crypto"]
        self.merchant_categories = [
            "grocery", "gas_station", "restaurant", "online_retail", "gaming",
            "subscription", "crypto_exchange", "money_transfer", "gambling", "pharmacy"
        ]
        self.fraud_types = [
            "stolen_card", "account_takeover", "synthetic_identity", "money_laundering",
            "merchant_fraud", "refund_fraud", "chargeback_fraud", "velocity_fraud"
        ]

    def generate_customers(self, count: int = 100) -> List[Customer]:
        """Generate realistic customer data."""
        print(f"🔧 Generating {count} customers...")
        
        customers = []
        for i in range(count):
            # Determine risk profile distribution (80% low, 15% medium, 5% high)
            risk_weights = [0.8, 0.15, 0.05]
            risk_profile = random.choices(["low", "medium", "high"], weights=risk_weights)[0]
            
            customer = Customer(
                id=f"cust_{uuid.uuid4().hex[:8]}",
                name=f"Customer {i+1}",
                email=f"customer{i+1}@test{random.randint(1,10)}.com",
                phone=f"+1{random.randint(1000000000, 9999999999)}",
                country=random.choice(self.countries),
                region=random.choice(["North", "South", "East", "West", "Central"]),
                risk_profile=risk_profile,
                account_age_days=random.randint(1, 1095),  # Up to 3 years
                kyc_verified=random.choice([True, True, True, False]),  # 75% verified
                total_transactions=random.randint(0, 500),
                avg_transaction_amount=round(random.uniform(10, 1000), 2)
            )
            customers.append(customer)
        
        self.customers = customers
        print(f"✅ Generated {len(customers)} customers")
        return customers

    def generate_normal_transactions(self, count: int = 1000) -> List[Transaction]:
        """Generate normal (non-fraudulent) transactions."""
        print(f"🔧 Generating {count} normal transactions...")
        
        normal_transactions = []
        
        for i in range(count):
            customer = random.choice(self.customers)
            
            # Normal transaction patterns
            amount = max(1.0, random.gauss(customer.avg_transaction_amount, 50))
            
            transaction = Transaction(
                id=f"txn_{uuid.uuid4().hex[:12]}",
                customer_id=customer.id,
                amount=round(amount, 2),
                currency=random.choice(["USD", "EUR", "GBP", "CAD"]),
                payment_method=random.choice(self.payment_methods),
                merchant_id=f"merchant_{random.randint(1, 100)}",
                merchant_category=random.choice(self.merchant_categories),
                timestamp=(datetime.utcnow() - timedelta(
                    hours=random.randint(0, 168)  # Last 7 days
                )).isoformat(),
                ip_address=self._generate_ip_address(customer.country),
                device_id=f"device_{uuid.uuid4().hex[:8]}",
                location=self._generate_location(customer.country),
                risk_indicators=[],
                is_fraudulent=False
            )
            
            normal_transactions.append(transaction)
        
        print(f"✅ Generated {len(normal_transactions)} normal transactions")
        return normal_transactions

    def generate_fraud_transactions(self, count: int = 50) -> List[Transaction]:
        """Generate fraudulent transactions with specific patterns."""
        print(f"🔧 Generating {count} fraudulent transactions...")
        
        fraud_transactions = []
        
        for i in range(count):
            # Choose fraud type
            fraud_type = random.choice(self.fraud_types)
            customer = random.choice([c for c in self.customers if c.risk_profile in ["medium", "high"]])
            
            # Generate transaction based on fraud type
            transaction = self._generate_fraud_transaction(customer, fraud_type, i)
            fraud_transactions.append(transaction)
        
        print(f"✅ Generated {len(fraud_transactions)} fraudulent transactions")
        return fraud_transactions

    def _generate_fraud_transaction(self, customer: Customer, fraud_type: str, index: int) -> Transaction:
        """Generate a specific type of fraudulent transaction."""
        
        # Fraud-specific modifications
        if fraud_type == "stolen_card":
            amount = random.uniform(100, 2000)  # Higher amounts
            risk_indicators = ["new_device", "geo_velocity_impossible", "unusual_spending_pattern"]
            location = self._generate_location("XX")  # Foreign location
            
        elif fraud_type == "velocity_fraud":
            amount = random.uniform(10, 500)
            risk_indicators = ["multiple_transactions_short_time", "burst_pattern_detected"]
            location = self._generate_location(customer.country)
            
        elif fraud_type == "account_takeover":
            amount = random.uniform(200, 1500)
            risk_indicators = ["new_device", "suspicious_device_fingerprint", "identity_verification_failed"]
            location = self._generate_location("XX")
            
        elif fraud_type == "money_laundering":
            amount = random.uniform(500, 10000)  # Large amounts
            risk_indicators = ["unusual_merchant_category", "high_risk_country", "amount_outside_normal_range"]
            location = self._generate_location("XX")
            
        else:  # Default fraud pattern
            amount = random.uniform(50, 1000)
            risk_indicators = ["suspicious_device_fingerprint", "unusual_spending_pattern"]
            location = self._generate_location(customer.country)
        
        return Transaction(
            id=f"fraud_txn_{uuid.uuid4().hex[:12]}",
            customer_id=customer.id,
            amount=round(amount, 2),
            currency=random.choice(["USD", "EUR", "GBP"]),
            payment_method=random.choice(["card", "bank_transfer"]),
            merchant_id=f"merchant_{random.randint(1, 100)}",
            merchant_category=random.choice(["online_retail", "crypto_exchange", "money_transfer"]),
            timestamp=(datetime.utcnow() - timedelta(
                hours=random.randint(0, 48)  # Recent fraud
            )).isoformat(),
            ip_address=self._generate_suspicious_ip(),
            device_id=f"suspicious_device_{index}",
            location=location,
            risk_indicators=risk_indicators,
            is_fraudulent=True,
            fraud_type=fraud_type
        )

    def _generate_ip_address(self, country: str) -> str:
        """Generate IP address based on country."""
        country_ip_ranges = {
            "US": "192.168",
            "CA": "198.51", 
            "GB": "203.0",
            "DE": "198.18",
            "XX": "10.0"  # Suspicious/foreign
        }
        
        prefix = country_ip_ranges.get(country, "192.168")
        return f"{prefix}.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def _generate_suspicious_ip(self) -> str:
        """Generate suspicious IP addresses."""
        suspicious_ranges = ["10.0", "172.16", "192.0"]
        prefix = random.choice(suspicious_ranges)
        return f"{prefix}.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def _generate_location(self, country: str) -> Dict[str, Any]:
        """Generate location data."""
        if country == "XX":  # Suspicious location
            return {
                "country": random.choice(["XX", "ZZ", "Unknown"]),
                "city": "Unknown",
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180),
                "is_high_risk": True
            }
        
        country_locations = {
            "US": {"city": "New York", "lat": 40.7128, "lon": -74.0060},
            "CA": {"city": "Toronto", "lat": 43.6532, "lon": -79.3832},
            "GB": {"city": "London", "lat": 51.5074, "lon": -0.1278},
            "DE": {"city": "Berlin", "lat": 52.5200, "lon": 13.4050}
        }
        
        loc = country_locations.get(country, {"city": "Unknown", "lat": 0, "lon": 0})
        return {
            "country": country,
            "city": loc["city"],
            "latitude": loc["lat"] + random.uniform(-1, 1),
            "longitude": loc["lon"] + random.uniform(-1, 1),
            "is_high_risk": False
        }

    def export_data(self, filename: str = "fraud_test_data.json") -> None:
        """Export generated data to JSON file."""
        print(f"🔧 Exporting data to {filename}...")
        
        export_data = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "total_customers": len(self.customers),
                "total_transactions": len(self.transactions),
                "fraudulent_transactions": len([t for t in self.transactions if t.is_fraudulent]),
                "fraud_types": list(set([t.fraud_type for t in self.transactions if t.fraud_type]))
            },
            "customers": [asdict(c) for c in self.customers],
            "transactions": [asdict(t) for t in self.transactions]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Data exported to {filename}")

    def print_summary(self) -> None:
        """Print summary of generated data."""
        fraud_count = len([t for t in self.transactions if t.is_fraudulent])
        normal_count = len(self.transactions) - fraud_count
        
        print("\n" + "="*60)
        print("📊 FRAUD DETECTION DATA GENERATION SUMMARY")
        print("="*60)
        print(f"👥 Total Customers: {len(self.customers)}")
        print(f"💳 Total Transactions: {len(self.transactions)}")
        print(f"✅ Normal Transactions: {normal_count}")
        print(f"🔴 Fraudulent Transactions: {fraud_count}")
        print(f"📈 Fraud Rate: {(fraud_count/len(self.transactions)*100):.1f}%")
        
        if fraud_count > 0:
            print("\n🔍 FRAUD TYPES GENERATED:")
            fraud_types = {}
            for t in self.transactions:
                if t.is_fraudulent and t.fraud_type:
                    fraud_types[t.fraud_type] = fraud_types.get(t.fraud_type, 0) + 1
            
            for fraud_type, count in fraud_types.items():
                print(f"  • {fraud_type}: {count} transactions")
        
        print("="*60)

def main():
    """Main function to generate fraud detection data."""
    parser = argparse.ArgumentParser(description="Generate fraud detection test data")
    parser.add_argument("--customers", type=int, default=50, help="Number of customers to generate")
    parser.add_argument("--normal-txns", type=int, default=200, help="Number of normal transactions")
    parser.add_argument("--fraud-txns", type=int, default=25, help="Number of fraud transactions")
    parser.add_argument("--export-file", default="fraud_test_data.json", help="Export filename")
    
    args = parser.parse_args()
    
    print("🚀 MCP Payments Fraud Detection Data Generator")
    print("="*60)
    
    # Initialize generator
    generator = FraudDataGenerator()
    
    # Generate data
    generator.generate_customers(args.customers)
    normal_txns = generator.generate_normal_transactions(args.normal_txns)
    fraud_txns = generator.generate_fraud_transactions(args.fraud_txns)
    
    # Combine all transactions
    generator.transactions = normal_txns + fraud_txns
    random.shuffle(generator.transactions)  # Mix normal and fraud transactions
    
    # Export data
    generator.export_data(args.export_file)
    
    # Print summary
    generator.print_summary()
    
    print(f"\n✅ Fraud detection data generation complete!")
    print(f"📄 Data exported to: {args.export_file}")

if __name__ == "__main__":
    main() 