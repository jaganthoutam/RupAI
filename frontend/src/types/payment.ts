export interface Payment {
  id: string;
  customer_id: string;
  amount: number;
  currency: string;
  method: PaymentMethod;
  status: PaymentStatus;
  description?: string;
  metadata?: Record<string, any>;
  provider: PaymentProvider;
  provider_payment_id?: string;
  idempotency_key: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  failed_at?: string;
  error_message?: string;
}

export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded'
}

export enum PaymentMethod {
  CARD = 'card',
  BANK_TRANSFER = 'bank_transfer',
  WALLET = 'wallet',
  UPI = 'upi'
}

export enum PaymentProvider {
  STRIPE = 'stripe',
  RAZORPAY = 'razorpay'
}

export interface CreatePaymentRequest {
  amount: number;
  currency: string;
  method: PaymentMethod;
  customer_id: string;
  description?: string;
  metadata?: Record<string, any>;
}

export interface PaymentResponse {
  success: boolean;
  payment?: Payment;
  error?: string;
  payment_url?: string;
}

export interface RefundRequest {
  payment_id: string;
  amount?: number;
  reason: string;
}

export interface PaymentMetrics {
  total_transactions: number;
  total_revenue: number;
  success_rate: number;
  average_amount: number;
  transactions_by_method: Record<PaymentMethod, number>;
  transactions_by_status: Record<PaymentStatus, number>;
  revenue_by_currency: Record<string, number>;
}

export interface Customer {
  id: string;
  email?: string;
  phone?: string;
  name?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
} 