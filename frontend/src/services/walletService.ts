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

export interface WalletFilters {
  page?: number;
  limit?: number;
  search?: string;
  status?: string;
  currency?: string;
}

export interface Wallet {
  id: string;
  customer_id: string;
  currency: string;
  balance: number;
  available_balance: number;
  pending_balance: number;
  status: 'active' | 'frozen' | 'suspended';
  created_at: string;
  updated_at: string;
}

export interface WalletResponse {
  data: Wallet[];
  total: number;
  page: number;
  limit: number;
}

export class WalletService {
  /**
   * Get wallets with filters
   */
  static async getWallets(filters: WalletFilters): Promise<WalletResponse> {
    try {
      const response: AxiosResponse<WalletResponse> = await api.get('/api/v1/wallets', {
        params: filters,
      });
      return response.data;
    } catch (error: any) {
      console.error('Get wallets error:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch wallets');
    }
  }

  /**
   * Get wallet by ID
   */
  static async getWallet(walletId: string): Promise<Wallet> {
    try {
      const response: AxiosResponse<Wallet> = await api.get(`/api/v1/wallets/${walletId}`);
      return response.data;
    } catch (error: any) {
      console.error('Get wallet error:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch wallet');
    }
  }

  /**
   * Create new wallet
   */
  static async createWallet(walletData: {
    customer_id: string;
    currency: string;
    initial_balance?: number;
  }): Promise<Wallet> {
    try {
      const response: AxiosResponse<Wallet> = await api.post('/api/v1/wallets', walletData);
      return response.data;
    } catch (error: any) {
      console.error('Create wallet error:', error);
      throw new Error(error.response?.data?.message || 'Failed to create wallet');
    }
  }

  /**
   * Update wallet
   */
  static async updateWallet(walletId: string, updates: Partial<Wallet>): Promise<Wallet> {
    try {
      const response: AxiosResponse<Wallet> = await api.put(`/api/v1/wallets/${walletId}`, updates);
      return response.data;
    } catch (error: any) {
      console.error('Update wallet error:', error);
      throw new Error(error.response?.data?.message || 'Failed to update wallet');
    }
  }

  /**
   * Transfer funds between wallets
   */
  static async transferFunds(transferData: {
    from_wallet_id: string;
    to_wallet_id: string;
    amount: number;
    currency: string;
    description?: string;
  }): Promise<any> {
    try {
      const response: AxiosResponse<any> = await api.post('/api/v1/wallets/transfer', transferData);
      return response.data;
    } catch (error: any) {
      console.error('Transfer funds error:', error);
      throw new Error(error.response?.data?.message || 'Failed to transfer funds');
    }
  }

  /**
   * Top up wallet
   */
  static async topUpWallet(topUpData: {
    wallet_id: string;
    amount: number;
    payment_method: string;
    description?: string;
  }): Promise<any> {
    try {
      const response: AxiosResponse<any> = await api.post('/api/v1/wallets/top-up', topUpData);
      return response.data;
    } catch (error: any) {
      console.error('Top up wallet error:', error);
      throw new Error(error.response?.data?.message || 'Failed to top up wallet');
    }
  }

  /**
   * Get wallet transaction history
   */
  static async getTransactionHistory(walletId: string, filters?: {
    page?: number;
    limit?: number;
    type?: string;
  }): Promise<any> {
    try {
      const response: AxiosResponse<any> = await api.get(`/api/v1/wallets/${walletId}/transactions`, {
        params: filters,
      });
      return response.data;
    } catch (error: any) {
      console.error('Get transaction history error:', error);
      throw new Error(error.response?.data?.message || 'Failed to fetch transaction history');
    }
  }
}

export const walletService = WalletService; 