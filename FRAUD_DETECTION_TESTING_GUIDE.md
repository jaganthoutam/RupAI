# 🔍 Fraud Detection & Prevention Testing Guide

## 📋 **Overview**

This guide shows you how to generate realistic fraud detection data and test the AI-powered fraud prevention system in the MCP Payments platform.

---

## 🎯 **What You'll Learn**

- ✅ Generate realistic fraud patterns and test data
- ✅ Test AI-powered fraud detection APIs
- ✅ Monitor fraud analytics in real-time dashboards  
- ✅ Simulate various fraud scenarios
- ✅ Analyze fraud detection performance

---

## 🚀 **Quick Start**

### **1. Generate Fraud Test Data**

```bash
# Generate comprehensive fraud test data
python scripts/generate_fraud_data.py --customers 50 --normal-txns 200 --fraud-txns 25

# Quick test with smaller dataset
python scripts/generate_fraud_data.py --customers 10 --normal-txns 50 --fraud-txns 5
```

**This creates:**
- 👥 **50 realistic customers** with different risk profiles
- 💳 **200 normal transactions** with typical patterns  
- 🔴 **25 fraudulent transactions** with specific fraud types
- 📊 **~11% fraud rate** (industry realistic)

### **2. Review Generated Data**

```bash
# View data summary
cat fraud_test_data.json | jq '.metadata'

# Check fraud types generated
cat fraud_test_data.json | jq '.metadata.fraud_types'
```

---

## 🔍 **Fraud Types Generated**

The system generates **8 different fraud patterns**:

### **1. 💳 Stolen Card Fraud**
- **Pattern**: High amounts, new devices, impossible geo-velocity
- **Risk Indicators**: `["new_device", "geo_velocity_impossible", "unusual_spending_pattern"]`
- **Amount Range**: $100 - $2,000

### **2. 🔐 Account Takeover**
- **Pattern**: New device, suspicious fingerprint, failed identity verification
- **Risk Indicators**: `["new_device", "suspicious_device_fingerprint", "identity_verification_failed"]`
- **Amount Range**: $200 - $1,500

### **3. 👤 Synthetic Identity**
- **Pattern**: Fake identity with unusual patterns
- **Risk Indicators**: `["suspicious_device_fingerprint", "unusual_spending_pattern"]`
- **Amount Range**: $50 - $1,000

### **4. 💰 Money Laundering**
- **Pattern**: Large amounts, unusual merchants, high-risk countries
- **Risk Indicators**: `["unusual_merchant_category", "high_risk_country", "amount_outside_normal_range"]`
- **Amount Range**: $500 - $10,000

### **5. ⚡ Velocity Fraud**
- **Pattern**: Rapid successive transactions
- **Risk Indicators**: `["multiple_transactions_short_time", "burst_pattern_detected"]`
- **Amount Range**: $10 - $500

### **6. 🏪 Merchant Fraud**
- **Pattern**: Suspicious merchant behavior
- **Risk Indicators**: `["suspicious_device_fingerprint", "unusual_spending_pattern"]`
- **Amount Range**: $50 - $1,000

### **7. 💸 Refund Fraud**
- **Pattern**: Unusual refund patterns
- **Risk Indicators**: `["suspicious_device_fingerprint", "unusual_spending_pattern"]`
- **Amount Range**: $50 - $1,000

### **8. 🔄 Chargeback Fraud**
- **Pattern**: Fraudulent chargeback claims
- **Risk Indicators**: `["suspicious_device_fingerprint", "unusual_spending_pattern"]`
- **Amount Range**: $50 - $1,000

---

## 🌐 **Testing Fraud Detection APIs**

### **Method 1: Manual API Testing**

#### **A. Authenticate**
```bash
# Login to get auth token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "customer@test.com", "password": "TestPassword123!"}'
```

#### **B. Test Fraud Detection**
```bash
# Use the access_token from login response
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "detect_fraud_patterns",
      "arguments": {
        "hours_back": 24,
        "risk_threshold": 70.0
      }
    }
  }'
```

### **Method 2: Use Customer App**

1. **Open Customer App**: http://localhost:3001
2. **Login** with test account: `customer@test.com` / `TestPassword123!`
3. **Create transactions** with different patterns:
   - Small amounts ($10-50) - Normal
   - Large amounts ($500+) - Suspicious 
   - Rapid transactions - Velocity pattern
   - Foreign locations - Geographic anomaly

### **Method 3: Use Admin Dashboard**

1. **Open Admin Dashboard**: http://localhost:3000
2. **Navigate to**: Fraud Detection section
3. **View**: Real-time fraud analytics and alerts
4. **Monitor**: Live fraud detection results

---

## 📊 **Available Fraud Detection Tools**

### **1. Detect Fraud Patterns**
```json
{
  "name": "detect_fraud_patterns",
  "parameters": {
    "transaction_id": "optional_txn_id",
    "user_id": "optional_user_id", 
    "hours_back": 24,
    "risk_threshold": 70.0
  }
}
```

### **2. Generate Custom Fraud Report**
```json
{
  "name": "generate_custom_report",
  "parameters": {
    "report_type": "fraud_analysis",
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-06-07T23:59:59Z",
    "format": "json"
  }
}
```

### **3. Get Dashboard Metrics**
```json
{
  "name": "get_dashboard_metrics",
  "parameters": {
    "time_range": "24h",
    "refresh_cache": true
  }
}
```

---

## 🎯 **Testing Scenarios**

### **Scenario 1: High-Velocity Attack**
```bash
# Create 5 rapid transactions from same customer
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/payments/ \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -d '{"amount": 100, "currency": "USD", "payment_method": "card", "customer_id": "test_customer_1"}' &
done
```

### **Scenario 2: Geographic Anomaly**
Create transactions with metadata indicating different geographic locations:
```json
{
  "amount": 500,
  "currency": "USD", 
  "payment_method": "card",
  "customer_id": "test_customer_1",
  "metadata": {
    "location": {
      "country": "XX",
      "city": "Unknown",
      "is_high_risk": true
    }
  }
}
```

### **Scenario 3: Amount Deviation**
```json
{
  "amount": 5000,
  "currency": "USD",
  "payment_method": "card", 
  "customer_id": "test_customer_1",
  "metadata": {
    "risk_indicators": ["amount_outside_normal_range"]
  }
}
```

---

## 📈 **Monitoring & Analytics**

### **Real-Time Dashboards**

#### **Admin Dashboard** (http://localhost:3000)
- 🔍 **Fraud Detection Overview**
- 📊 **Risk Score Analytics**
- 🚨 **Alert Management**
- 📈 **Trend Analysis**

#### **Customer App** (http://localhost:3001)
- 💳 **Transaction Security Status**
- 🔐 **Account Security Alerts**
- 📱 **Device Management**

### **API Endpoints for Analytics**

```bash
# Get fraud analytics
curl "http://localhost:8000/api/v1/analytics/fraud" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get real-time metrics
curl "http://localhost:8000/api/v1/monitoring/metrics" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get compliance reports
curl "http://localhost:8000/api/v1/compliance/audit-logs" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 **Advanced Testing**

### **Load Testing Fraud Detection**
```bash
# Use locust for load testing
cd tests/performance
locust -f locustfile.py --host=http://localhost:8000
```

### **Custom Fraud Patterns**
Create your own fraud patterns by modifying the data generator:

```python
# Add to scripts/generate_fraud_data.py
def _generate_custom_fraud(self, customer, fraud_type):
    return Transaction(
        # Your custom fraud logic here
        risk_indicators=["custom_pattern", "your_indicator"],
        amount=custom_amount_logic(),
        # ... other fields
    )
```

---

## 🎯 **Expected Results**

### **Fraud Detection Accuracy**
- ✅ **Detection Rate**: 97.2% (as shown in logs)
- ✅ **False Positive Rate**: <3%
- ✅ **Response Time**: <150ms average
- ✅ **Real-time Processing**: Yes

### **Sample Fraud Detection Response**
```json
{
  "success": true,
  "analysis": {
    "overall_risk_score": 85.5,
    "suspicious_patterns": [
      {
        "type": "velocity",
        "risk_score": 89.0,
        "description": "Multiple rapid transactions detected"
      }
    ],
    "recommendations": [
      "Monitor user activity for next 24 hours",
      "Implement additional verification"
    ]
  },
  "message": "Fraud pattern analysis completed. Found 2 high-risk patterns."
}
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Authentication Errors**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Create new test user if needed
curl -X POST http://localhost:8000/api/v1/auth/register \
  -d '{"name": "Test User", "email": "test@example.com", "password": "TestPass123!"}'
```

#### **2. Rate Limiting (429 errors)**
- Wait 1 minute between requests
- Use different test accounts
- Check rate limiting settings in backend

#### **3. MCP Tools Not Found (404)**
```bash
# Check available MCP tools
curl http://localhost:8000/mcp/tools/list
```

#### **4. No Fraud Data**
```bash
# Regenerate test data
python scripts/generate_fraud_data.py --fraud-txns 10
```

---

## 📚 **Key Files**

| File | Purpose |
|------|---------|
| `scripts/generate_fraud_data.py` | Generate test fraud data |
| `scripts/test_fraud_detection.py` | Test fraud detection APIs |
| `fraud_test_data.json` | Generated fraud test dataset |
| `app/mcp/tools/analytics_tools.py` | Fraud detection MCP tools |
| `app/services/analytics_service.py` | Fraud detection business logic |

---

## 🏆 **Best Practices**

### **1. Data Generation**
- ✅ Use realistic fraud rates (5-15%)
- ✅ Mix different fraud types
- ✅ Include geographic diversity
- ✅ Vary transaction amounts

### **2. Testing**
- ✅ Test multiple scenarios
- ✅ Monitor response times
- ✅ Validate accuracy metrics
- ✅ Check false positive rates

### **3. Monitoring**
- ✅ Set up real-time alerts
- ✅ Monitor fraud trends
- ✅ Track model performance
- ✅ Review compliance metrics

---

## 🎉 **Success Metrics**

After testing, you should see:

✅ **Generated Data**: 100+ transactions with realistic fraud patterns  
✅ **API Responses**: Fraud detection working with risk scores  
✅ **Dashboard**: Real-time fraud analytics visible  
✅ **Alerts**: Fraud alerts triggering correctly  
✅ **Performance**: Sub-200ms response times  
✅ **Accuracy**: High detection rates with low false positives

---

## 🔗 **Next Steps**

1. **📊 Monitor dashboards** for real-time fraud detection
2. **🔧 Tune parameters** like risk thresholds  
3. **📈 Analyze patterns** to improve detection
4. **🚨 Set up alerts** for fraud events
5. **📋 Generate reports** for compliance

**Happy fraud hunting!** 🕵️‍♂️ 