import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface MCPToolCall {
  jsonrpc: '2.0';
  id: number;
  method: 'tools/call';
  params: {
    name: string;
    arguments: Record<string, any>;
  };
}

export interface MCPToolResponse {
  jsonrpc: '2.0';
  id: number;
  result?: {
    content: Array<{
      type: string;
      text: string;
    }>;
    isError: boolean;
    _meta?: Record<string, any>;
  };
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

export interface MCPToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
}

export class MCPService {
  /**
   * Call an MCP tool
   */
  static async callTool(toolName: string, args: Record<string, any>): Promise<any> {
    try {
      const payload: MCPToolCall = {
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: args,
        },
      };

      const response: AxiosResponse<MCPToolResponse> = await api.post('/mcp', payload);
      
      if (response.data.error) {
        throw new Error(response.data.error.message);
      }

      return response.data.result;
    } catch (error: any) {
      console.error(`MCP tool call error (${toolName}):`, error);
      throw new Error(error.response?.data?.message || `Failed to call MCP tool: ${toolName}`);
    }
  }

  /**
   * Get available MCP tools
   */
  static async getTools(): Promise<MCPToolDefinition[]> {
    try {
      const response = await api.post('/mcp', {
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/list',
        params: {},
      });

      return response.data.result?.tools || [];
    } catch (error: any) {
      console.error('Get MCP tools error:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch MCP tools');
    }
  }

  /**
   * Payment Tools
   */
  static async createPayment(data: {
    amount: number;
    currency: string;
    method: string;
    customer_id: string;
    description?: string;
    metadata?: Record<string, any>;
  }): Promise<any> {
    return this.callTool('create_payment', {
      ...data,
      idempotency_key: `pay_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    });
  }

  static async verifyPayment(paymentId: string): Promise<any> {
    return this.callTool('verify_payment', { payment_id: paymentId });
  }

  static async refundPayment(data: {
    payment_id: string;
    amount?: number;
    reason: string;
  }): Promise<any> {
    return this.callTool('refund_payment', {
      ...data,
      idempotency_key: `refund_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    });
  }

  static async getPaymentStatus(paymentId: string): Promise<any> {
    return this.callTool('get_payment_status', { payment_id: paymentId });
  }

  /**
   * Wallet Tools
   */
  static async getWalletBalance(customerId: string, currency?: string): Promise<any> {
    return this.callTool('get_wallet_balance', { customer_id: customerId, currency });
  }

  static async transferFunds(data: {
    from_wallet_id: string;
    to_wallet_id: string;
    amount: number;
    currency: string;
    description?: string;
  }): Promise<any> {
    return this.callTool('transfer_funds', {
      ...data,
      idempotency_key: `transfer_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    });
  }

  static async getWalletTransactionHistory(walletId: string, limit?: number): Promise<any> {
    return this.callTool('wallet_transaction_history', { wallet_id: walletId, limit });
  }

  static async topUpWallet(data: {
    wallet_id: string;
    amount: number;
    payment_method: string;
    description?: string;
  }): Promise<any> {
    return this.callTool('top_up_wallet', {
      ...data,
      idempotency_key: `topup_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    });
  }

  /**
   * Analytics Tools
   */
  static async getPaymentMetrics(data: {
    start_date: Date;
    end_date: Date;
    granularity?: string;
    currency?: string;
    payment_method?: string;
    provider?: string;
  }): Promise<any> {
    return this.callTool('get_payment_metrics', {
      ...data,
      start_date: data.start_date.toISOString(),
      end_date: data.end_date.toISOString(),
    });
  }

  static async analyzeUserBehavior(data: {
    user_id?: string;
    start_date: Date;
    end_date: Date;
    behavior_type?: string;
  }): Promise<any> {
    return this.callTool('analyze_user_behavior', {
      ...data,
      start_date: data.start_date.toISOString(),
      end_date: data.end_date.toISOString(),
    });
  }

  static async generateRevenueAnalytics(data: {
    start_date: Date;
    end_date: Date;
    breakdown?: string;
    currency?: string;
  }): Promise<any> {
    return this.callTool('generate_revenue_analytics', {
      ...data,
      start_date: data.start_date.toISOString(),
      end_date: data.end_date.toISOString(),
    });
  }

  static async detectFraudPatterns(data: {
    user_id?: string;
    transaction_id?: string;
    analysis_type?: string;
    threshold?: number;
  }): Promise<any> {
    return this.callTool('detect_fraud_patterns', data);
  }

  static async getDashboardMetrics(data: {
    start_date: Date;
    end_date: Date;
  }): Promise<any> {
    return this.callTool('get_dashboard_metrics', {
      start_date: data.start_date.toISOString(),
      end_date: data.end_date.toISOString(),
    });
  }

  /**
   * Monitoring Tools
   */
  static async performHealthCheck(): Promise<any> {
    return this.callTool('perform_health_check', {});
  }

  static async getSystemStatus(): Promise<any> {
    return this.callTool('get_system_status', {});
  }

  static async getActiveAlerts(): Promise<any> {
    return this.callTool('get_active_alerts', {});
  }

  static async createAlert(data: {
    alert_type: string;
    severity: string;
    message: string;
    metadata?: Record<string, any>;
  }): Promise<any> {
    return this.callTool('create_alert', data);
  }

  static async resolveAlert(alertId: string, resolution?: string): Promise<any> {
    return this.callTool('resolve_alert', { alert_id: alertId, resolution });
  }

  static async getPerformanceMetrics(data: {
    start_date: Date;
    end_date: Date;
    metric_type?: string;
  }): Promise<any> {
    return this.callTool('get_performance_metrics', {
      ...data,
      start_date: data.start_date.toISOString(),
      end_date: data.end_date.toISOString(),
    });
  }

  /**
   * Compliance Tools
   */
  static async generateAuditReport(data: {
    report_type: string;
    start_date: Date;
    end_date: Date;
    user_id?: string;
    include_pii?: boolean;
  }): Promise<any> {
    return this.callTool('generate_audit_report', {
      ...data,
      start_date: data.start_date.toISOString(),
      end_date: data.end_date.toISOString(),
    });
  }

  static async exportComplianceData(data: {
    data_type: string;
    start_date: Date;
    end_date: Date;
    format?: string;
    encryption?: boolean;
  }): Promise<any> {
    return this.callTool('export_compliance_data', {
      ...data,
      start_date: data.start_date.toISOString(),
      end_date: data.end_date.toISOString(),
    });
  }

  static async validatePCICompliance(data?: {
    validation_scope?: string;
    include_recommendations?: boolean;
  }): Promise<any> {
    return this.callTool('validate_pci_compliance', data || {});
  }

  static async getAuditTrail(data: {
    entity_type: string;
    entity_id?: string;
    action_type?: string;
    start_date?: Date;
    end_date?: Date;
    user_id?: string;
    limit?: number;
  }): Promise<any> {
    return this.callTool('get_audit_trail', {
      ...data,
      start_date: data.start_date?.toISOString(),
      end_date: data.end_date?.toISOString(),
    });
  }
}

export const mcpService = MCPService; 