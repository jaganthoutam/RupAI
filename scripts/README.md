# 🚀 MCP Payments Load Testing Scripts

This directory contains comprehensive load testing scripts for the MCP Payments system, designed to test end-to-end functionality with up to 1000+ concurrent payments.

## 📋 Overview

The load testing suite provides:
- **Concurrent Payment Testing**: Test 1000+ simultaneous payment requests
- **Mixed Scenario Testing**: Test multiple MCP tools (create_payment, verify_payment, get_wallet_balance)
- **Performance Metrics**: Detailed response time, throughput, and success rate analysis
- **Error Analysis**: Comprehensive error reporting and categorization
- **Configurable Parameters**: Flexible testing configuration

## 🛠️ Scripts Available

### 1. `simple_load_test.py` - Main Load Testing Script

**Features:**
- Tests MCP payment creation, verification, and wallet operations
- Configurable concurrent requests and total volume
- Comprehensive performance reporting
- Mixed scenario testing support
- Error analysis and categorization

**Usage:**
```bash
# Basic test with 1000 payments, 100 concurrent
python scripts/simple_load_test.py

# Custom configuration
python scripts/simple_load_test.py --url http://localhost:8000 --total 1000 --concurrent 100

# Quick test mode
python scripts/simple_load_test.py --quick

# Mixed scenarios (different MCP tools)
python scripts/simple_load_test.py --mixed --total 500 --concurrent 50

# Custom timeout
python scripts/simple_load_test.py --timeout 60 --total 2000 --concurrent 200
```

**Parameters:**
- `--url`: Base URL of the MCP server (default: http://localhost:8000)
- `--total`: Total number of requests (default: 1000)
- `--concurrent`: Number of concurrent requests (default: 100)
- `--timeout`: Request timeout in seconds (default: 30)
- `--mixed`: Use mixed scenarios (create_payment, verify_payment, get_wallet_balance)
- `--quick`: Quick test mode (100 requests, 10 concurrent)

## 📊 Test Scenarios

### 1. Payment Creation Test
- Creates realistic payment requests with random amounts, currencies, and methods
- Tests MCP `create_payment` tool
- Validates response format and success rates

### 2. Payment Verification Test
- Verifies existing payment IDs
- Tests MCP `verify_payment` tool
- Checks payment status retrieval

### 3. Wallet Balance Test
- Retrieves wallet balances for random customers
- Tests MCP `get_wallet_balance` tool
- Validates balance information format

### 4. Mixed Scenario Test
- Randomly executes different MCP tools
- Simulates real-world usage patterns
- Tests system under varied load

## 🎯 Performance Targets

Based on the MCP Payments specification:

| Operation | Target Latency | Throughput | Error Rate |
|-----------|----------------|------------|------------|
| Create Payment | < 150ms p95 | 1000 TPS | < 0.1% |
| Verify Payment | < 50ms p95 | 5000 TPS | < 0.01% |
| Wallet Balance | < 25ms p95 | 10000 TPS | < 0.001% |

## 📈 Sample Output

```
================================================================================
🚀 MCP PAYMENTS LOAD TEST REPORT
================================================================================

📊 Overall Statistics:
   Total Requests: 1,000
   Successful: 987
   Failed: 13
   Success Rate: 98.7%
   Test Duration: 12.3 seconds
   Requests/Second: 81.3

⚡ Performance Metrics:
   Min Response Time: 45.2ms
   Max Response Time: 1,234.5ms
   Avg Response Time: 156.7ms
   95th Percentile: 289.3ms
   99th Percentile: 567.8ms

🎯 Scenario Breakdown:
   create_payment: 500 total, 492 success (98.4%)
   verify_payment: 300 total, 298 success (99.3%)
   get_wallet_balance: 200 total, 197 success (98.5%)

❌ Error Analysis:
   Connection timeout: 8 occurrences
   HTTP 500: Internal Server Error: 3 occurrences
   JSON decode error: 2 occurrences

🎯 Performance Assessment:
   ✅ EXCELLENT - High success rate
   ⚠️  GOOD - Acceptable response times
================================================================================
```

## 🚀 Quick Start Guide

### 1. Prerequisites
```bash
# Ensure MCP server is running
docker-compose up -d

# Install dependencies (if not already installed)
pip install aiohttp asyncio
```

### 2. Basic Load Test
```bash
# Run a quick test to verify everything works
python scripts/simple_load_test.py --quick

# Run full load test
python scripts/simple_load_test.py
```

### 3. Advanced Testing
```bash
# High-volume test
python scripts/simple_load_test.py --total 5000 --concurrent 500

# Mixed scenario test
python scripts/simple_load_test.py --mixed --total 2000 --concurrent 200

# Extended timeout for slow networks
python scripts/simple_load_test.py --timeout 60
```

## 🔧 Configuration

### Environment Variables
The load tester respects these environment variables:
- `API_BASE_URL`: Default base URL for testing
- `LOAD_TEST_CONCURRENT`: Default concurrent requests
- `LOAD_TEST_TOTAL`: Default total requests
- `LOAD_TEST_TIMEOUT`: Default timeout

### Test Data Configuration
The script generates realistic test data:
- **Currencies**: USD, EUR, GBP, INR, JPY
- **Payment Methods**: card, bank_transfer, wallet, upi
- **Amount Range**: $10.00 - $1,000.00
- **Customer IDs**: Random UUIDs
- **Idempotency Keys**: Unique per request

## 📝 Interpreting Results

### Success Rate Analysis
- **95%+**: Excellent - System handling load well
- **90-95%**: Good - Acceptable performance
- **<90%**: Poor - Investigation needed

### Response Time Analysis
- **<200ms avg**: Excellent performance
- **200-500ms avg**: Good performance
- **>500ms avg**: Poor performance - optimization needed

### Error Categories
- **Connection timeouts**: Network or server overload
- **HTTP 5xx errors**: Server-side issues
- **JSON decode errors**: Response format issues
- **MCP protocol errors**: Tool execution failures

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Solution: Ensure MCP server is running on the specified URL
   Check: docker-compose ps
   ```

2. **High Error Rate**
   ```
   Solution: Reduce concurrent requests or increase timeout
   Try: --concurrent 50 --timeout 60
   ```

3. **Slow Performance**
   ```
   Solution: Check server resources and database connections
   Monitor: docker stats
   ```

### Debug Mode
```bash
# Enable verbose logging
export PYTHONPATH=.
python -v scripts/simple_load_test.py --quick
```

## 📊 Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run Load Tests
  run: |
    python scripts/simple_load_test.py --total 100 --concurrent 10
    if [ $? -ne 0 ]; then
      echo "Load test failed"
      exit 1
    fi
```

### Performance Regression Detection
```bash
# Save baseline results
python scripts/simple_load_test.py > baseline_results.txt

# Compare with current results
python scripts/simple_load_test.py > current_results.txt
# Add comparison logic as needed
```

## 🔮 Future Enhancements

- **Real Payment Provider Testing**: Integration with actual Stripe/Razorpay APIs
- **Database Load Testing**: Direct database operation testing
- **WebSocket Testing**: Real-time notification testing
- **Chaos Engineering**: Fault injection testing
- **Performance Profiling**: Detailed bottleneck analysis

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs: `docker-compose logs mcp-server`
3. Check system resources: `docker stats`
4. Verify configuration: Review `env.example` file

---

**Happy Load Testing! 🚀** 