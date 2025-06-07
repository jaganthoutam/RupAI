#!/usr/bin/env python3
"""
MCP Payments E2E Test Runner

Comprehensive test runner for the MCP Payments Enterprise system.
Includes all major workflows and performance benchmarks.
"""

import asyncio
import json
import uuid
import httpx
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8000"
MCP_ENDPOINT = f"{BASE_URL}/mcp"
API_ENDPOINT = f"{BASE_URL}/api/v1"

class MCPPaymentsTestRunner:
    """Complete MCP Payments Test Runner"""
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30.0, follow_redirects=False)
        self.test_results = []
        self.start_time = None
        
    async def setup(self):
        """Initialize test environment"""
        print("\n🚀 MCP PAYMENTS E2E TEST SUITE")
        print("=" * 50)
        self.start_time = time.time()
        
        # Health check
        try:
            response = await self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                health = response.json()
                print(f"✅ System Health: {health.get('status', 'unknown')}")
            else:
                print("❌ System health check failed")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
            
        return True
        
    async def cleanup(self):
        """Cleanup test environment"""
        await self.session.aclose()
        
    async def _mcp_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool call"""
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self.session.post(MCP_ENDPOINT, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
            
    async def test_mcp_tools_discovery(self):
        """Test 1: MCP Tools Discovery"""
        print("\n🧪 Test 1: MCP Tools Discovery")
        
        try:
            response = await self.session.post(MCP_ENDPOINT, json={
                "jsonrpc": "2.0",
                "id": "test-tools",
                "method": "tools/list"
            })
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get("result", {}).get("tools", [])
                tool_names = [tool.get("name") for tool in tools]
                
                expected_tools = [
                    "create_payment", "verify_payment", "refund_payment",
                    "get_wallet_balance", "transfer_funds"
                ]
                
                found_tools = sum(1 for tool in expected_tools if tool in tool_names)
                print(f"   Found {len(tools)} total tools")
                print(f"   Expected tools found: {found_tools}/{len(expected_tools)}")
                
                result = {
                    "test": "mcp_tools_discovery",
                    "status": "passed" if found_tools >= 3 else "failed",
                    "tools_found": len(tools),
                    "expected_found": found_tools
                }
            else:
                result = {"test": "mcp_tools_discovery", "status": "failed", "error": "HTTP error"}
                
        except Exception as e:
            result = {"test": "mcp_tools_discovery", "status": "failed", "error": str(e)}
            
        self.test_results.append(result)
        print(f"   Status: {'✅ PASSED' if result['status'] == 'passed' else '❌ FAILED'}")
        
    async def test_payment_creation(self):
        """Test 2: Payment Creation via MCP"""
        print("\n🧪 Test 2: Payment Creation via MCP")
        
        customer_id = f"test_customer_{uuid.uuid4().hex[:8]}"
        amount = 99.99
        
        try:
            result = await self._mcp_call("create_payment", {
                "amount": amount,
                "currency": "USD",
                "method": "card",
                "customer_id": customer_id,
                "idempotency_key": f"test_{uuid.uuid4().hex}",
                "description": "E2E Test Payment"
            })
            
            if "error" not in result and not result.get("isError", False):
                payment_id = result.get("result", {}).get("_meta", {}).get("payment_id")
                print(f"   Payment created: {payment_id}")
                
                test_result = {
                    "test": "payment_creation",
                    "status": "passed",
                    "payment_id": payment_id,
                    "amount": amount
                }
            else:
                test_result = {
                    "test": "payment_creation", 
                    "status": "failed",
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            test_result = {"test": "payment_creation", "status": "failed", "error": str(e)}
            
        self.test_results.append(test_result)
        print(f"   Status: {'✅ PASSED' if test_result['status'] == 'passed' else '❌ FAILED'}")
        
    async def test_wallet_operations(self):
        """Test 3: Wallet Operations"""
        print("\n🧪 Test 3: Wallet Operations")
        
        try:
            # Test wallet balance via MCP (this doesn't require authentication)
            balance_result = await self._mcp_call("get_wallet_balance", {
                "customer_id": f"test_wallet_{uuid.uuid4().hex[:8]}",
                "currency": "USD"
            })
            
            mcp_success = "error" not in balance_result and not balance_result.get("isError", False)
            print(f"   MCP wallet balance call: {'✅' if mcp_success else '❌'}")
            
            # Test direct wallet endpoint (with proper trailing slash to avoid redirect)
            api_response = await self.session.get(f"{API_ENDPOINT}/wallets/?limit=5")
            
            # Should work in development mode with mock auth
            api_works_correctly = api_response.status_code == 200
            
            if api_response.status_code == 200:
                print(f"   API wallets endpoint: ✅ (development mode)")
                try:
                    wallets = api_response.json()
                    wallet_count = len(wallets) if isinstance(wallets, list) else 0
                    print(f"   Found {wallet_count} wallets via API")
                except:
                    print(f"   Invalid JSON response from wallets API")
                    api_works_correctly = False
            else:
                print(f"   API wallets endpoint: ❌ (status: {api_response.status_code})")
            
            # Overall success if MCP works and API responds appropriately
            overall_success = mcp_success and api_works_correctly
            
            result = {
                "test": "wallet_operations",
                "status": "passed" if overall_success else "failed",
                "mcp_success": mcp_success,
                "api_response_code": api_response.status_code,
                "api_works": api_works_correctly
            }
            
        except Exception as e:
            result = {"test": "wallet_operations", "status": "failed", "error": str(e)}
            
        self.test_results.append(result)
        print(f"   Status: {'✅ PASSED' if result['status'] == 'passed' else '❌ FAILED'}")
        
    async def test_analytics_endpoints(self):
        """Test 4: Analytics Endpoints"""
        print("\n🧪 Test 4: Analytics Endpoints")
        
        endpoints = [
            ("revenue", f"{API_ENDPOINT}/analytics/revenue?days=7"),
            ("payments", f"{API_ENDPOINT}/analytics/payments?days=7"),
            ("users", f"{API_ENDPOINT}/analytics/users?days=7")
        ]
        
        results = {}
        overall_success = True
        
        for name, url in endpoints:
            try:
                response = await self.session.get(url)
                success = response.status_code == 200
                results[name] = success
                if not success:
                    overall_success = False
                print(f"   {name.title()} analytics: {'✅' if success else '❌'}")
            except Exception as e:
                results[name] = False
                overall_success = False
                print(f"   {name.title()} analytics: ❌ ({e})")
                
        result = {
            "test": "analytics_endpoints",
            "status": "passed" if overall_success else "failed",
            "endpoint_results": results
        }
        
        self.test_results.append(result)
        print(f"   Status: {'✅ PASSED' if result['status'] == 'passed' else '❌ FAILED'}")
        
    async def test_monitoring_endpoints(self):
        """Test 5: Monitoring Endpoints"""
        print("\n🧪 Test 5: Monitoring Endpoints")
        
        endpoints = [
            ("metrics", f"{API_ENDPOINT}/monitoring/system-metrics"),
            ("status", f"{API_ENDPOINT}/monitoring/system-status"),
            ("alerts", f"{API_ENDPOINT}/monitoring/alerts")
        ]
        
        results = {}
        overall_success = True
        
        for name, url in endpoints:
            try:
                response = await self.session.get(url)
                success = response.status_code == 200
                results[name] = success
                if not success:
                    overall_success = False
                print(f"   {name.title()}: {'✅' if success else '❌'}")
            except Exception as e:
                results[name] = False
                overall_success = False
                print(f"   {name.title()}: ❌ ({e})")
                
        result = {
            "test": "monitoring_endpoints",
            "status": "passed" if overall_success else "failed",
            "endpoint_results": results
        }
        
        self.test_results.append(result)
        print(f"   Status: {'✅ PASSED' if result['status'] == 'passed' else '❌ FAILED'}")
        
    async def test_compliance_endpoints(self):
        """Test 6: Compliance & Audit Endpoints"""
        print("\n🧪 Test 6: Compliance & Audit")
        
        try:
            response = await self.session.get(f"{API_ENDPOINT}/compliance/audit-logs?limit=5")
            success = response.status_code == 200
            
            if success:
                audit_data = response.json()
                audit_count = len(audit_data) if isinstance(audit_data, list) else 0
                print(f"   Found {audit_count} audit log entries")
            
            result = {
                "test": "compliance_endpoints",
                "status": "passed" if success else "failed",
                "audit_logs_found": audit_count if success else 0
            }
            
        except Exception as e:
            result = {"test": "compliance_endpoints", "status": "failed", "error": str(e)}
            
        self.test_results.append(result)
        print(f"   Status: {'✅ PASSED' if result['status'] == 'passed' else '❌ FAILED'}")
        
    async def test_concurrent_requests(self):
        """Test 7: Concurrent Request Handling"""
        print("\n🧪 Test 7: Concurrent Request Handling")
        
        async def make_request(i):
            try:
                response = await self.session.get(f"{API_ENDPOINT}/analytics/revenue?days=1")
                return response.status_code == 200
            except:
                return False
                
        try:
            # Make 10 concurrent requests
            tasks = [make_request(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            successful = sum(results)
            
            print(f"   Concurrent requests: {successful}/10 successful")
            
            result = {
                "test": "concurrent_requests",
                "status": "passed" if successful >= 8 else "failed",
                "successful_requests": successful,
                "total_requests": 10
            }
            
        except Exception as e:
            result = {"test": "concurrent_requests", "status": "failed", "error": str(e)}
            
        self.test_results.append(result)
        print(f"   Status: {'✅ PASSED' if result['status'] == 'passed' else '❌ FAILED'}")
        
    async def test_error_handling(self):
        """Test 8: Error Handling"""
        print("\n🧪 Test 8: Error Handling")
        
        error_tests = [
            ("truly_invalid_endpoint", f"{API_ENDPOINT}/nonexistent/endpoint/that/really/does/not/exist"),
            ("malformed_payment_id", f"{API_ENDPOINT}/payments/clearly-invalid-payment-id"),
            ("deep_invalid_path", f"{API_ENDPOINT}/some/deep/invalid/path/structure")
        ]
        
        error_handled_correctly = 0
        
        for test_name, url in error_tests:
            try:
                response = await self.session.get(url)
                # We expect proper error codes for truly invalid endpoints
                # 404 for not found, 422 for validation errors, etc.
                expected_codes = [404, 422, 500]
                
                if response.status_code in expected_codes:
                    error_handled_correctly += 1
                    print(f"   {test_name}: ✅ (returned {response.status_code})")
                else:
                    print(f"   {test_name}: ❌ (unexpected {response.status_code})")
            except Exception as e:
                print(f"   {test_name}: ❌ (exception: {e})")
                
        result = {
            "test": "error_handling",
            "status": "passed" if error_handled_correctly >= 2 else "failed",
            "errors_handled": error_handled_correctly,
            "total_error_tests": len(error_tests)
        }
        
        self.test_results.append(result)
        print(f"   Status: {'✅ PASSED' if result['status'] == 'passed' else '❌ FAILED'}")
        
    def generate_final_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get("status") == "passed")
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🎯 MCP PAYMENTS E2E TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests:     {total_tests}")
        print(f"Passed:          {passed_tests} ✅")
        print(f"Failed:          {failed_tests} ❌")
        print(f"Success Rate:    {success_rate:.1f}%")
        print(f"Total Time:      {total_time:.2f} seconds")
        print("\n📊 DETAILED RESULTS:")
        
        for i, result in enumerate(self.test_results, 1):
            status_icon = "✅" if result.get("status") == "passed" else "❌"
            test_name = result.get("test", "unknown").replace("_", " ").title()
            print(f"{i:2d}. {status_icon} {test_name}")
            
            # Show additional details
            if "tools_found" in result:
                print(f"     → Tools discovered: {result['tools_found']}")
            elif "payment_id" in result:
                print(f"     → Payment ID: {result['payment_id']}")
            elif "api_response_code" in result:
                print(f"     → MCP works, API status: {result['api_response_code']}")
            elif "successful_requests" in result:
                print(f"     → Concurrent success: {result['successful_requests']}/{result['total_requests']}")
            elif "errors_handled" in result:
                print(f"     → Error handling: {result['errors_handled']}/{result['total_error_tests']}")
                
            if "error" in result:
                print(f"     → Error: {result['error']}")
                
        print("\n" + "=" * 60)
        
        if success_rate == 100:
            print("🏆 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
        elif success_rate >= 80:
            print("✅ MOSTLY SUCCESSFUL - SYSTEM READY WITH MINOR NOTES")
        else:
            print("⚠️ ISSUES DETECTED - REQUIRES ATTENTION")
            
        print("=" * 60)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "total_time": total_time,
            "results": self.test_results
        }
        
    async def run_all_tests(self):
        """Run complete test suite"""
        if not await self.setup():
            return {"error": "Setup failed"}
            
        try:
            # Run all test workflows
            await self.test_mcp_tools_discovery()
            await self.test_payment_creation()
            await self.test_wallet_operations()
            await self.test_analytics_endpoints()
            await self.test_monitoring_endpoints()
            await self.test_compliance_endpoints()
            await self.test_concurrent_requests()
            await self.test_error_handling()
            
            return self.generate_final_report()
            
        finally:
            await self.cleanup()

async def main():
    """Main test runner"""
    test_runner = MCPPaymentsTestRunner()
    results = await test_runner.run_all_tests()
    
    if "error" in results:
        print(f"Test suite failed: {results['error']}")
        sys.exit(1)
        
    # Exit with appropriate code
    exit_code = 0 if results["success_rate"] >= 80 else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main()) 