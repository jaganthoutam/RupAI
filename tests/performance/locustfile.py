"""
Performance Testing for MCP Payments Enterprise System

Load testing scenarios for the MCP payment system including:
- Payment creation workflows
- Analytics API performance
- Wallet operations load testing
- Concurrent MCP tool usage
"""

import json
import uuid
import random
from locust import HttpUser, task, between, events
from datetime import datetime, timedelta

# Test Configuration
MCP_ENDPOINT = "/mcp"
API_ENDPOINT = "/api/v1"

class PaymentUser(HttpUser):
    """Simulates payment system users"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup user session"""
        self.customer_id = f"perf_customer_{uuid.uuid4().hex[:8]}"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "LoadTest/1.0"
        }
        
    def _mcp_call(self, tool_name: str, arguments: dict, name: str = None):
        """Make MCP protocol call"""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        with self.client.post(
            MCP_ENDPOINT,
            json=payload,
            headers=self.headers,
            name=name or f"MCP: {tool_name}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "error" in data or data.get("isError", False):
                    response.failure(f"MCP Error: {data}")
                else:
                    response.success()
                return data
            else:
                response.failure(f"HTTP {response.status_code}")
                return None
    
    @task(3)
    def create_payment(self):
        """Create payment via MCP (high frequency)"""
        amount = round(random.uniform(10.0, 1000.0), 2)
        
        self._mcp_call("create_payment", {
            "amount": amount,
            "currency": "USD",
            "method": random.choice(["card", "bank", "wallet"]),
            "customer_id": self.customer_id,
            "idempotency_key": f"perf_{uuid.uuid4().hex}",
            "description": f"Performance test payment {amount}"
        }, name="Payment Creation")
    
    @task(2)
    def verify_payment(self):
        """Verify payment status"""
        payment_id = f"pay_{uuid.uuid4().hex[:12]}"
        
        self._mcp_call("verify_payment", {
            "payment_id": payment_id
        }, name="Payment Verification")
    
    @task(2)
    def get_wallet_balance(self):
        """Check wallet balance via MCP"""
        self._mcp_call("get_wallet_balance", {
            "customer_id": self.customer_id,
            "currency": "USD"
        }, name="Wallet Balance Check")
    
    @task(1)
    def transfer_funds(self):
        """Transfer funds between wallets"""
        amount = round(random.uniform(5.0, 500.0), 2)
        
        self._mcp_call("transfer_funds", {
            "from_wallet_id": f"wallet_{uuid.uuid4().hex[:10]}",
            "to_wallet_id": f"wallet_{uuid.uuid4().hex[:10]}",
            "amount": amount,
            "currency": "USD",
            "description": f"Performance test transfer {amount}"
        }, name="Fund Transfer")

class AnalyticsUser(HttpUser):
    """Simulates analytics dashboard users"""
    wait_time = between(2, 5)
    
    def on_start(self):
        """Setup analytics user session"""
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "AnalyticsLoadTest/1.0"
        }
    
    @task(4)
    def get_revenue_analytics(self):
        """Fetch revenue analytics (most common)"""
        days = random.choice([1, 7, 30, 90])
        
        with self.client.get(
            f"{API_ENDPOINT}/analytics/revenue",
            params={"days": days},
            headers=self.headers,
            name="Revenue Analytics"
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
    
    @task(3)
    def get_payment_analytics(self):
        """Fetch payment analytics"""
        days = random.choice([7, 30])
        
        with self.client.get(
            f"{API_ENDPOINT}/analytics/payments",
            params={"days": days},
            headers=self.headers,
            name="Payment Analytics"
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def get_user_analytics(self):
        """Fetch user analytics"""
        days = random.choice([7, 30])
        
        with self.client.get(
            f"{API_ENDPOINT}/analytics/users",
            params={"days": days},
            headers=self.headers,
            name="User Analytics"
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_fraud_analytics(self):
        """Fetch fraud detection analytics"""
        with self.client.get(
            f"{API_ENDPOINT}/analytics/fraud",
            params={"days": 7},
            headers=self.headers,
            name="Fraud Analytics"
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")

class MonitoringUser(HttpUser):
    """Simulates monitoring dashboard users"""
    wait_time = between(3, 8)
    
    def on_start(self):
        """Setup monitoring user session"""
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "MonitoringLoadTest/1.0"
        }
    
    @task(5)
    def get_system_metrics(self):
        """Check system metrics (frequent monitoring)"""
        with self.client.get(
            f"{API_ENDPOINT}/monitoring/system-metrics",
            headers=self.headers,
            name="System Metrics"
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
    
    @task(3)
    def get_system_status(self):
        """Check system status"""
        with self.client.get(
            f"{API_ENDPOINT}/monitoring/system-status",
            headers=self.headers,
            name="System Status"
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_alerts(self):
        """Check system alerts"""
        with self.client.get(
            f"{API_ENDPOINT}/monitoring/alerts",
            headers=self.headers,
            name="System Alerts"
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")

class WalletUser(HttpUser):
    """Simulates wallet management users"""
    wait_time = between(1, 4)
    
    def on_start(self):
        """Setup wallet user session"""
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "WalletLoadTest/1.0"
        }
    
    @task(4)
    def list_wallets(self):
        """List user wallets"""
        limit = random.choice([5, 10, 20])
        
        with self.client.get(
            f"{API_ENDPOINT}/wallets",
            params={"limit": limit},
            headers=self.headers,
            name="List Wallets"
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def get_wallet_transactions(self):
        """Get wallet transaction history"""
        wallet_id = f"wallet_{uuid.uuid4().hex[:12]}"
        
        with self.client.get(
            f"{API_ENDPOINT}/wallets/{wallet_id}/transactions",
            params={"limit": 10},
            headers=self.headers,
            name="Wallet Transactions"
        ) as response:
            # 404 is expected for non-existent wallets in load test
            if response.status_code not in [200, 404]:
                response.failure(f"HTTP {response.status_code}")

class ComplianceUser(HttpUser):
    """Simulates compliance team users"""
    wait_time = between(5, 15)
    
    def on_start(self):
        """Setup compliance user session"""
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "ComplianceLoadTest/1.0"
        }
    
    @task(3)
    def get_audit_logs(self):
        """Fetch audit logs"""
        limit = random.choice([10, 25, 50])
        
        with self.client.get(
            f"{API_ENDPOINT}/compliance/audit-logs",
            params={"limit": limit},
            headers=self.headers,
            name="Audit Logs"
        ) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_compliance_report(self):
        """Generate compliance report"""
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        end_date = datetime.now().isoformat()
        
        with self.client.get(
            f"{API_ENDPOINT}/compliance/reports",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "type": "monthly"
            },
            headers=self.headers,
            name="Compliance Report"
        ) as response:
            # This endpoint might not exist, so allow 404
            if response.status_code not in [200, 404]:
                response.failure(f"HTTP {response.status_code}")

# Performance test scenarios
class HighLoadPaymentUser(PaymentUser):
    """High-frequency payment user for stress testing"""
    wait_time = between(0.1, 0.5)  # Very fast requests
    weight = 3

class NormalAnalyticsUser(AnalyticsUser):
    """Normal analytics usage"""
    weight = 2

class LightMonitoringUser(MonitoringUser):
    """Light monitoring usage"""
    weight = 1

# Event handlers for performance reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Print test start information"""
    print(f"\n🚀 STARTING PERFORMANCE TEST")
    print(f"Target: {environment.host}")
    print(f"Users: {environment.runner.target_user_count}")
    print("=" * 50)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print test completion summary"""
    stats = environment.runner.stats
    print(f"\n📊 PERFORMANCE TEST RESULTS")
    print("=" * 50)
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests/sec: {stats.total.current_rps:.2f}")
    print(f"Failure Rate: {(stats.total.num_failures/stats.total.num_requests*100):.2f}%")
    print("=" * 50)
    
    # Performance benchmarks
    if stats.total.avg_response_time > 500:
        print("⚠️  WARNING: Average response time exceeds 500ms")
    if (stats.total.num_failures/stats.total.num_requests) > 0.01:
        print("⚠️  WARNING: Failure rate exceeds 1%")
    if stats.total.current_rps < 10:
        print("⚠️  WARNING: Low throughput detected")

# Custom performance metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Track custom performance metrics"""
    if exception:
        return
        
    # Track slow requests
    if response_time > 1000:
        print(f"🐌 Slow request detected: {name} took {response_time:.2f}ms")
    
    # Track MCP-specific metrics
    if name.startswith("MCP:"):
        # Could store MCP-specific metrics here
        pass 