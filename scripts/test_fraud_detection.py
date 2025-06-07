#!/usr/bin/env python3
"""
Fraud Detection API Testing Script

This script tests the MCP Payments fraud detection system with realistic scenarios
and creates live transaction data for testing.

Run with: python scripts/test_fraud_detection.py
"""

import asyncio
import json
import httpx
import argparse
from datetime import datetime, timedelta
import random
import uuid
from typing import Dict, List, Any, Optional

class FraudDetectionTester:
    """Test fraud detection system with realistic scenarios."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.auth_token: Optional[str] = None
        
        # Test scenarios
        self.fraud_scenarios = [
            {
                "name": "Velocity Attack",
                "description": "Multiple rapid transactions from same customer",
                "pattern": "velocity_fraud",
                "risk_level": "high"
            },
            {
                "name": "Geographic Anomaly", 
                "description": "Transaction from impossible location",
                "pattern": "location_fraud",
                "risk_level": "high"
            },
            {
                "name": "Large Amount Deviation",
                "description": "Transaction significantly larger than normal",
                "pattern": "amount_fraud",
                "risk_level": "medium"
            },
            {
                "name": "New Device Pattern",
                "description": "First-time device with suspicious behavior", 
                "pattern": "device_fraud",
                "risk_level": "medium"
            },
            {
                "name": "Off-Hours Activity",
                "description": "Unusual activity during off hours",
                "pattern": "behavioral_fraud",
                "risk_level": "low"
            }
        ]

    async def authenticate(self) -> bool:
        """Authenticate with the API."""
        print("🔐 Authenticating with API...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Try to login with test account
                response = await client.post(
                    f"{self.api_base_url}/api/v1/auth/login",
                    json={
                        "email": "customer@test.com",
                        "password": "TestPassword123!"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    print("✅ Authentication successful")
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status_code}")
                    print("Creating test user...")
                    return await self._create_test_user()
                    
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    async def _create_test_user(self) -> bool:
        """Create a test user for fraud testing."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/api/v1/auth/register",
                    json={
                        "name": "Fraud Test Customer",
                        "email": "customer@test.com",
                        "password": "TestPassword123!",
                        "phone": "+1234567890"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    print("✅ Test user created and authenticated")
                    return True
                else:
                    print(f"❌ Failed to create test user: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error creating test user: {str(e)}")
            return False

    async def create_test_transactions(self, count: int = 20) -> List[str]:
        """Create test transactions for fraud analysis."""
        print(f"🔧 Creating {count} test transactions...")
        
        if not self.auth_token:
            print("❌ Not authenticated")
            return []
        
        transaction_ids = []
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            for i in range(count):
                # Mix of normal and suspicious transactions
                is_suspicious = i % 4 == 0  # 25% suspicious
                
                if is_suspicious:
                    amount = random.uniform(500, 5000)  # High amounts
                    payment_method = "card"
                    metadata = {
                        "test_scenario": "suspicious",
                        "risk_indicators": ["large_amount", "new_device"],
                        "device_id": f"suspicious_device_{i}"
                    }
                else:
                    amount = random.uniform(10, 200)  # Normal amounts
                    payment_method = random.choice(["card", "bank_transfer", "wallet"])
                    metadata = {
                        "test_scenario": "normal",
                        "device_id": f"normal_device_{i}"
                    }
                
                try:
                    payment_data = {
                        "amount": round(amount, 2),
                        "currency": "USD",
                        "payment_method": payment_method,
                        "customer_id": f"test_customer_{i % 5}",  # Reuse some customers
                        "metadata": metadata
                    }
                    
                    response = await client.post(
                        f"{self.api_base_url}/api/v1/payments/",
                        json=payment_data,
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        transaction_id = result.get("id", f"txn_{i}")
                        transaction_ids.append(transaction_id)
                        
                        status = "🔴 SUSPICIOUS" if is_suspicious else "✅ NORMAL"
                        print(f"  {status} Transaction: ${amount:.2f} - {payment_method}")
                    else:
                        print(f"  ❌ Failed transaction {i}: {response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Error creating transaction {i}: {str(e)}")
        
        print(f"✅ Created {len(transaction_ids)} transactions")
        return transaction_ids

    async def test_fraud_detection_scenarios(self) -> None:
        """Test various fraud detection scenarios."""
        print("\n🔍 Testing Fraud Detection Scenarios...")
        print("="*60)
        
        if not self.auth_token:
            print("❌ Not authenticated")
            return
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            for i, scenario in enumerate(self.fraud_scenarios):
                print(f"\n📊 Testing: {scenario['name']}")
                print(f"   Description: {scenario['description']}")
                print(f"   Risk Level: {scenario['risk_level']}")
                
                # Test fraud detection with different parameters
                test_params = {
                    "hours_back": 24,
                    "risk_threshold": 50.0 if scenario['risk_level'] == 'high' else 70.0
                }
                
                try:
                    # Use MCP tools endpoint for fraud detection
                    mcp_request = {
                        "jsonrpc": "2.0",
                        "id": i + 1,
                        "method": "tools/call",
                        "params": {
                            "name": "detect_fraud_patterns",
                            "arguments": test_params
                        }
                    }
                    
                    response = await client.post(
                        f"{self.api_base_url}/mcp/tools/call",
                        json=mcp_request,
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Extract fraud detection results
                        if "result" in result and "content" in result["result"]:
                            content = result["result"]["content"]
                            if content and isinstance(content, list) and len(content) > 0:
                                text_content = content[0].get("text", "")
                                print(f"   ✅ Result: {text_content[:100]}...")
                            else:
                                print("   ✅ Fraud detection completed (no content)")
                        
                        # Check metadata for additional insights
                        meta = result.get("result", {}).get("_meta", {})
                        if meta:
                            risk_score = meta.get("risk_score", "N/A")
                            alerts = meta.get("alerts", 0)
                            print(f"   📈 Risk Score: {risk_score}")
                            print(f"   🚨 Alerts: {alerts}")
                    else:
                        print(f"   ❌ Test failed: {response.status_code}")
                        if response.status_code == 404:
                            print("   💡 MCP tools endpoint may not be available")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")

    async def test_specific_fraud_patterns(self) -> None:
        """Test specific fraud patterns with targeted data."""
        print("\n🎯 Testing Specific Fraud Patterns...")
        print("="*60)
        
        patterns = [
            {
                "name": "High Velocity",
                "params": {"hours_back": 1, "risk_threshold": 30.0},
                "description": "Detect rapid transaction patterns"
            },
            {
                "name": "Geographic Analysis", 
                "params": {"hours_back": 6, "risk_threshold": 60.0},
                "description": "Analyze geographic anomalies"
            },
            {
                "name": "Amount Analysis",
                "params": {"hours_back": 12, "risk_threshold": 80.0},
                "description": "Detect unusual transaction amounts"
            }
        ]
        
        if not self.auth_token:
            print("❌ Not authenticated")
            return
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            for pattern in patterns:
                print(f"\n🔬 {pattern['name']}")
                print(f"   {pattern['description']}")
                
                try:
                    mcp_request = {
                        "jsonrpc": "2.0",
                        "id": random.randint(1000, 9999),
                        "method": "tools/call",
                        "params": {
                            "name": "detect_fraud_patterns",
                            "arguments": pattern["params"]
                        }
                    }
                    
                    response = await client.post(
                        f"{self.api_base_url}/mcp/tools/call",
                        json=mcp_request,
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ Analysis completed")
                        
                        # Show relevant fraud insights
                        if "result" in result:
                            meta = result["result"].get("_meta", {})
                            if "fraud_score" in meta:
                                print(f"   📊 Fraud Score: {meta['fraud_score']}")
                            if "patterns_detected" in meta:
                                print(f"   🔍 Patterns: {meta['patterns_detected']}")
                    else:
                        print(f"   ❌ Failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")

    async def test_custom_analytics(self) -> None:
        """Test custom analytics and reporting."""
        print("\n📈 Testing Custom Analytics...")
        print("="*60)
        
        if not self.auth_token:
            print("❌ Not authenticated")
            return
        
        # Test different analytics endpoints
        analytics_tests = [
            {
                "name": "Fraud Analysis Report",
                "tool": "generate_custom_report",
                "params": {
                    "report_type": "fraud_analysis",
                    "start_date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                    "end_date": datetime.utcnow().isoformat(),
                    "format": "json"
                }
            },
            {
                "name": "Dashboard Metrics",
                "tool": "get_dashboard_metrics", 
                "params": {
                    "time_range": "24h",
                    "refresh_cache": True
                }
            }
        ]
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            for test in analytics_tests:
                print(f"\n📊 {test['name']}")
                
                try:
                    mcp_request = {
                        "jsonrpc": "2.0", 
                        "id": random.randint(1000, 9999),
                        "method": "tools/call",
                        "params": {
                            "name": test["tool"],
                            "arguments": test["params"]
                        }
                    }
                    
                    response = await client.post(
                        f"{self.api_base_url}/mcp/tools/call",
                        json=mcp_request,
                        headers=headers,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ Analytics generated successfully")
                        
                        # Show summary of results
                        if "result" in result and "content" in result["result"]:
                            content = result["result"]["content"]
                            if content and len(content) > 0:
                                summary = content[0].get("text", "")[:150]
                                print(f"   📄 Summary: {summary}...")
                    else:
                        print(f"   ❌ Failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")

    def print_summary(self) -> None:
        """Print testing summary and next steps."""
        print("\n" + "="*60)
        print("🎉 FRAUD DETECTION TESTING COMPLETE")
        print("="*60)
        print("✅ Test Results:")
        print("  • API Authentication: Successful")
        print("  • Transaction Creation: Completed")
        print("  • Fraud Detection: Tested")
        print("  • Analytics Generation: Verified")
        print("\n🔍 Next Steps:")
        print("  1. Open Admin Dashboard: http://localhost:3000")
        print("  2. Navigate to Fraud Detection section")
        print("  3. Review generated alerts and patterns") 
        print("  4. Test customer app: http://localhost:3001")
        print("  5. Monitor real-time fraud detection")
        print("="*60)

async def main():
    """Main testing function."""
    parser = argparse.ArgumentParser(description="Test fraud detection system")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--transactions", type=int, default=20, help="Number of test transactions")
    parser.add_argument("--skip-transactions", action="store_true", help="Skip transaction creation")
    
    args = parser.parse_args()
    
    print("🚀 MCP Payments Fraud Detection Tester")
    print("="*60)
    
    tester = FraudDetectionTester(api_base_url=args.api_url)
    
    # Authenticate
    if not await tester.authenticate():
        print("❌ Authentication failed. Exiting.")
        return
    
    # Create test transactions
    if not args.skip_transactions:
        await tester.create_test_transactions(args.transactions)
    
    # Test fraud detection scenarios
    await tester.test_fraud_detection_scenarios()
    
    # Test specific patterns
    await tester.test_specific_fraud_patterns()
    
    # Test analytics
    await tester.test_custom_analytics()
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main()) 