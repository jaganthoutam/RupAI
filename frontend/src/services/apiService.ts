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
    const response = await api.post('/api/v1/auth/login', {
      email,
      password,
      remember_me: rememberMe,
    });
    return response.data;
  }

  static async logout(refreshToken: string) {
    const response = await api.post('/api/v1/auth/logout', {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  static async getCurrentUser() {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
  }

  static async refreshToken(refreshToken: string) {
    const response = await api.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  }

  // Analytics - Revenue
  static async getRevenueAnalytics(startDate: Date, endDate: Date, breakdown?: string, currency?: string): Promise<RevenueAnalyticsData> {
    const response = await api.get('/api/v1/analytics/revenue', {
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
    const response = await api.get('/api/v1/analytics/payments', {
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
    const response = await api.get('/api/v1/analytics/users', {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      },
    });
    return response.data;
  }

  // Analytics - Fraud Detection
  static async getFraudAnalytics(startDate: Date, endDate: Date): Promise<FraudAnalyticsData> {
    const response = await api.get('/api/v1/analytics/fraud', {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString(),
      },
    });
    return response.data;
  }

  // System Monitoring
  static async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await api.get('/api/v1/monitoring/system-metrics');
    return response.data;
  }

  static async getSystemStatus() {
    const response = await api.get('/api/v1/monitoring/system-status');
    return response.data;
  }

  static async getActiveAlerts() {
    const response = await api.get('/api/v1/monitoring/alerts');
    return response.data;
  }

  // Payments
  static async getPayments(page: number = 1, limit: number = 50, filters?: any) {
    const response = await api.get('/api/v1/payments', {
      params: {
        page,
        limit,
        ...filters,
      },
    });
    return response.data;
  }

  static async getPayment(paymentId: string): Promise<PaymentData> {
    const response = await api.get(`/api/v1/payments/${paymentId}`);
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
    const response = await api.post('/api/v1/payments', paymentData);
    return response.data;
  }

  static async refundPayment(paymentId: string, data: {
    amount?: number;
    reason: string;
  }) {
    const response = await api.post(`/api/v1/payments/${paymentId}/refund`, data);
    return response.data;
  }

  // Wallets
  static async getWallets(page: number = 1, limit: number = 50) {
    const response = await api.get('/api/v1/wallets', {
      params: { page, limit },
    });
    return response.data;
  }

  static async getWallet(walletId: string): Promise<WalletData> {
    const response = await api.get(`/api/v1/wallets/${walletId}`);
    return response.data;
  }

  static async getWalletBalance(customerId: string, currency?: string) {
    const response = await api.get(`/api/v1/wallets/balance/${customerId}`, {
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
    const response = await api.post('/api/v1/wallets/transfer', data);
    return response.data;
  }

  static async topUpWallet(walletId: string, data: {
    amount: number;
    payment_method: string;
    description?: string;
  }) {
    const response = await api.post(`/api/v1/wallets/${walletId}/topup`, data);
    return response.data;
  }

  static async getWalletTransactionHistory(walletId: string, limit?: number) {
    const response = await api.get(`/api/v1/wallets/${walletId}/transactions`, {
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

    const response = await api.get('/api/v1/compliance/audit-logs', { params });
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

    const response = await api.get('/api/v1/compliance/audit-logs/export', {
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
    const response = await api.post('/api/v1/compliance/reports', {
      ...data,
      start_date: data.start_date.toISOString(),
      end_date: data.end_date.toISOString(),
    });
    return response.data;
  }

  static async validatePCICompliance() {
    const response = await api.post('/api/v1/compliance/pci-validation');
    return response.data;
  }

  // User Management
  static async getUsers(page: number = 1, limit: number = 50, filters?: {
    search?: string;
    role?: string;
    active?: boolean;
  }) {
    const params: any = { page, limit };
    
    if (filters?.search) params.search = filters.search;
    if (filters?.role) params.role = filters.role;
    if (filters?.active !== undefined) params.active = filters.active;
    
    const response = await api.get('/api/v1/users', { params });
    return response.data;
  }

  static async createUser(userData: {
    email: string;
    name: string;
    password: string;
    role?: string;
    permissions?: string[];
  }) {
    const response = await api.post('/api/v1/users', userData);
    return response.data;
  }

  static async getUser(userId: string) {
    const response = await api.get(`/api/v1/users/${userId}`);
    return response.data;
  }

  static async updateUser(userId: string, userData: {
    name?: string;
    role?: string;
    permissions?: string[];
    is_active?: boolean;
  }) {
    const response = await api.put(`/api/v1/users/${userId}`, userData);
    return response.data;
  }

  static async deleteUser(userId: string) {
    const response = await api.delete(`/api/v1/users/${userId}`);
    return response.data;
  }

  static async activateUser(userId: string) {
    const response = await api.post(`/api/v1/users/${userId}/activate`);
    return response.data;
  }

  static async deactivateUser(userId: string) {
    const response = await api.post(`/api/v1/users/${userId}/deactivate`);
    return response.data;
  }

  static async getUserPermissions(userId: string) {
    const response = await api.get(`/api/v1/users/${userId}/permissions`);
    return response.data;
  }

  static async updateUserPermissions(userId: string, permissions: string[]) {
    const response = await api.put(`/api/v1/users/${userId}/permissions`, permissions);
    return response.data;
  }

  static async getUserStats() {
    const response = await api.get('/api/v1/users/stats/overview');
    return response.data;
  }

  static async getLoginAttempts(page: number = 1, limit: number = 50) {
    const response = await api.get('/api/v1/auth/login-attempts', {
      params: { skip: (page - 1) * limit, limit },
    });
    return response.data;
  }

  static async getTokenStats() {
    const response = await api.get('/api/v1/auth/token-stats');
    return response.data;
  }

  // Dashboard
  static async getDashboardMetrics(startDate: Date, endDate: Date) {
    const response = await api.get('/api/v1/analytics/dashboard-metrics', {
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

  // Subscription Management
  static async getSubscriptionPlans(activeOnly?: boolean) {
    const params: any = {};
    if (activeOnly !== undefined) params.active_only = activeOnly;
    
    const response = await api.get('/api/v1/subscriptions/plans', { params });
    return response.data;
  }

  static async createSubscriptionPlan(planData: {
    name: string;
    description?: string;
    price: number;
    currency?: string;
    billing_interval: string;
    trial_days?: number;
    features?: string[];
    is_active?: boolean;
    max_users?: number;
    max_transactions?: number;
  }) {
    const response = await api.post('/api/v1/subscriptions/plans', planData);
    return response.data;
  }

  static async getSubscriptionPlan(planId: string) {
    const response = await api.get(`/api/v1/subscriptions/plans/${planId}`);
    return response.data;
  }

  static async getSubscriptions(page: number = 1, limit: number = 50, filters?: {
    customer_id?: string;
    status?: string;
    search?: string;
  }) {
    const params: any = { page, limit };
    
    if (filters?.customer_id) params.customer_id = filters.customer_id;
    if (filters?.status) params.status = filters.status;
    if (filters?.search) params.search = filters.search;
    
    const response = await api.get('/api/v1/subscriptions', { params });
    return response.data;
  }

  static async createSubscription(subscriptionData: {
    customer_id: string;
    plan_id: string;
    payment_method_id?: string;
    trial_end?: string;
    metadata?: Record<string, any>;
  }) {
    const response = await api.post('/api/v1/subscriptions', subscriptionData);
    return response.data;
  }

  static async getSubscription(subscriptionId: string) {
    const response = await api.get(`/api/v1/subscriptions/${subscriptionId}`);
    return response.data;
  }

  static async cancelSubscription(subscriptionId: string, atPeriodEnd: boolean = true) {
    const response = await api.put(`/api/v1/subscriptions/${subscriptionId}/cancel`, null, {
      params: { at_period_end: atPeriodEnd }
    });
    return response.data;
  }

  static async reactivateSubscription(subscriptionId: string) {
    const response = await api.put(`/api/v1/subscriptions/${subscriptionId}/reactivate`);
    return response.data;
  }

  static async getSubscriptionInvoices(subscriptionId: string) {
    const response = await api.get(`/api/v1/subscriptions/${subscriptionId}/invoices`);
    return response.data;
  }

  static async getSubscriptionAnalytics(startDate?: string, endDate?: string) {
    const params: any = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    
    const response = await api.get('/api/v1/subscriptions/analytics', { params });
    return response.data;
  }

  // Settings & Configuration
  static async getSystemSettings(category?: string) {
    const params: any = {};
    if (category) params.category = category;
    
    const response = await api.get('/api/v1/settings/system', { params });
    return response.data;
  }

  static async updateSystemSetting(settingKey: string, value: any, description?: string) {
    const response = await api.put(`/api/v1/settings/system/${settingKey}`, {
      value,
      description
    });
    return response.data;
  }

  static async getUserPreferences() {
    const response = await api.get('/api/v1/settings/preferences');
    return response.data;
  }

  static async updateUserPreference(preferenceKey: string, value: any) {
    const response = await api.put(`/api/v1/settings/preferences/${preferenceKey}`, {
      value
    });
    return response.data;
  }

  static async getApiKeys(service?: string) {
    const params: any = {};
    if (service) params.service = service;
    
    const response = await api.get('/api/v1/settings/api-keys', { params });
    return response.data;
  }

  static async createApiKey(keyData: {
    name: string;
    service: string;
    description?: string;
    permissions?: string[];
    expires_at?: string;
  }) {
    const response = await api.post('/api/v1/settings/api-keys', keyData);
    return response.data;
  }

  static async deleteApiKey(keyId: string) {
    const response = await api.delete(`/api/v1/settings/api-keys/${keyId}`);
    return response.data;
  }

  static async getNotificationSettings() {
    const response = await api.get('/api/v1/settings/notifications');
    return response.data;
  }

  static async updateNotificationSetting(notificationType: string, settingData: {
    enabled: boolean;
    channels?: string[];
    frequency?: string;
    conditions?: Record<string, any>;
  }) {
    const response = await api.put(`/api/v1/settings/notifications/${notificationType}`, settingData);
    return response.data;
  }

  static async testNotification(notificationType: string, channels: string[]) {
    const response = await api.post(`/api/v1/settings/notifications/test/${notificationType}`, null, {
      params: { channels }
    });
    return response.data;
  }

  static async exportConfiguration(includeSensitive: boolean = false) {
    const response = await api.get('/api/v1/settings/export', {
      params: { include_sensitive: includeSensitive }
    });
    return response.data;
  }

  static async importConfiguration(configData: Record<string, any>, dryRun: boolean = false) {
    const response = await api.post('/api/v1/settings/import', configData, {
      params: { dry_run: dryRun }
    });
    return response.data;
  }

  // Advanced Features
  static async getMcpTools() {
    const response = await api.get('/api/v1/advanced/mcp/tools');
    return response.data;
  }

  static async executeMcpTool(toolName: string, arguments_: Record<string, any> = {}) {
    const response = await api.post('/api/v1/advanced/mcp/execute', {
      tool_name: toolName,
      arguments: arguments_
    });
    return response.data;
  }

  static async generateAiInsight(insightType: string, dataSource: string, parameters?: Record<string, any>, timeRange?: Record<string, string>) {
    const response = await api.post('/api/v1/advanced/ai-insights/generate', {
      insight_type: insightType,
      data_source: dataSource,
      parameters: parameters || {},
      time_range: timeRange
    });
    return response.data;
  }

  static async getAiInsights(insightType?: string) {
    const params: any = {};
    if (insightType) params.insight_type = insightType;
    
    const response = await api.get('/api/v1/advanced/ai-insights', { params });
    return response.data;
  }

  static async createCustomReport(reportData: {
    name: string;
    description?: string;
    data_sources: string[];
    filters?: Record<string, any>;
    grouping?: string[];
    metrics: string[];
    chart_type?: string;
    schedule?: Record<string, any>;
  }) {
    const response = await api.post('/api/v1/advanced/reports', reportData);
    return response.data;
  }

  static async getCustomReports() {
    const response = await api.get('/api/v1/advanced/reports');
    return response.data;
  }

  static async generateReport(reportId: string) {
    const response = await api.post(`/api/v1/advanced/reports/${reportId}/generate`);
    return response.data;
  }

  static async sendChatMessage(message: string, sessionId?: string, context?: Record<string, any>) {
    const response = await api.post('/api/v1/advanced/chat/message', {
      message,
      session_id: sessionId,
      context: context || {}
    });
    return response.data;
  }

  static async getChatSessions() {
    const response = await api.get('/api/v1/advanced/chat/sessions');
    return response.data;
  }

  static async searchDocumentation(query: string, category?: string, tags?: string[]) {
    const response = await api.post('/api/v1/advanced/documentation/search', {
      query,
      category,
      tags: tags || []
    });
    return response.data;
  }

  static async getDocumentationCategories() {
    const response = await api.get('/api/v1/advanced/documentation/categories');
    return response.data;
  }
}

export default ApiService; 