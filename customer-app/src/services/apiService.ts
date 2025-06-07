import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// API client instance
class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = Cookies.get('auth_token')
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor to handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          Cookies.remove('auth_token')
          window.location.href = '/auth'
        }
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete(url, config)
    return response.data
  }
}

const apiClient = new ApiClient()

// Types
export interface User {
  id: string
  email: string
  name: string
  phone?: string
  avatar_url?: string
  verified: boolean
  created_at: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  user: User
  expires_in: number
}

export interface Payment {
  id: string
  amount: number
  currency: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  payment_method: string
  description?: string
  created_at: string
  updated_at: string
  metadata?: Record<string, any>
}

export interface PaymentRequest {
  amount: number
  currency: string
  payment_method: string
  description?: string
  customer_id?: string
  metadata?: Record<string, any>
  optimize?: boolean
}

export interface Wallet {
  id: string
  user_id: string
  currency: string
  balance: number
  available_balance: number
  status: 'active' | 'suspended' | 'closed'
  created_at: string
}

export interface Transaction {
  id: string
  wallet_id: string
  type: 'credit' | 'debit'
  amount: number
  currency: string
  status: 'pending' | 'completed' | 'failed'
  description: string
  reference_id?: string
  created_at: string
}

export interface Subscription {
  id: string
  user_id: string
  plan_id: string
  status: 'active' | 'cancelled' | 'paused' | 'expired'
  amount: number
  currency: string
  billing_cycle: 'monthly' | 'yearly'
  next_billing_date: string
  created_at: string
}

export interface ChatMessage {
  session_id: string
  message: string
  response: string
  response_type: string
  confidence: number
  suggested_actions: Array<{
    action: string
    label: string
  }>
  timestamp: string
  response_time: number
}

// API Services
export class AuthService {
  static async login(email: string, password: string): Promise<AuthResponse> {
    return apiClient.post('/api/v1/auth/login', { email, password })
  }

  static async register(userData: {
    email: string
    password: string
    name: string
    phone?: string
  }): Promise<AuthResponse> {
    return apiClient.post('/api/v1/auth/register', userData)
  }

  static async refreshToken(): Promise<AuthResponse> {
    return apiClient.post('/api/v1/auth/refresh')
  }

  static async logout(): Promise<void> {
    await apiClient.post('/api/v1/auth/logout')
    Cookies.remove('auth_token')
  }

  static async getProfile(): Promise<User> {
    return apiClient.get('/api/v1/auth/me')
  }

  static async updateProfile(userData: Partial<User>): Promise<User> {
    return apiClient.put('/api/v1/auth/me', userData)
  }
}

export class PaymentService {
  static async createPayment(paymentData: PaymentRequest): Promise<Payment> {
    if (paymentData.optimize) {
      // Use AI-optimized payment creation
      return apiClient.post('/mcp', {
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/call',
        params: {
          name: 'create_payment_optimized',
          arguments: {
            amount: paymentData.amount,
            customer_id: 'current_user',
            currency: paymentData.currency,
            payment_method: paymentData.payment_method,
            ai_optimization: true,
            fraud_check: true
          }
        }
      })
    }
    
    return apiClient.post('/api/v1/payments/', paymentData)
  }

  static async getPayments(): Promise<Payment[]> {
    return apiClient.get('/api/v1/payments/')
  }

  static async getPayment(id: string): Promise<Payment> {
    return apiClient.get(`/api/v1/payments/${id}`)
  }

  static async getPaymentMethods(): Promise<any[]> {
    return apiClient.get('/api/v1/payments/methods')
  }

  static async optimizeRouting(amount: number, currency: string): Promise<any> {
    return apiClient.post('/mcp', {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: 'optimize_payment_routing',
        arguments: {
          amount,
          currency,
          optimize_for: 'success_rate'
        }
      }
    })
  }
}

export class WalletService {
  static async getWallets(): Promise<Wallet[]> {
    return apiClient.get('/api/v1/wallets/')
  }

  static async getWallet(id: string): Promise<Wallet> {
    return apiClient.get(`/api/v1/wallets/${id}`)
  }

  static async getBalance(walletId: string): Promise<any> {
    return apiClient.post('/mcp', {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: 'get_wallet_balance',
        arguments: {
          wallet_id: walletId
        }
      }
    })
  }

  static async transferFunds(data: {
    from_wallet_id: string
    to_wallet_id: string
    amount: number
    currency: string
    description?: string
  }): Promise<Transaction> {
    return apiClient.post('/mcp', {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: 'transfer_funds',
        arguments: data
      }
    })
  }

  static async getTransactions(walletId: string): Promise<Transaction[]> {
    return apiClient.get(`/api/v1/wallets/${walletId}/transactions`)
  }

  static async topUpWallet(walletId: string, amount: number): Promise<Transaction> {
    return apiClient.post('/mcp', {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: 'top_up_wallet',
        arguments: {
          wallet_id: walletId,
          amount
        }
      }
    })
  }
}

export class SubscriptionService {
  static async getSubscriptions(): Promise<Subscription[]> {
    return apiClient.get('/api/v1/subscriptions/')
  }

  static async createSubscription(data: {
    plan_id: string
    amount: number
    currency: string
    billing_cycle: string
  }): Promise<Subscription> {
    return apiClient.post('/mcp', {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: 'create_subscription_optimized',
        arguments: {
          customer_id: 'current_user',
          plan_id: data.plan_id,
          amount: data.amount,
          currency: data.currency,
          billing_cycle: data.billing_cycle,
          ai_optimization: true
        }
      }
    })
  }

  static async cancelSubscription(id: string): Promise<void> {
    return apiClient.post('/mcp', {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: 'cancel_subscription',
        arguments: {
          subscription_id: id
        }
      }
    })
  }

  static async getAvailablePlans(): Promise<any[]> {
    return apiClient.get('/api/v1/subscriptions/plans')
  }
}

export class ChatService {
  static async sendMessage(message: string, sessionId?: string): Promise<ChatMessage> {
    return apiClient.post('/api/v1/advanced/chat/message', {
      message,
      session_id: sessionId || `session_${Date.now()}`,
      context: {}
    })
  }

  static async getChatSessions(): Promise<any[]> {
    return apiClient.get('/api/v1/advanced/chat/sessions')
  }
}

export class AnalyticsService {
  static async getFraudAnalytics(): Promise<any> {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - 30)
    
    return apiClient.get('/api/v1/analytics/fraud', {
      params: {
        start_date: startDate.toISOString(),
        end_date: endDate.toISOString()
      }
    })
  }

  static async getPaymentAnalytics(): Promise<any> {
    return apiClient.get('/api/v1/analytics/payments', {
      params: {
        days: 30
      }
    })
  }

  static async getDashboardMetrics(): Promise<any> {
    return apiClient.post('/mcp', {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: 'get_dashboard_metrics',
        arguments: {
          time_range: '24h',
          refresh_cache: true
        }
      }
    })
  }
}

// Combined API Service (default export)
const apiService = {
  // Auth methods
  login: AuthService.login,
  register: AuthService.register,
  refreshToken: AuthService.refreshToken,
  logout: AuthService.logout,
  getProfile: AuthService.getProfile,
  updateProfile: AuthService.updateProfile,

  // Payment methods
  createPayment: PaymentService.createPayment,
  getPayments: PaymentService.getPayments,
  getPayment: PaymentService.getPayment,
  getPaymentMethods: PaymentService.getPaymentMethods,
  optimizeRouting: PaymentService.optimizeRouting,

  // Wallet methods
  getWallets: WalletService.getWallets,
  getWallet: WalletService.getWallet,
  getBalance: WalletService.getBalance,
  transferFunds: WalletService.transferFunds,
  getTransactions: WalletService.getTransactions,
  topUpWallet: WalletService.topUpWallet,

  // Subscription methods
  getSubscriptions: SubscriptionService.getSubscriptions,
  createSubscription: SubscriptionService.createSubscription,
  cancelSubscription: SubscriptionService.cancelSubscription,
  getAvailablePlans: SubscriptionService.getAvailablePlans,

  // Chat methods
  sendMessage: ChatService.sendMessage,
  getChatSessions: ChatService.getChatSessions,

  // Analytics methods
  getFraudAnalytics: AnalyticsService.getFraudAnalytics,
  getPaymentAnalytics: AnalyticsService.getPaymentAnalytics,
  getDashboardMetrics: AnalyticsService.getDashboardMetrics
}

export default apiService 