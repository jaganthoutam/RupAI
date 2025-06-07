import React from 'react';
import { Helmet } from 'react-helmet-async';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Paper,
  useTheme,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Payment,
  People,
  Security,
  Warning,
  CheckCircle,
  Error,
  Refresh,
  Timeline,
  AccountBalance,
  Shield,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import numeral from 'numeral';
import { format, subHours } from 'date-fns';

// Components
import MetricCard from '../components/dashboard/MetricCard';
import PaymentVolumeChart from '../components/charts/PaymentVolumeChart';
import RevenueChart from '../components/charts/RevenueChart';
import SystemHealthIndicator from '../components/monitoring/SystemHealthIndicator';
import AlertsList from '../components/alerts/AlertsList';
import RecentTransactions from '../components/transactions/RecentTransactions';
import PerformanceMetrics from '../components/monitoring/PerformanceMetrics';

// Services
import { analyticsService } from '../services/analyticsService';
import { monitoringService } from '../services/monitoringService';

// Types
interface DashboardMetrics {
  totalTransactions: number;
  totalRevenue: number;
  successRate: number;
  activeUsers: number;
  avgResponseTime: number;
  errorRate: number;
  systemHealth: number;
  alertsCount: number;
}

interface SystemStatus {
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

const Dashboard: React.FC = () => {
  const theme = useTheme();

  // Fetch dashboard metrics
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
    refetch: refetchMetrics,
  } = useQuery<DashboardMetrics>({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await analyticsService.getDashboardMetrics({
        startDate: subHours(new Date(), 24),
        endDate: new Date(),
      });
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch system status
  const {
    data: systemStatus,
    isLoading: statusLoading,
    error: statusError,
    refetch: refetchStatus,
  } = useQuery<SystemStatus>({
    queryKey: ['system-status'],
    queryFn: async () => {
      const response = await monitoringService.getSystemStatus();
      return response.data;
    },
    refetchInterval: 15000, // Refresh every 15 seconds
  });

  // Fetch payment volume data for chart
  const { data: paymentVolumeData } = useQuery({
    queryKey: ['payment-volume-chart'],
    queryFn: async () => {
      const response = await analyticsService.getPaymentMetrics({
        startDate: subHours(new Date(), 24),
        endDate: new Date(),
        granularity: 'hourly',
      });
      return response.data;
    },
    refetchInterval: 60000, // Refresh every minute
  });

  // Fetch revenue data for chart
  const { data: revenueData } = useQuery({
    queryKey: ['revenue-chart'],
    queryFn: async () => {
      const response = await analyticsService.getRevenueAnalytics({
        startDate: subHours(new Date(), 24),
        endDate: new Date(),
        breakdown: 'hourly',
      });
      return response.data;
    },
    refetchInterval: 60000,
  });

  // Fetch active alerts
  const { data: alerts } = useQuery({
    queryKey: ['active-alerts'],
    queryFn: async () => {
      const response = await monitoringService.getActiveAlerts();
      return response.data;
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return theme.palette.success.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'critical':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle sx={{ color: theme.palette.success.main }} />;
      case 'warning':
        return <Warning sx={{ color: theme.palette.warning.main }} />;
      case 'critical':
        return <Error sx={{ color: theme.palette.error.main }} />;
      default:
        return <Warning sx={{ color: theme.palette.grey[500] }} />;
    }
  };

  const formatCurrency = (amount: number) => numeral(amount).format('$0,0.00');
  const formatNumber = (num: number) => numeral(num).format('0,0');
  const formatPercentage = (num: number) => numeral(num / 100).format('0.0%');

  return (
    <>
      <Helmet>
        <title>Dashboard - MCP Payments Analytics</title>
        <meta name="description" content="Real-time payment system analytics and monitoring dashboard" />
      </Helmet>

      <Box sx={{ flexGrow: 1, p: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" component="h1">
            Payment System Dashboard
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Refresh metrics">
              <IconButton onClick={() => refetchMetrics()} disabled={metricsLoading}>
                <Refresh />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh system status">
              <IconButton onClick={() => refetchStatus()} disabled={statusLoading}>
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* System Status Alert */}
        {systemStatus && systemStatus.status !== 'healthy' && (
          <Alert
            severity={systemStatus.status === 'critical' ? 'error' : 'warning'}
            sx={{ mb: 3 }}
            icon={getStatusIcon(systemStatus.status)}
          >
            System status: {systemStatus.status.toUpperCase()} - 
            {systemStatus.status === 'critical' 
              ? ' Immediate attention required' 
              : ' Monitoring required'}
          </Alert>
        )}

        {/* Key Metrics */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Total Transactions"
              value={formatNumber(metrics?.totalTransactions || 0)}
              icon={<Payment />}
              trend={{
                direction: 'up',
                value: '5.2%',
                period: 'vs last month'
              }}
              loading={metricsLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Total Revenue"
              value={formatCurrency(metrics?.totalRevenue || 0)}
              icon={<AccountBalance />}
              trend={{
                direction: 'up',
                value: '8.1%',
                period: 'vs last month'
              }}
              loading={metricsLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Success Rate"
              value={formatPercentage(metrics?.successRate || 0)}
              icon={<CheckCircle />}
              trend={{
                direction: 'up',
                value: '0.3%',
                period: 'vs last month'
              }}
              loading={metricsLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Active Users"
              value={formatNumber(metrics?.activeUsers || 0)}
              icon={<People />}
              trend={{
                direction: 'up',
                value: '12.5%',
                period: 'vs last month'
              }}
              loading={metricsLoading}
            />
          </Grid>
        </Grid>

        {/* System Health & Performance */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Health
                </Typography>
                {systemStatus ? (
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      {getStatusIcon(systemStatus.status)}
                      <Typography variant="h4" sx={{ ml: 2, color: getStatusColor(systemStatus.status) }}>
                        {systemStatus.systemHealth || 0}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={systemStatus.systemHealth || 0}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        mb: 2,
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getStatusColor(systemStatus.status),
                        },
                      }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Uptime: {formatPercentage(systemStatus.uptime || 0)} | 
                      Last check: {format(new Date(systemStatus.lastCheck || new Date()), 'HH:mm:ss')}
                    </Typography>
                  </Box>
                ) : (
                  <SystemHealthIndicator 
                    status="healthy"
                    health={98}
                    components={{
                      database: 'healthy',
                      cache: 'healthy',
                      queue: 'healthy',
                      payments: 'healthy'
                    }}
                    loading={statusLoading} 
                  />
                )}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Metrics
                </Typography>
                <PerformanceMetrics
                  metrics={{
                    cpu: 45,
                    memory: 67,
                    disk: 23,
                    network: 12
                  }}
                  loading={metricsLoading}
                />
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Charts */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Payment Volume (Last 24 Hours)
                </Typography>
                <PaymentVolumeChart data={paymentVolumeData} loading={!paymentVolumeData} />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Revenue Trend
                </Typography>
                <RevenueChart data={revenueData} loading={!revenueData} />
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Active Alerts & Recent Transactions */}
        <Grid container spacing={3}>
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Active Alerts
                  </Typography>
                  <Chip 
                    label={alerts?.length || 0} 
                    color={alerts?.length > 0 ? 'error' : 'success'}
                    size="small"
                  />
                </Box>
                <AlertsList alerts={alerts || []} />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} lg={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Transactions
                </Typography>
                <RecentTransactions transactions={[]} />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </>
  );
};

export default Dashboard; 