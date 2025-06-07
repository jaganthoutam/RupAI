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

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface PaymentData {
  id: string;
  amount: number;
  currency: string;
  status: string;
  method: string;
  customer_id: string;
  created_at: string;
  updated_at: string;
  description?: string;
  metadata?: Record<string, any>;
}

export interface WalletData {
  id: string;
  customer_id: string;
  currency: string;
  balance: number;
  available_balance: number;
  pending_balance: number;
  created_at: string;
  updated_at: string;
}

export interface UserAnalyticsData {
  total_users: number;
  active_users: number;
  new_users: number;
  retention_rate: number;
  user_segments: Array<{
    segment: string;
    count: number;
    percentage: number;
  }>;
  user_lifecycle: Array<{
    stage: string;
    count: number;
    conversion_rate: number;
  }>;
}

export interface PaymentAnalyticsData {
  total_payments: number;
  total_amount: number;
  success_rate: number;
  average_amount: number;
  successful_payments: number;
  failed_payments: number;
  pending_payments: number;
  average_processing_time: number;
  payment_methods: Array<{
    method: string;
    count: number;
    amount: number;
    success_rate: number;
  }>;
  daily_trends: Array<{
    date: string;
    count: number;
    amount: number;
    success_rate: number;
  }>;
  geographic_data: Array<{
    country: string;
    count: number;
    amount: number;
  }>;
}

export interface RevenueAnalyticsData {
  total_revenue: number;
  monthly_revenue: number;
  revenue_growth: number;
  profit_margin: number;
  top_merchants: Array<{
    merchant_id: string;
    name: string;
    revenue: number;
    growth: number;
  }>;
  revenue_trends: Array<{
    date: string;
    revenue: number;
    transactions: number;
  }>;
  revenue_forecast: Array<{
    date: string;
    predicted_revenue: number;
    confidence: number;
  }>;
}

export interface FraudAnalyticsData {
  total_alerts: number;
  high_risk_transactions: number;
  fraud_rate: number;
  blocked_amount: number;
  risk_patterns: Array<{
    pattern: string;
    count: number;
    risk_score: number;
  }>;
  alerts_by_type: Array<{
    type: string;
    count: number;
    severity: string;
  }>;
}

export interface SystemMetrics {
  uptime: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  response_time: number;
  throughput: number;
  error_rate: number;
  active_connections: number;
  service_status: Array<{
    service: string;
    status: 'healthy' | 'warning' | 'critical';
    response_time: number;
    last_check: string;
  }>;
}

export class ApiService {
  // Authentication
  static async login(email: string, password: string, rememberMe: boolean = false) {
    const response = await api.post('/auth/login', {
      email,
      password,
      remember_me: rememberMe,
    });
    return response.data;
  }

  static async logout(refreshToken: string) {
    const response = await api.post('/auth/logout', {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  static async getCurrentUser() {
    const response = await api.get('/auth/me');
    return response.data;
  }

  static async refreshToken(refreshToken: string) {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  // Analytics - Revenue
  static async getRevenueAnalytics(startDate: Date, endDate: Date, breakdown?: string, currency?: string): Promise<RevenueAnalyticsData> {
    const response = await api.get('/analytics/revenue', {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        breakdown,
        currency,
      },
    });
    return response.data;
  }

  // Analytics - Payments
  static async getPaymentAnalytics(startDate: Date, endDate: Date, granularity?: string): Promise<PaymentAnalyticsData> {
    const response = await api.get('/analytics/payments', {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
        granularity,
      },
    });
    return response.data;
  }

  // Analytics - Users
  static async getUserAnalytics(startDate: Date, endDate: Date): Promise<UserAnalyticsData> {
    const response = await api.get('/analytics/users', {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      },
    });
    return response.data;
  }

  // Analytics - Fraud Detection
  static async getFraudAnalytics(startDate: Date, endDate: Date): Promise<FraudAnalyticsData> {
    const response = await api.get('/analytics/fraud', {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      },
    });
    return response.data;
  }

  // System Monitoring
  static async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await api.get('/system/metrics');
    return response.data;
  }

  static async getSystemStatus() {
    const response = await api.get('/system/status');
    return response.data;
  }

  static async getActiveAlerts() {
    const response = await api.get('/system/alerts');
    return response.data;
  }

  // Payments
  static async getPayments(page: number = 1, limit: number = 50, filters?: any) {
    const response = await api.get('/payments', {
      params: {
        page,
        limit,
        ...filters,
      },
    });
    return response.data;
  }

  static async getPayment(paymentId: string): Promise<PaymentData> {
    const response = await api.get(`/payments/${paymentId}`);
    return response.data;
  }

  static async createPayment(paymentData: {
    amount: number;
    currency: string;
    method: string;
    customer_id: string;
    description?: string;
    metadata?: Record<string, any>;
  }) {
    const response = await api.post('/payments', paymentData);
    return response.data;
  }

  static async refundPayment(paymentId: string, data: {
    amount?: number;
    reason: string;
  }) {
    const response = await api.post(`/payments/${paymentId}/refund`, data);
    return response.data;
  }

  // Wallets
  static async getWallets(page: number = 1, limit: number = 50) {
    const response = await api.get('/wallets', {
      params: { page, limit },
    });
    return response.data;
  }

  static async getWallet(walletId: string): Promise<WalletData> {
    const response = await api.get(`/wallets/${walletId}`);
    return response.data;
  }

  static async getWalletBalance(customerId: string, currency?: string) {
    const response = await api.get(`/wallets/balance/${customerId}`, {
      params: { currency },
    });
    return response.data;
  }

  static async transferFunds(data: {
    from_wallet_id: string;
    to_wallet_id: string;
    amount: number;
    currency: string;
    description?: string;
  }) {
    const response = await api.post('/wallets/transfer', data);
    return response.data;
  }

  static async topUpWallet(walletId: string, data: {
    amount: number;
    payment_method: string;
    description?: string;
  }) {
    const response = await api.post(`/wallets/${walletId}/topup`, data);
    return response.data;
  }

  static async getWalletTransactionHistory(walletId: string, limit?: number) {
    const response = await api.get(`/wallets/${walletId}/transactions`, {
      params: { limit },
    });
    return response.data;
  }

  // Audit Logs
  static async getAuditLogs(filters: {
    start_date?: Date;
    end_date?: Date;
    entity_type?: string;
    action_type?: string;
    user_id?: string;
    page?: number;
    limit?: number;
  }) {
    const params: any = {
      page: filters.page || 1,
      limit: filters.limit || 50,
    };

    if (filters.start_date) params.start_date = filters.start_date.toISOString();
    if (filters.end_date) params.end_date = filters.end_date.toISOString();
    if (filters.entity_type) params.entity_type = filters.entity_type;
    if (filters.action_type) params.action_type = filters.action_type;
    if (filters.user_id) params.user_id = filters.user_id;

    const response = await api.get('/audit/logs', { params });
    return response.data;
  }

  static async exportAuditLogs(filters: {
    start_date: Date;
    end_date: Date;
    format?: string;
    entity_type?: string;
    action_type?: string;
  }) {
    const params: any = {
      start_date: filters.start_date.toISOString(),
      end_date: filters.end_date.toISOString(),
      format: filters.format || 'csv',
    };

    if (filters.entity_type) params.entity_type = filters.entity_type;
    if (filters.action_type) params.action_type = filters.action_type;

    const response = await api.get('/audit/export', {
      params,
      responseType: 'blob',
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `audit_logs_${new Date().toISOString().split('T')[0]}.${filters.format || 'csv'}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    return response.data;
  }

  // Compliance
  static async generateComplianceReport(data: {
    report_type: string;
    start_date: Date;
    end_date: Date;
    include_pii?: boolean;
  }) {
    const response = await api.post('/compliance/reports', {
      ...data,
      start_date: data.start_date.toISOString(),
      end_date: data.end_date.toISOString(),
    });
    return response.data;
  }

  static async validatePCICompliance() {
    const response = await api.post('/compliance/pci-validation');
    return response.data;
  }

  // User Management
  static async getUsers(page: number = 1, limit: number = 50) {
    const response = await api.get('/auth/users', {
      params: { skip: (page - 1) * limit, limit },
    });
    return response.data;
  }

  static async createUser(userData: {
    email: string;
    name: string;
    password: string;
    role?: string;
    permissions?: string[];
  }) {
    const response = await api.post('/auth/users', userData);
    return response.data;
  }

  static async getLoginAttempts(page: number = 1, limit: number = 50) {
    const response = await api.get('/auth/login-attempts', {
      params: { skip: (page - 1) * limit, limit },
    });
    return response.data;
  }

  static async getTokenStats() {
    const response = await api.get('/auth/token-stats');
    return response.data;
  }

  // Dashboard
  static async getDashboardMetrics(startDate: Date, endDate: Date) {
    const response = await api.get('/dashboard/metrics', {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      },
    });
    return response.data;
  }

  // Health Check
  static async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  }

  static async readinessCheck() {
    const response = await api.get('/ready');
    return response.data;
  }
}

export default ApiService; 