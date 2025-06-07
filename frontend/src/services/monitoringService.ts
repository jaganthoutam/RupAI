const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Placeholder monitoring service
export const monitoringService = {
  getSystemStatus: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return {
      data: {
        status: 'healthy' as const,
        uptime: 99.95,
        lastCheck: new Date().toISOString(),
        systemHealth: 98,
        components: {
          database: 'healthy',
          cache: 'healthy',
          queue: 'healthy',
          payments: 'healthy',
        }
      }
    };
  },
  
  getActiveAlerts: async () => {
    return {
      data: []
    };
  },

  getMetrics: async (params: any) => {
    return {
      data: {
        cpu: 45,
        memory: 67,
        disk: 23,
        network: 12
      }
    };
  }
}; 