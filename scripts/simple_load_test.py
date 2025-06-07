#!/usr/bin/env python3
"""
MCP Payments Load Testing Script
Tests end-to-end functionality with configurable concurrent payments
"""

import asyncio
import aiohttp
import json
import time
import logging
from uuid import uuid4
import random
import sys
import argparse
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PaymentLoadTester:
    """Load tester for MCP Payment system."""
    
    def __init__(self, base_url: str = 'http://localhost:8000', total_payments: int = 1000, 
                 concurrent: int = 100, timeout: int = 30):
        self.base_url = base_url
        self.total_payments = total_payments
        self.concurrent = concurrent
        self.timeout = timeout
        self.currencies = ['USD', 'EUR', 'GBP', 'INR', 'JPY']
        self.payment_methods = ['card', 'bank_transfer', 'wallet', 'upi']
        self.results = []
        
    async def create_payment_request(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Create a single payment request."""
        payload = {
            'jsonrpc': '2.0',
            'id': uuid4().hex,
            'method': 'tools/call',
            'params': {
                'name': 'create_payment',
                'arguments': {
                    'amount': round(random.uniform(10.0, 1000.0), 2),
                    'currency': random.choice(self.currencies),
                    'method': random.choice(self.payment_methods),
                    'customer_id': str(uuid4()),
                    'idempotency_key': f'test_{uuid4().hex}',
                    'description': f'Load test payment {uuid4().hex[:8]}',
                    'metadata': {
                        'test_run': True,
                        'load_test_id': uuid4().hex,
                        'timestamp': time.time()
                    }
                }
            }
        }
        
        start_time = time.time()
        try:
            async with session.post(f'{self.base_url}/mcp', json=payload) as response:
                response_time = time.time() - start_time
                result_data = await response.json()
                
                return {
                    'success': response.status == 200 and not result_data.get('error'),
                    'response_time': response_time,
                    'status_code': response.status,
                    'payload_size': len(json.dumps(payload)),
                    'response_size': len(json.dumps(result_data)),
                    'data': result_data
                }
        except Exception as e:
            return {
                'success': False,
                'response_time': time.time() - start_time,
                'error': str(e),
                'status_code': None
            }
    
    async def verify_payment_request(self, session: aiohttp.ClientSession, payment_id: str) -> Dict[str, Any]:
        """Verify a payment request."""
        payload = {
            'jsonrpc': '2.0',
            'id': uuid4().hex,
            'method': 'tools/call',
            'params': {
                'name': 'verify_payment',
                'arguments': {
                    'payment_id': payment_id
                }
            }
        }
        
        start_time = time.time()
        try:
            async with session.post(f'{self.base_url}/mcp', json=payload) as response:
                response_time = time.time() - start_time
                result_data = await response.json()
                
                return {
                    'success': response.status == 200 and not result_data.get('error'),
                    'response_time': response_time,
                    'status_code': response.status,
                    'data': result_data
                }
        except Exception as e:
            return {
                'success': False,
                'response_time': time.time() - start_time,
                'error': str(e)
            }
    
    async def get_wallet_balance_request(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Get wallet balance request."""
        payload = {
            'jsonrpc': '2.0',
            'id': uuid4().hex,
            'method': 'tools/call',
            'params': {
                'name': 'get_wallet_balance',
                'arguments': {
                    'customer_id': str(uuid4()),
                    'currency': random.choice(self.currencies)
                }
            }
        }
        
        start_time = time.time()
        try:
            async with session.post(f'{self.base_url}/mcp', json=payload) as response:
                response_time = time.time() - start_time
                result_data = await response.json()
                
                return {
                    'success': response.status == 200 and not result_data.get('error'),
                    'response_time': response_time,
                    'status_code': response.status,
                    'data': result_data
                }
        except Exception as e:
            return {
                'success': False,
                'response_time': time.time() - start_time,
                'error': str(e)
            }
    
    async def mixed_scenario_request(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Execute a mixed scenario (different operations)."""
        scenario = random.choice(['create_payment', 'verify_payment', 'get_wallet_balance'])
        
        if scenario == 'create_payment':
            result = await self.create_payment_request(session)
            result['scenario'] = 'create_payment'
            return result
        elif scenario == 'verify_payment':
            payment_id = f'pay_{uuid4().hex[:12]}'
            result = await self.verify_payment_request(session, payment_id)
            result['scenario'] = 'verify_payment'
            return result
        else:
            result = await self.get_wallet_balance_request(session)
            result['scenario'] = 'get_wallet_balance'
            return result
    
    async def run_load_test(self, mixed_scenarios: bool = False) -> Dict[str, Any]:
        """Execute the complete load test."""
        logger.info(f"Starting load test with {self.total_payments} requests")
        logger.info(f"Concurrent requests: {self.concurrent}")
        logger.info(f"Target URL: {self.base_url}")
        logger.info(f"Mixed scenarios: {mixed_scenarios}")
        
        # Setup HTTP session with proper configuration
        connector = aiohttp.TCPConnector(
            limit=200,  # Total connection pool size
            limit_per_host=50,  # Per-host connection limit
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        ) as session:
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(self.concurrent)
            
            async def bounded_request():
                async with semaphore:
                    if mixed_scenarios:
                        return await self.mixed_scenario_request(session)
                    else:
                        return await self.create_payment_request(session)
            
            # Record start time
            start_time = time.time()
            
            # Create and execute all tasks
            tasks = [bounded_request() for _ in range(self.total_payments)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Calculate total test duration
            total_duration = time.time() - start_time
            
            # Process results
            valid_results = []
            for result in results:
                if isinstance(result, dict):
                    valid_results.append(result)
                elif isinstance(result, Exception):
                    valid_results.append({
                        'success': False,
                        'response_time': 0,
                        'error': str(result)
                    })
            
            # Generate comprehensive report
            report = self.generate_report(valid_results, total_duration)
            self.print_report(report)
            
            return report
    
    def generate_report(self, results: List[Dict[str, Any]], total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        successful_results = [r for r in results if r.get('success', False)]
        failed_results = [r for r in results if not r.get('success', False)]
        
        # Calculate performance metrics
        response_times = [r['response_time'] for r in successful_results if 'response_time' in r]
        
        # Basic statistics
        total_requests = len(results)
        successful_requests = len(successful_results)
        failed_requests = len(failed_results)
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Performance metrics
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Percentiles
        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95) if sorted_times else 0
        p99_index = int(len(sorted_times) * 0.99) if sorted_times else 0
        p95_response_time = sorted_times[p95_index] if p95_index < len(sorted_times) else 0
        p99_response_time = sorted_times[p99_index] if p99_index < len(sorted_times) else 0
        
        # Throughput
        requests_per_second = total_requests / total_duration if total_duration > 0 else 0
        
        # Error analysis
        error_counts = {}
        for result in failed_results:
            error = result.get('error', 'Unknown error')
            error_counts[error] = error_counts.get(error, 0) + 1
        
        # Scenario breakdown (if mixed scenarios)
        scenario_stats = {}
        for result in results:
            scenario = result.get('scenario', 'create_payment')
            if scenario not in scenario_stats:
                scenario_stats[scenario] = {'total': 0, 'successful': 0, 'failed': 0}
            
            scenario_stats[scenario]['total'] += 1
            if result.get('success', False):
                scenario_stats[scenario]['successful'] += 1
            else:
                scenario_stats[scenario]['failed'] += 1
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': success_rate,
            'test_duration': total_duration,
            'requests_per_second': requests_per_second,
            'avg_response_time': avg_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'p95_response_time': p95_response_time,
            'p99_response_time': p99_response_time,
            'error_counts': error_counts,
            'scenario_stats': scenario_stats
        }
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted test report."""
        print("\n" + "="*80)
        print("🚀 MCP PAYMENTS LOAD TEST REPORT")
        print("="*80)
        
        print(f"\n📊 Overall Statistics:")
        print(f"   Total Requests: {report['total_requests']:,}")
        print(f"   Successful: {report['successful_requests']:,}")
        print(f"   Failed: {report['failed_requests']:,}")
        print(f"   Success Rate: {report['success_rate']:.1f}%")
        print(f"   Test Duration: {report['test_duration']:.2f} seconds")
        print(f"   Requests/Second: {report['requests_per_second']:.1f}")
        
        if report['successful_requests'] > 0:
            print(f"\n⚡ Performance Metrics:")
            print(f"   Min Response Time: {report['min_response_time']*1000:.1f}ms")
            print(f"   Max Response Time: {report['max_response_time']*1000:.1f}ms")
            print(f"   Avg Response Time: {report['avg_response_time']*1000:.1f}ms")
            print(f"   95th Percentile: {report['p95_response_time']*1000:.1f}ms")
            print(f"   99th Percentile: {report['p99_response_time']*1000:.1f}ms")
        
        if report['scenario_stats']:
            print(f"\n🎯 Scenario Breakdown:")
            for scenario, stats in report['scenario_stats'].items():
                success_rate = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"   {scenario}: {stats['total']} total, {stats['successful']} success ({success_rate:.1f}%)")
        
        if report['error_counts']:
            print(f"\n❌ Error Analysis:")
            for error, count in sorted(report['error_counts'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {error}: {count} occurrences")
        
        print(f"\n🎯 Performance Assessment:")
        if report['success_rate'] >= 95:
            print("   ✅ EXCELLENT - High success rate")
        elif report['success_rate'] >= 90:
            print("   ⚠️  GOOD - Acceptable success rate")
        else:
            print("   ❌ POOR - Low success rate, investigate issues")
        
        if report['avg_response_time'] < 0.2:  # 200ms
            print("   ✅ EXCELLENT - Fast response times")
        elif report['avg_response_time'] < 0.5:  # 500ms
            print("   ⚠️  GOOD - Acceptable response times")
        else:
            print("   ❌ POOR - Slow response times, optimization needed")
        
        print("\n" + "="*80)

def main():
    """Main function to run load tests."""
    parser = argparse.ArgumentParser(description='MCP Payments Load Tester')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the MCP server (default: http://localhost:8000)')
    parser.add_argument('--total', type=int, default=1000,
                       help='Total number of requests to send (default: 1000)')
    parser.add_argument('--concurrent', type=int, default=100,
                       help='Number of concurrent requests (default: 100)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds (default: 30)')
    parser.add_argument('--mixed', action='store_true',
                       help='Use mixed scenarios (create_payment, verify_payment, get_wallet_balance)')
    parser.add_argument('--quick', action='store_true',
                       help='Quick test with 100 requests and 10 concurrent')
    
    args = parser.parse_args()
    
    # Quick test override
    if args.quick:
        args.total = 100
        args.concurrent = 10
        print("🏃 Running quick test mode")
    
    # Validate arguments
    if args.concurrent > args.total:
        args.concurrent = args.total
        print(f"⚠️  Adjusted concurrent requests to {args.concurrent} (cannot exceed total)")
    
    # Create and run tester
    tester = PaymentLoadTester(
        base_url=args.url,
        total_payments=args.total,
        concurrent=args.concurrent,
        timeout=args.timeout
    )
    
    try:
        print(f"🚀 Starting MCP Payments Load Test")
        print(f"📡 Target: {args.url}")
        print(f"📊 Configuration: {args.total} total, {args.concurrent} concurrent")
        
        report = asyncio.run(tester.run_load_test(mixed_scenarios=args.mixed))
        
        # Exit with appropriate code
        if report['failed_requests'] > report['total_requests'] * 0.1:  # More than 10% failures
            logger.error("❌ Load test failed with high error rate")
            sys.exit(1)
        else:
            logger.info("✅ Load test completed successfully")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("🛑 Load test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Load test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
