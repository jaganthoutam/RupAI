#!/usr/bin/env python3
"""
Enterprise Load Testing Script for MCP Payments
Tests end-to-end functionality with 1000 concurrent payments
"""

import asyncio
import aiohttp
import json
import time
import logging
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from uuid import uuid4
from decimal import Decimal
import random
import argparse
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'load_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestConfig:
    """Test configuration parameters."""
    base_url: str = os.getenv('API_BASE_URL', 'http://localhost:8000')
    mcp_endpoint: str = '/mcp'
    api_endpoint: str = '/api/v1'
    
    # Load test parameters
    total_payments: int = 1000
    concurrent_payments: int = 100
    ramp_up_time: int = 30  # seconds
    
    # Payment parameters
    currencies: List[str] = None
    payment_methods: List[str] = None
    amount_range: tuple = (10.0, 1000.0)
    
    # Timeout settings
    request_timeout: int = 30
    connection_timeout: int = 10
    
    # Test scenarios
    scenarios: Dict[str, float] = None  # scenario_name: weight
    
    def __post_init__(self):
        if self.currencies is None:
            self.currencies = ['USD', 'EUR', 'GBP', 'INR', 'JPY']
        if self.payment_methods is None:
            self.payment_methods = ['card', 'bank_transfer', 'wallet', 'upi']
        if self.scenarios is None:
            self.scenarios = {
                'create_payment': 0.5,
                'verify_payment': 0.2,
                'get_wallet_balance': 0.15,
                'transfer_funds': 0.1,
                'refund_payment': 0.05
            }

@dataclass
class TestResult:
    """Individual test result."""
    scenario: str
    success: bool
    response_time: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class LoadTestReport:
    """Comprehensive load test report."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_time: float = 0.0
    
    # Performance metrics
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    avg_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # Throughput metrics
    requests_per_second: float = 0.0
    
    # Scenario-specific metrics
    scenario_stats: Dict[str, Dict[str, Any]] = None
    
    # Error analysis
    error_distribution: Dict[str, int] = None
    
    def __post_init__(self):
        if self.scenario_stats is None:
            self.scenario_stats = {}
        if self.error_distribution is None:
            self.error_distribution = defaultdict(int)

class PaymentDataGenerator:
    """Generate realistic payment test data."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.customer_ids = [str(uuid4()) for _ in range(100)]  # Pool of customer IDs
        self.payment_ids = []  # Track created payment IDs for verification/refunds
        
    def generate_payment_data(self) -> Dict[str, Any]:
        """Generate realistic payment data."""
        return {
            'amount': round(random.uniform(*self.config.amount_range), 2),
            'currency': random.choice(self.config.currencies),
            'method': random.choice(self.config.payment_methods),
            'customer_id': random.choice(self.customer_ids),
            'description': f'Load test payment {uuid4().hex[:8]}',
            'metadata': {
                'test_run': True,
                'load_test_id': uuid4().hex,
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def generate_wallet_data(self) -> Dict[str, Any]:
        """Generate wallet operation data."""
        return {
            'customer_id': random.choice(self.customer_ids),
            'currency': random.choice(self.config.currencies)
        }
    
    def generate_transfer_data(self) -> Dict[str, Any]:
        """Generate transfer data."""
        return {
            'from_customer_id': random.choice(self.customer_ids),
            'to_customer_id': random.choice(self.customer_ids),
            'amount': round(random.uniform(10.0, 500.0), 2),
            'currency': random.choice(self.config.currencies),
            'description': f'Load test transfer {uuid4().hex[:8]}'
        }

class MCPPaymentTester:
    """MCP Payment system load tester."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.data_generator = PaymentDataGenerator(config)
        self.results: List[TestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self._lock = threading.Lock()
        
    async def setup_session(self):
        """Initialize HTTP session with proper configuration."""
        timeout = aiohttp.ClientTimeout(
            total=self.config.request_timeout,
            connect=self.config.connection_timeout
        )
        
        connector = aiohttp.TCPConnector(
            limit=200,  # Connection pool size
            limit_per_host=50,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'MCP-Payments-LoadTester/1.0'
            }
        )
    
    async def close_session(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
    
    async def make_mcp_request(self, tool_name: str, arguments: Dict[str, Any]) -> TestResult:
        """Make an MCP tool call request."""
        start_time = time.time()
        
        payload = {
            'jsonrpc': '2.0',
            'id': uuid4().hex,
            'method': 'tools/call',
            'params': {
                'name': tool_name,
                'arguments': arguments
            }
        }
        
        try:
            async with self.session.post(
                f"{self.config.base_url}{self.config.mcp_endpoint}",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    result_data = await response.json()
                    
                    # Check for MCP-level errors
                    if 'error' in result_data:
                        return TestResult(
                            scenario=tool_name,
                            success=False,
                            response_time=response_time,
                            status_code=response.status,
                            error_message=result_data['error'].get('message', 'MCP Error')
                        )
                    
                    # Check for tool-level errors
                    if result_data.get('result', {}).get('isError', False):
                        error_msg = 'Tool execution error'
                        if 'content' in result_data['result']:
                            error_msg = result_data['result']['content'][0].get('text', error_msg)
                        
                        return TestResult(
                            scenario=tool_name,
                            success=False,
                            response_time=response_time,
                            status_code=response.status,
                            error_message=error_msg
                        )
                    
                    # Success case
                    return TestResult(
                        scenario=tool_name,
                        success=True,
                        response_time=response_time,
                        status_code=response.status
                    )
                else:
                    error_text = await response.text()
                    return TestResult(
                        scenario=tool_name,
                        success=False,
                        response_time=response_time,
                        status_code=response.status,
                        error_message=f"HTTP {response.status}: {error_text[:200]}"
                    )
                    
        except asyncio.TimeoutError:
            return TestResult(
                scenario=tool_name,
                success=False,
                response_time=time.time() - start_time,
                error_message="Request timeout"
            )
        except Exception as e:
            return TestResult(
                scenario=tool_name,
                success=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def test_create_payment(self) -> TestResult:
        """Test payment creation."""
        payment_data = self.data_generator.generate_payment_data()
        payment_data['idempotency_key'] = f"test_{uuid4().hex}"
        
        result = await self.make_mcp_request('create_payment', payment_data)
        
        # Store payment ID for later verification/refund tests
        if result.success:
            with self._lock:
                self.data_generator.payment_ids.append(f"pay_{uuid4().hex[:12]}")
        
        return result
    
    async def test_verify_payment(self) -> TestResult:
        """Test payment verification."""
        with self._lock:
            if not self.data_generator.payment_ids:
                # Create dummy payment ID if none available
                payment_id = f"pay_{uuid4().hex[:12]}"
            else:
                payment_id = random.choice(self.data_generator.payment_ids)
        
        return await self.make_mcp_request('verify_payment', {
            'payment_id': payment_id
        })
    
    async def test_get_wallet_balance(self) -> TestResult:
        """Test wallet balance retrieval."""
        wallet_data = self.data_generator.generate_wallet_data()
        return await self.make_mcp_request('get_wallet_balance', wallet_data)
    
    async def test_transfer_funds(self) -> TestResult:
        """Test fund transfer."""
        transfer_data = self.data_generator.generate_transfer_data()
        transfer_data['idempotency_key'] = f"transfer_{uuid4().hex}"
        
        return await self.make_mcp_request('transfer_funds', transfer_data)
    
    async def test_refund_payment(self) -> TestResult:
        """Test payment refund."""
        with self._lock:
            if not self.data_generator.payment_ids:
                payment_id = f"pay_{uuid4().hex[:12]}"
            else:
                payment_id = random.choice(self.data_generator.payment_ids)
        
        return await self.make_mcp_request('refund_payment', {
            'payment_id': payment_id,
            'reason': 'Load test refund',
            'idempotency_key': f"refund_{uuid4().hex}"
        })
    
    async def execute_scenario(self) -> TestResult:
        """Execute a random test scenario based on weights."""
        scenario_choices = list(self.config.scenarios.keys())
        scenario_weights = list(self.config.scenarios.values())
        
        scenario = random.choices(scenario_choices, weights=scenario_weights)[0]
        
        if scenario == 'create_payment':
            return await self.test_create_payment()
        elif scenario == 'verify_payment':
            return await self.test_verify_payment()
        elif scenario == 'get_wallet_balance':
            return await self.test_get_wallet_balance()
        elif scenario == 'transfer_funds':
            return await self.test_transfer_funds()
        elif scenario == 'refund_payment':
            return await self.test_refund_payment()
        else:
            raise ValueError(f"Unknown scenario: {scenario}")
    
    def record_result(self, result: TestResult):
        """Thread-safe result recording."""
        with self._lock:
            self.results.append(result)
    
    async def run_concurrent_tests(self, num_requests: int) -> List[TestResult]:
        """Run concurrent test requests."""
        semaphore = asyncio.Semaphore(self.config.concurrent_payments)
        
        async def bounded_test():
            async with semaphore:
                return await self.execute_scenario()
        
        tasks = [bounded_test() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and convert to TestResult
        valid_results = []
        for result in results:
            if isinstance(result, TestResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                valid_results.append(TestResult(
                    scenario='unknown',
                    success=False,
                    response_time=0.0,
                    error_message=str(result)
                ))
        
        return valid_results
    
    def generate_report(self, results: List[TestResult]) -> LoadTestReport:
        """Generate comprehensive test report."""
        if not results:
            return LoadTestReport()
        
        report = LoadTestReport()
        report.total_requests = len(results)
        
        successful_results = [r for r in results if r.success]
        report.successful_requests = len(successful_results)
        report.failed_requests = report.total_requests - report.successful_requests
        
        if successful_results:
            response_times = [r.response_time for r in successful_results]
            report.min_response_time = min(response_times)
            report.max_response_time = max(response_times)
            report.avg_response_time = statistics.mean(response_times)
            report.p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            report.p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        
        # Calculate scenario-specific stats
        scenario_groups = defaultdict(list)
        for result in results:
            scenario_groups[result.scenario].append(result)
        
        for scenario, scenario_results in scenario_groups.items():
            successful = [r for r in scenario_results if r.success]
            report.scenario_stats[scenario] = {
                'total': len(scenario_results),
                'successful': len(successful),
                'failed': len(scenario_results) - len(successful),
                'success_rate': len(successful) / len(scenario_results) * 100,
                'avg_response_time': statistics.mean([r.response_time for r in successful]) if successful else 0
            }
        
        # Error distribution
        for result in results:
            if not result.success:
                error_key = result.error_message or 'Unknown Error'
                report.error_distribution[error_key] += 1
        
        return report
    
    def print_report(self, report: LoadTestReport, test_duration: float):
        """Print formatted test report."""
        print("\n" + "="*80)
        print("MCP PAYMENTS LOAD TEST REPORT")
        print("="*80)
        
        print(f"\n📊 Overall Statistics:")
        print(f"   Total Requests: {report.total_requests}")
        print(f"   Successful: {report.successful_requests}")
        print(f"   Failed: {report.failed_requests}")
        print(f"   Success Rate: {(report.successful_requests/report.total_requests*100):.1f}%")
        print(f"   Test Duration: {test_duration:.1f} seconds")
        print(f"   Requests/Second: {report.total_requests/test_duration:.1f}")
        
        if report.successful_requests > 0:
            print(f"\n⚡ Performance Metrics:")
            print(f"   Min Response Time: {report.min_response_time*1000:.1f}ms")
            print(f"   Max Response Time: {report.max_response_time*1000:.1f}ms")
            print(f"   Avg Response Time: {report.avg_response_time*1000:.1f}ms")
            print(f"   95th Percentile: {report.p95_response_time*1000:.1f}ms")
            print(f"   99th Percentile: {report.p99_response_time*1000:.1f}ms")
        
        print(f"\n🎯 Scenario Breakdown:")
        for scenario, stats in report.scenario_stats.items():
            print(f"   {scenario}:")
            print(f"     Total: {stats['total']}, Success: {stats['successful']}, "
                  f"Rate: {stats['success_rate']:.1f}%, "
                  f"Avg Time: {stats['avg_response_time']*1000:.1f}ms")
        
        if report.error_distribution:
            print(f"\n❌ Error Analysis:")
            for error, count in sorted(report.error_distribution.items(), 
                                     key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {error}: {count} occurrences")
        
        print("\n" + "="*80)
    
    async def run_load_test(self) -> LoadTestReport:
        """Execute the complete load test."""
        logger.info(f"Starting load test with {self.config.total_payments} payments")
        logger.info(f"Configuration: {asdict(self.config)}")
        
        await self.setup_session()
        
        try:
            start_time = time.time()
            
            # Run tests in batches to control load
            batch_size = min(self.config.concurrent_payments, self.config.total_payments)
            batches = [self.config.total_payments // batch_size] * (self.config.total_payments // batch_size)
            if self.config.total_payments % batch_size:
                batches.append(self.config.total_payments % batch_size)
            
            all_results = []
            for i, batch_requests in enumerate(batches):
                logger.info(f"Running batch {i+1}/{len(batches)} with {batch_requests} requests")
                
                batch_results = await self.run_concurrent_tests(batch_requests)
                all_results.extend(batch_results)
                
                # Add delay between batches for ramp-up
                if i < len(batches) - 1:
                    await asyncio.sleep(self.config.ramp_up_time / len(batches))
            
            test_duration = time.time() - start_time
            
            # Generate and display report
            report = self.generate_report(all_results)
            self.print_report(report, test_duration)
            
            # Save detailed results to file
            self.save_detailed_results(all_results, report, test_duration)
            
            return report
            
        finally:
            await self.close_session()
    
    def save_detailed_results(self, results: List[TestResult], report: LoadTestReport, duration: float):
        """Save detailed test results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"load_test_results_{timestamp}.json"
        
        data = {
            'test_config': asdict(self.config),
            'test_summary': {
                'total_requests': report.total_requests,
                'successful_requests': report.successful_requests,
                'failed_requests': report.failed_requests,
                'test_duration': duration,
                'requests_per_second': report.total_requests / duration,
                'success_rate': report.successful_requests / report.total_requests * 100
            },
            'performance_metrics': {
                'min_response_time': report.min_response_time,
                'max_response_time': report.max_response_time,
                'avg_response_time': report.avg_response_time,
                'p95_response_time': report.p95_response_time,
                'p99_response_time': report.p99_response_time
            },
            'scenario_stats': report.scenario_stats,
            'error_distribution': dict(report.error_distribution),
            'detailed_results': [
                {
                    'scenario': r.scenario,
                    'success': r.success,
                    'response_time': r.response_time,
                    'status_code': r.status_code,
                    'error_message': r.error_message,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Detailed results saved to {filename}")

def main():
    """Main function to run load tests."""
    parser = argparse.ArgumentParser(description='MCP Payments Load Tester')
    parser.add_argument('--base-url', default='http://localhost:8000', 
                       help='Base URL of the MCP server')
    parser.add_argument('--total-payments', type=int, default=1000,
                       help='Total number of payments to test')
    parser.add_argument('--concurrent', type=int, default=100,
                       help='Number of concurrent requests')
    parser.add_argument('--ramp-up', type=int, default=30,
                       help='Ramp-up time in seconds')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    # Create test configuration
    config = TestConfig(
        base_url=args.base_url,
        total_payments=args.total_payments,
        concurrent_payments=args.concurrent,
        ramp_up_time=args.ramp_up,
        request_timeout=args.timeout
    )
    
    # Run the load test
    tester = MCPPaymentTester(config)
    
    try:
        report = asyncio.run(tester.run_load_test())
        
        # Exit with error code if test failed significantly
        if report.failed_requests > report.total_requests * 0.1:  # More than 10% failures
            logger.error("Load test failed with high error rate")
            sys.exit(1)
        else:
            logger.info("Load test completed successfully")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Load test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Load test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 