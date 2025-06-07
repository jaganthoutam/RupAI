#!/usr/bin/env python3
"""
Post Fraud Data to API Script

This script posts fraud detection data directly to the MCP Payments API
so you can immediately see fraud alerts in the admin portal.

Run with: python scripts/post_fraud_data_api.py
"""

import asyncio
import json
import httpx
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class FraudDataPoster:
    """Post fraud detection data to the API for admin portal viewing."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.auth_token: Optional[str] = None

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
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    async def create_realistic_transactions(self, count: int = 30) -> List[str]:
        """Create realistic transactions that will trigger fraud detection."""
        print(f"🔧 Creating {count} realistic transactions...")
        
        if not self.auth_token:
            print("❌ Not authenticated")
            return []
        
        transaction_ids = []
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Create different types of transactions
            transaction_patterns = [
                # Normal transactions (60%)
                {"type": "normal", "weight": 0.6, "amount_range": (10, 200), "methods": ["card", "bank_transfer", "wallet"]},
                # Suspicious high amounts (20%) 
                {"type": "high_amount", "weight": 0.2, "amount_range": (1000, 5000), "methods": ["card"], "risk": ["amount_outside_normal_range"]},
                # Velocity fraud (10%)
                {"type": "velocity", "weight": 0.1, "amount_range": (50, 300), "methods": ["card"], "risk": ["multiple_transactions_short_time"]},
                # Geographic anomalies (10%)
                {"type": "geo_anomaly", "weight": 0.1, "amount_range": (200, 1500), "methods": ["card"], "risk": ["geo_velocity_impossible", "high_risk_country"]}
            ]
            
            for i in range(count):
                # Choose transaction pattern based on weights
                pattern = random.choices(
                    transaction_patterns, 
                    weights=[p["weight"] for p in transaction_patterns]
                )[0]
                
                # Generate transaction based on pattern
                amount = random.uniform(*pattern["amount_range"])
                payment_method = random.choice(pattern["methods"])
                
                # Build metadata
                metadata = {
                    "test_scenario": pattern["type"],
                    "device_id": f"device_{random.randint(1000, 9999)}",
                    "session_id": f"session_{random.randint(10000, 99999)}",
                    "fraud_test": True
                }
                
                # Add risk indicators for suspicious transactions
                if "risk" in pattern:
                    metadata["risk_indicators"] = pattern["risk"]
                    metadata["suspicious"] = True
                    
                    # Add specific fraud metadata
                    if pattern["type"] == "geo_anomaly":
                        metadata["location"] = {
                            "country": "XX",
                            "city": "Unknown",
                            "is_high_risk": True,
                            "ip_address": "10.0.0.1"
                        }
                    elif pattern["type"] == "velocity":
                        metadata["velocity_pattern"] = {
                            "transactions_per_minute": random.randint(5, 15),
                            "burst_detected": True
                        }
                
                try:
                    payment_data = {
                        "amount": round(amount, 2),
                        "currency": "USD", 
                        "method": payment_method,
                        "customer_id": f"customer_{random.randint(1, 10)}",  # Use 10 different customers
                        "description": f"Test transaction - {pattern['type']}",
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
                        
                        # Show transaction type
                        if pattern["type"] == "normal":
                            print(f"  ✅ Normal: ${amount:.2f} - {payment_method}")
                        else:
                            print(f"  🔴 {pattern['type'].title()}: ${amount:.2f} - {payment_method}")
                    else:
                        print(f"  ❌ Failed transaction {i}: {response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Error creating transaction {i}: {str(e)}")
                
                # Small delay for velocity transactions
                if pattern["type"] == "velocity" and random.random() > 0.7:
                    await asyncio.sleep(0.1)  # Create burst pattern
        
        print(f"✅ Created {len(transaction_ids)} transactions")
        return transaction_ids

    async def trigger_fraud_detection(self) -> None:
        """Trigger fraud detection analysis on recent transactions."""
        print("🔍 Triggering fraud detection analysis...")
        
        if not self.auth_token:
            print("❌ Not authenticated")
            return
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Run multiple fraud detection scenarios
            detection_scenarios = [
                {
                    "name": "Recent High-Risk Activity",
                    "params": {"hours_back": 1, "risk_threshold": 50.0}
                },
                {
                    "name": "Velocity Pattern Analysis", 
                    "params": {"hours_back": 2, "risk_threshold": 60.0}
                },
                {
                    "name": "Geographic Anomaly Detection",
                    "params": {"hours_back": 6, "risk_threshold": 70.0}
                },
                {
                    "name": "Amount Deviation Analysis",
                    "params": {"hours_back": 12, "risk_threshold": 80.0}
                }
            ]
            
            for scenario in detection_scenarios:
                print(f"\n📊 Running: {scenario['name']}")
                
                try:
                    mcp_request = {
                        "jsonrpc": "2.0",
                        "id": random.randint(1000, 9999),
                        "method": "tools/call",
                        "params": {
                            "name": "detect_fraud_patterns",
                            "arguments": scenario["params"]
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
                        
                        # Extract and display key results
                        if "result" in result and "content" in result["result"]:
                            content = result["result"]["content"]
                            if content and len(content) > 0:
                                text = content[0].get("text", "")
                                # Extract key insights
                                if "97.2%" in text:
                                    print("   🎯 AI Detection: 97.2% accuracy")
                                if "alerts" in text.lower():
                                    print("   🚨 Fraud alerts generated")
                                if "risk" in text.lower():
                                    print("   📈 Risk patterns analyzed")
                        
                        # Check metadata
                        meta = result.get("result", {}).get("_meta", {})
                        if meta:
                            if "risk_score" in meta:
                                print(f"   📊 Risk Score: {meta['risk_score']}")
                            if "alerts" in meta:
                                print(f"   🚨 Alerts: {meta['alerts']}")
                    else:
                        print(f"   ❌ Analysis failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
                
                # Small delay between analyses
                await asyncio.sleep(1)

    async def generate_dashboard_metrics(self) -> None:
        """Generate dashboard metrics for admin portal."""
        print("\n📈 Generating dashboard metrics...")
        
        if not self.auth_token:
            print("❌ Not authenticated")
            return
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Generate various dashboard data
            dashboard_requests = [
                {
                    "name": "Real-time Metrics",
                    "tool": "get_dashboard_metrics",
                    "params": {"time_range": "1h", "refresh_cache": True}
                },
                {
                    "name": "24-Hour Analytics",
                    "tool": "get_dashboard_metrics", 
                    "params": {"time_range": "24h", "refresh_cache": True}
                },
                {
                    "name": "Fraud Analysis Report",
                    "tool": "generate_custom_report",
                    "params": {
                        "report_type": "fraud_analysis",
                        "start_date": (datetime.utcnow() - timedelta(hours=24)).isoformat(),
                        "end_date": datetime.utcnow().isoformat(),
                        "format": "json"
                    }
                }
            ]
            
            for request in dashboard_requests:
                print(f"📊 Generating: {request['name']}")
                
                try:
                    mcp_request = {
                        "jsonrpc": "2.0",
                        "id": random.randint(1000, 9999),
                        "method": "tools/call",
                        "params": {
                            "name": request["tool"],
                            "arguments": request["params"]
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
                        print(f"   ✅ Generated successfully")
                        
                        # Show relevant metrics
                        if "result" in result and "content" in result["result"]:
                            content = result["result"]["content"]
                            if content and len(content) > 0:
                                summary = content[0].get("text", "")[:100]
                                print(f"   📄 {summary}...")
                    else:
                        print(f"   ❌ Failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")

    def print_admin_portal_info(self) -> None:
        """Print information about accessing the admin portal."""
        print("\n" + "="*60)
        print("🎉 FRAUD DATA POSTED TO API")
        print("="*60)
        print("✅ Data Successfully Posted:")
        print("  • Realistic transactions created with fraud patterns")
        print("  • Fraud detection analyses triggered")
        print("  • Dashboard metrics generated")
        print("  • Real-time alerts activated")
        
        print("\n🔍 View in Admin Portal:")
        print("  1. Open: http://localhost:3000")
        print("  2. Navigate to: Fraud Detection")
        print("  3. Check: Real-time fraud alerts")
        print("  4. Review: Risk analytics and patterns")
        print("  5. Monitor: Live fraud detection dashboard")
        
        print("\n📊 Expected to See:")
        print("  • 🔴 High-risk transaction alerts")
        print("  • 🎯 97.2% AI detection accuracy")
        print("  • 📈 Real-time risk score analytics")
        print("  • 🚨 Fraud pattern notifications")
        print("  • 📄 Compliance and audit reports")
        
        print("\n💡 Next Steps:")
        print("  • Refresh admin dashboard to see new data")
        print("  • Test different fraud scenarios")
        print("  • Monitor real-time fraud detection")
        print("  • Review fraud analytics and reports")
        print("="*60)

async def main():
    """Main function to post fraud data to API."""
    print("🚀 MCP Payments Fraud Data API Poster")
    print("="*60)
    
    poster = FraudDataPoster()
    
    # Authenticate
    if not await poster.authenticate():
        print("❌ Authentication failed. Please ensure:")
        print("  • Backend is running (http://localhost:8000)")
        print("  • Test user exists (customer@test.com)")
        print("  • No rate limiting issues")
        return
    
    # Create realistic transactions
    print("\n🔧 Phase 1: Creating realistic transactions...")
    transaction_ids = await poster.create_realistic_transactions(25)
    
    if not transaction_ids:
        print("❌ No transactions created. Exiting.")
        return
    
    # Small delay to let transactions settle
    print("\n⏳ Waiting for transactions to process...")
    await asyncio.sleep(2)
    
    # Trigger fraud detection
    print("\n🔍 Phase 2: Triggering fraud detection...")
    await poster.trigger_fraud_detection()
    
    # Generate dashboard metrics
    print("\n📈 Phase 3: Generating dashboard metrics...")
    await poster.generate_dashboard_metrics()
    
    # Print admin portal info
    poster.print_admin_portal_info()

if __name__ == "__main__":
    asyncio.run(main()) 