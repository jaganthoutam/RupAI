# MCP Payments Enterprise - Testing Guide

## 🧪 Comprehensive Testing Framework

This document outlines the complete testing strategy for the MCP Payments Enterprise system, covering unit tests, integration tests, end-to-end tests, and performance testing.

---

## 📋 Test Structure Overview

```
tests/
├── unit/                     # Unit tests for individual components
├── integration/              # Integration tests for service interactions
├── e2e/                     # End-to-end workflow tests
│   └── test_mcp_payments_e2e.py
├── performance/             # Load and performance tests
│   └── locustfile.py
├── fixtures/                # Test data and fixtures
└── requirements.txt         # Test dependencies
```

---

## 🚀 Quick Start Testing

### 1. Install Test Dependencies
```bash
# Install test requirements
pip install -r tests/requirements.txt

# Or use Make command
make install-test
```

### 2. Start System for Testing
```bash
# Start all services
make docker-up

# Or manually
docker-compose up -d
```

### 3. Run Tests

#### E2E Tests (Recommended)
```bash
# Run complete E2E test suite
make test-e2e

# Or run directly
python3 scripts/run_e2e_tests.py
```

#### Unit Tests
```bash
# Run unit tests
make test

# With coverage
make test-coverage
```

#### Performance Tests
```bash
# Run load tests
make test-performance

# Custom load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

---

## 🎯 End-to-End Test Suite

### Test Coverage

The E2E test suite covers 8 comprehensive test scenarios:

| Test | Description | Coverage |
|------|-------------|----------|
| **MCP Tools Discovery** | Validates MCP protocol compliance and tool availability | Protocol, Tool Registry |
| **Payment Creation** | Tests complete payment workflow via MCP | Payments, MCP Integration |
| **Wallet Operations** | Validates wallet balance and management | Wallets, MCP Tools |
| **Analytics Endpoints** | Tests all analytics APIs | Revenue, Users, Payments Analytics |
| **Monitoring Endpoints** | Validates system monitoring | Metrics, Status, Alerts |
| **Compliance & Audit** | Tests audit logging and compliance | Audit Logs, Compliance |
| **Concurrent Requests** | Tests system under concurrent load | Concurrency, Stability |
| **Error Handling** | Validates proper error responses | Error Handling, Resilience |

### Expected Test Results

**🏆 Success Criteria:**
- ✅ All 8 tests passing (100% success rate)
- ✅ Response times < 200ms average
- ✅ Zero critical errors
- ✅ MCP protocol fully compliant

**⚠️ Acceptable Results:**
- ✅ 6-7 tests passing (75-87% success rate)
- ⚠️ Response times < 500ms average
- ⚠️ Minor non-critical issues

**❌ Failure Indicators:**
- ❌ < 6 tests passing (< 75% success rate)
- ❌ Response times > 500ms average
- ❌ Critical system errors

---

## 📊 Performance Testing

### Load Test Scenarios

The Locust performance test simulates realistic user behavior:

#### User Types
1. **PaymentUser** - Creates payments, verifies transactions
2. **AnalyticsUser** - Fetches dashboard analytics
3. **MonitoringUser** - Checks system health
4. **WalletUser** - Manages wallet operations
5. **ComplianceUser** - Reviews audit logs

#### Performance Benchmarks

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| **Average Response Time** | < 150ms | < 300ms | > 500ms |
| **95th Percentile** | < 300ms | < 500ms | > 1000ms |
| **Throughput** | > 100 RPS | > 50 RPS | < 10 RPS |
| **Error Rate** | < 0.1% | < 1% | > 5% |
| **Concurrent Users** | 100+ | 50+ | < 10 |

#### Running Performance Tests

```bash
# Quick performance test (30 seconds, 50 users)
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --headless -u 50 -r 5 -t 30s

# Extended load test (5 minutes, 100 users)
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --headless -u 100 -r 10 -t 300s

# Interactive web UI
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000
# Then open http://localhost:8089
```

---

## 🔍 Test Categories Detail

### 1. MCP Protocol Testing

**Validates:**
- MCP 2.0 JSON-RPC compliance
- Tool discovery and registration
- Error handling and responses
- Protocol message formatting

**Key Tests:**
```python
# Tool discovery
POST /mcp
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": "test-1"
}

# Tool execution
POST /mcp
{
  "jsonrpc": "2.0", 
  "method": "tools/call",
  "params": {
    "name": "create_payment",
    "arguments": {...}
  }
}
```

### 2. Payment Workflow Testing

**Validates:**
- Payment creation via MCP
- Payment verification and status
- Refund processing
- Transaction state management

**Test Scenarios:**
- ✅ Valid payment creation
- ✅ Invalid payment data handling
- ✅ Duplicate idempotency key handling
- ✅ Payment verification workflow
- ✅ Multi-currency support

### 3. Analytics API Testing

**Validates:**
- Revenue analytics computation
- User behavior analysis
- Payment trend analysis
- Fraud detection metrics

**Endpoints Tested:**
- `GET /api/v1/analytics/revenue?days=N`
- `GET /api/v1/analytics/payments?days=N`
- `GET /api/v1/analytics/users?days=N`
- `GET /api/v1/analytics/fraud?days=N`

### 4. System Monitoring Testing

**Validates:**
- Real-time system metrics
- Health check endpoints
- Alert system functionality
- Performance monitoring

**Metrics Verified:**
- CPU and memory usage
- Response time tracking
- Database performance
- Cache hit rates

---

## 🛠 Test Environment Setup

### Prerequisites

1. **Docker & Docker Compose**
   - All services containerized
   - Isolated test environment
   - Reproducible test conditions

2. **Python Dependencies**
   ```bash
   pip install pytest httpx asyncio locust
   ```

3. **System Requirements**
   - 4GB+ RAM available
   - Port 8000 free for backend
   - Port 3000 free for frontend

### Environment Variables

```bash
# Test configuration
export TEST_BASE_URL="http://localhost:8000"
export TEST_TIMEOUT=30
export TEST_PARALLEL_REQUESTS=10

# Database (uses Docker containers)
export POSTGRES_DB=payments_test
export POSTGRES_USER=test_user
export POSTGRES_PASSWORD=test_pass

# Redis (uses Docker containers)
export REDIS_URL=redis://localhost:6379/1
```

---

## 📈 Continuous Integration

### GitHub Actions Integration

```yaml
# .github/workflows/test.yml
name: MCP Payments Test Suite

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: make install-test
      
      - name: Start services
        run: make docker-up
      
      - name: Run E2E tests
        run: make test-e2e
      
      - name: Run performance tests
        run: make test-performance
      
      - name: Cleanup
        run: make docker-down
```

### Make Commands Summary

```bash
# Development
make help               # Show all available commands
make start              # Start entire system
make stop               # Stop all services
make restart            # Restart system

# Testing
make test               # Unit tests
make test-e2e           # End-to-end tests
make test-all           # All tests
make test-coverage      # Coverage report
make test-performance   # Load testing

# Quality
make lint               # Code linting
make format             # Code formatting
make type-check         # Type checking
make security-scan      # Security analysis

# Monitoring
make health-check       # System health
make quick-test         # Quick validation
make metrics            # System metrics
```

---

## 🐛 Debugging Test Failures

### Common Issues & Solutions

#### 1. Connection Refused Errors
```bash
# Check if services are running
make status

# Restart services
make restart

# Check health
make health-check
```

#### 2. Timeout Errors
```bash
# Increase timeout in test config
export TEST_TIMEOUT=60

# Check system resources
docker stats

# View logs
make logs
```

#### 3. MCP Protocol Errors
```bash
# Check MCP endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":"test"}'

# Verify tool registration
make quick-test
```

#### 4. Database Connection Issues
```bash
# Reset database
make db-reset

# Check database status
docker-compose exec postgres psql -U payments -c '\l'
```

---

## 📊 Test Reporting

### Test Result Formats

#### E2E Test Report
```
🎯 MCP PAYMENTS E2E TEST RESULTS
============================================================
Total Tests:     8
Passed:          6 ✅
Failed:          2 ❌  
Success Rate:    75.0%
Total Time:      1.14 seconds

📊 DETAILED RESULTS:
 1. ✅ MCP Tools Discovery (Tools discovered: 15)
 2. ✅ Payment Creation (Payment ID: abc123...)
 3. ❌ Wallet Operations (Wallets found: 0)
 4. ✅ Analytics Endpoints
 5. ✅ Monitoring Endpoints  
 6. ✅ Compliance Endpoints
 7. ✅ Concurrent Requests (10/10 successful)
 8. ❌ Error Handling (1/3 handled correctly)
```

#### Performance Test Report
```
📊 PERFORMANCE TEST RESULTS
============================================================
Total Requests: 1,247
Total Failures: 12
Average Response Time: 145.32ms
Max Response Time: 892.15ms
Requests/sec: 41.57
Failure Rate: 0.96%
============================================================
```

---

## 🎯 Best Practices

### Writing Tests

1. **Use Descriptive Names**
   ```python
   async def test_payment_creation_with_valid_card_data(self):
   async def test_wallet_balance_retrieval_for_existing_customer(self):
   ```

2. **Isolate Tests**
   - Each test should be independent
   - Use unique test data
   - Clean up after tests

3. **Test Real Scenarios**
   - Use realistic data amounts
   - Test edge cases
   - Simulate actual user behavior

4. **Assert Meaningful Results**
   ```python
   assert response.status_code == 200
   assert "payment_id" in response_data
   assert response_data["amount"] == expected_amount
   ```

### Performance Testing

1. **Gradual Load Increase**
   - Start with low user count
   - Gradually increase load
   - Monitor system behavior

2. **Test Different Scenarios**
   - Normal usage patterns
   - Peak load conditions
   - Stress testing beyond capacity

3. **Monitor System Resources**
   - CPU and memory usage
   - Database performance
   - Network latency

---

## 🔮 Future Enhancements

### Planned Test Improvements

1. **Visual Regression Testing**
   - Frontend UI component testing
   - Cross-browser compatibility
   - Mobile responsiveness

2. **Security Testing**
   - Penetration testing
   - Vulnerability scanning
   - Authentication bypass attempts

3. **Chaos Engineering**
   - Random service failures
   - Network partition testing
   - Database failure scenarios

4. **Contract Testing**
   - API contract validation
   - Schema evolution testing
   - Backward compatibility

---

## 📞 Support & Troubleshooting

### Getting Help

1. **Check Test Logs**
   ```bash
   make logs
   ```

2. **Run Health Check**
   ```bash
   make health-check
   ```

3. **View System Status**
   ```bash
   make status
   ```

4. **Contact Team**
   - Development team: dev@mcppayments.com
   - DevOps team: devops@mcppayments.com
   - QA team: qa@mcppayments.com

---

**Last Updated:** January 2024  
**Version:** 2.0.0  
**Documentation:** Complete testing framework for MCP Payments Enterprise 