import axios, { AxiosResponse } from 'axios';
import { 
  Payment, 
  CreatePaymentRequest, 
  PaymentResponse, 
  RefundRequest, 
  PaymentMetrics 
} from '../types/payment';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export class PaymentService {
  /**
   * Create a new payment
   */
  static async createPayment(request: CreatePaymentRequest): Promise<PaymentResponse> {
    try {
      const response: AxiosResponse<PaymentResponse> = await api.post('/mcp/tools/call', {
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/call',
        params: {
          name: 'create_payment',
          arguments: {
            ...request,
            idempotency_key: `pay_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
          }
        }
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Create payment error:', error);
      throw new Error(error.response?.data?.message || 'Failed to create payment');
    }
  }

  /**
   * Verify payment status
   */
  static async verifyPayment(paymentId: string): Promise<Payment> {
    try {
      const response: AxiosResponse<{result: Payment}> = await api.post('/mcp/tools/call', {
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/call',
        params: {
          name: 'verify_payment',
          arguments: {
            payment_id: paymentId
          }
        }
      });
      
      return response.data.result;
    } catch (error: any) {
      console.error('Verify payment error:', error);
      throw new Error(error.response?.data?.message || 'Failed to verify payment');
    }
  }

  /**
   * Refund a payment
   */
  static async refundPayment(request: RefundRequest): Promise<PaymentResponse> {
    try {
      const response: AxiosResponse<PaymentResponse> = await api.post('/mcp/tools/call', {
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/call',
        params: {
          name: 'refund_payment',
          arguments: {
            ...request,
            idempotency_key: `refund_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
          }
        }
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Refund payment error:', error);
      throw new Error(error.response?.data?.message || 'Failed to refund payment');
    }
  }

  /**
   * Get payment by ID
   */
  static async getPayment(paymentId: string): Promise<Payment> {
    try {
      const response: AxiosResponse<Payment> = await api.get(`/payments/${paymentId}`);
      return response.data;
    } catch (error: any) {
      console.error('Get payment error:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch payment');
    }
  }

  /**
   * Get payments list with filters
   */
  static async getPayments(params?: {
    page?: number;
    limit?: number;
    status?: string;
    method?: string;
    customer_id?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<{payments: Payment[]; total: number; page: number; limit: number}> {
    try {
      const response = await api.get('/payments', { params });
      return response.data;
    } catch (error: any) {
      console.error('Get payments error:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch payments');
    }
  }

  /**
   * Get payment metrics
   */
  static async getPaymentMetrics(params?: {
    start_date?: string;
    end_date?: string;
    granularity?: 'hourly' | 'daily' | 'weekly' | 'monthly';
  }): Promise<PaymentMetrics> {
    try {
      const response: AxiosResponse<PaymentMetrics> = await api.get('/analytics/payments', { params });
      return response.data;
    } catch (error: any) {
      console.error('Get payment metrics error:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch payment metrics');
    }
  }

  /**
   * Get recent transactions
   */
  static async getRecentTransactions(limit: number = 10): Promise<Payment[]> {
    try {
      const response = await api.get('/payments/recent', { params: { limit } });
      return response.data;
    } catch (error: any) {
      console.error('Get recent transactions error:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch recent transactions');
    }
  }
}

export default PaymentService; 