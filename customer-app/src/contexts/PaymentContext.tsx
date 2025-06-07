import React, { createContext, useContext, useState, ReactNode } from 'react'
import { PaymentService, WalletService, Payment, Wallet } from '../services/apiService'
import { toast } from 'react-toastify'

interface PaymentContextType {
  currentPayment: Payment | null
  wallets: Wallet[]
  isProcessing: boolean
  createOptimizedPayment: (paymentData: OptimizedPaymentData) => Promise<Payment>
  optimizePaymentRouting: (amount: number, currency: string) => Promise<any>
  refreshWallets: () => Promise<void>
  transferFunds: (transferData: TransferData) => Promise<void>
  topUpWallet: (walletId: string, amount: number) => Promise<void>
}

interface OptimizedPaymentData {
  amount: number
  currency: string
  payment_method: string
  description?: string
  optimize?: boolean
}

interface TransferData {
  from_wallet_id: string
  to_wallet_id: string
  amount: number
  currency: string
  description?: string
}

const PaymentContext = createContext<PaymentContextType | undefined>(undefined)

export const usePayment = () => {
  const context = useContext(PaymentContext)
  if (context === undefined) {
    throw new Error('usePayment must be used within a PaymentProvider')
  }
  return context
}

interface PaymentProviderProps {
  children: ReactNode
}

export const PaymentProvider: React.FC<PaymentProviderProps> = ({ children }) => {
  const [currentPayment, setCurrentPayment] = useState<Payment | null>(null)
  const [wallets, setWallets] = useState<Wallet[]>([])
  const [isProcessing, setIsProcessing] = useState(false)

  const createOptimizedPayment = async (paymentData: OptimizedPaymentData): Promise<Payment> => {
    try {
      setIsProcessing(true)
      const payment = await PaymentService.createPayment(paymentData)
      setCurrentPayment(payment)
      
      if (paymentData.optimize) {
        toast.success('AI-optimized payment created successfully!')
      } else {
        toast.success('Payment created successfully!')
      }
      
      return payment
    } catch (error: any) {
      console.error('Payment creation error:', error)
      toast.error(error.response?.data?.detail || 'Payment creation failed.')
      throw error
    } finally {
      setIsProcessing(false)
    }
  }

  const optimizePaymentRouting = async (amount: number, currency: string): Promise<any> => {
    try {
      const optimization = await PaymentService.optimizeRouting(amount, currency)
      toast.info('Payment routing optimized for best success rate!')
      return optimization
    } catch (error: any) {
      console.error('Payment optimization error:', error)
      toast.error('Payment optimization failed.')
      throw error
    }
  }

  const refreshWallets = async (): Promise<void> => {
    try {
      const walletsData = await WalletService.getWallets()
      setWallets(walletsData)
    } catch (error: any) {
      console.error('Wallets refresh error:', error)
      toast.error('Failed to refresh wallets.')
    }
  }

  const transferFunds = async (transferData: TransferData): Promise<void> => {
    try {
      setIsProcessing(true)
      await WalletService.transferFunds(transferData)
      toast.success('Funds transferred successfully!')
      await refreshWallets() // Refresh wallet balances
    } catch (error: any) {
      console.error('Transfer error:', error)
      toast.error(error.response?.data?.detail || 'Transfer failed.')
      throw error
    } finally {
      setIsProcessing(false)
    }
  }

  const topUpWallet = async (walletId: string, amount: number): Promise<void> => {
    try {
      setIsProcessing(true)
      await WalletService.topUpWallet(walletId, amount)
      toast.success('Wallet topped up successfully!')
      await refreshWallets() // Refresh wallet balances
    } catch (error: any) {
      console.error('Top-up error:', error)
      toast.error(error.response?.data?.detail || 'Top-up failed.')
      throw error
    } finally {
      setIsProcessing(false)
    }
  }

  const contextValue: PaymentContextType = {
    currentPayment,
    wallets,
    isProcessing,
    createOptimizedPayment,
    optimizePaymentRouting,
    refreshWallets,
    transferFunds,
    topUpWallet,
  }

  return (
    <PaymentContext.Provider value={contextValue}>
      {children}
    </PaymentContext.Provider>
  )
}

export default PaymentContext 