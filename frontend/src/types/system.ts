export interface SystemStatus {
  status: 'healthy' | 'warning' | 'critical';
  uptime: number;
  lastCheck: string;
  systemHealth: number;
  components: {
    database: string;
    cache: string;
    queue: string;
    payments: string;
  };
}

export interface SystemMetrics {
  totalPayments: number;
  totalRevenue: number;
  totalUsers: number;
  successRate: number;
  averageTransactionTime: number;
  peakTPS: number;
}

export interface Alert {
  id: string;
  type: 'error' | 'warning' | 'info';
  message: string;
  timestamp: string;
  resolved: boolean;
} 