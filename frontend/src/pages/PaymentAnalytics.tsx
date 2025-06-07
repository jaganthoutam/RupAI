import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  Tab,
  Tabs,
  FormControl,
  Select,
  MenuItem,
  SelectChangeEvent,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Alert,
  Switch,
  FormControlLabel,
  Container,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import {
  CreditCard,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Error,
  Pending,
  AccountBalance,
  Speed,
  Assessment,
  Download,
  Refresh,
  FilterList,
  Analytics,
  Payment,
  Timeline,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { mcpService } from '../services/mcpService';
import ApiService, { PaymentAnalyticsData } from '../services/apiService';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface PaymentMetrics {
  totalPayments: number;
  successfulPayments: number;
  failedPayments: number;
  pendingPayments: number;
  successRate: number;
  averageProcessingTime: number;
  totalVolume: number;
  averageAmount: number;
}

interface PaymentTrend {
  date: string;
  successful: number;
  failed: number;
  pending: number;
  volume: number;
  processingTime: number;
}

interface PaymentMethod {
  method: string;
  count: number;
  successRate: number;
  averageAmount: number;
  volume: number;
  color: string;
}

interface PaymentStatus {
  status: string;
  count: number;
  percentage: number;
  color: string;
}

interface ErrorAnalysis {
  errorCode: string;
  errorMessage: string;
  count: number;
  percentage: number;
  trend: 'up' | 'down' | 'stable';
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const PaymentAnalytics: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [timePeriod, setTimePeriod] = useState('7d');
  const [granularity, setGranularity] = useState('daily');
  const [startDate, setStartDate] = useState(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000));
  const [endDate, setEndDate] = useState(new Date());
  const [loading, setLoading] = useState(false);
  const [realTimeMode, setRealTimeMode] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<PaymentAnalyticsData | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as 'success' | 'error' | 'info' });

  const loadPaymentData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to get data from MCP service first (AI-powered analytics)
      let paymentData;
      try {
        paymentData = await mcpService.getPaymentMetrics({
          start_date: startDate,
          end_date: endDate,
          granularity,
        });
      } catch (mcpError) {
        console.warn('MCP service unavailable, falling back to direct API:', mcpError);
        // Fallback to direct API service
        paymentData = await ApiService.getPaymentAnalytics(startDate, endDate, granularity);
      }

      setData(paymentData);
      setSnackbar({
        open: true,
        message: 'Payment analytics updated successfully',
        severity: 'success'
      });
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to load payment analytics';
      setError(errorMessage);
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
      console.error('Payment analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPaymentData();
  }, [timePeriod, granularity, startDate, endDate]);

  useEffect(() => {
    let interval: NodeJS.Timeout | undefined;
    if (realTimeMode) {
      interval = setInterval(loadPaymentData, 30000); // Refresh every 30 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [realTimeMode, timePeriod]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleTimePeriodChange = (period: string) => {
    setTimePeriod(period);
    const now = new Date();
    switch (period) {
      case '1d':
        setStartDate(new Date(now.getTime() - 24 * 60 * 60 * 1000));
        break;
      case '7d':
        setStartDate(new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000));
        break;
      case '30d':
        setStartDate(new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000));
        break;
      case '90d':
        setStartDate(new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000));
        break;
      default:
        break;
    }
    setEndDate(now);
  };

  const handleExportData = async () => {
    try {
      setSnackbar({
        open: true,
        message: 'Preparing payment analytics report...',
        severity: 'info'
      });

      const reportData = await mcpService.generateAuditReport({
        report_type: 'payment_analytics',
        start_date: startDate,
        end_date: endDate,
        include_pii: false,
      });

      // Create and download CSV
      const csvContent = generateCSV(reportData);
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `payment_analytics_${startDate.toISOString().split('T')[0]}_${endDate.toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setSnackbar({
        open: true,
        message: 'Payment analytics report downloaded successfully',
        severity: 'success'
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Failed to export payment data',
        severity: 'error'
      });
    }
  };

  const generateCSV = (data: any) => {
    if (!data) return '';
    
    const headers = ['Date', 'Count', 'Amount', 'Success Rate'];
    const rows = [headers.join(',')];
    
    if (data.daily_trends) {
      data.daily_trends.forEach((item: any) => {
        rows.push([
          item.date,
          item.count || 0,
          item.amount || 0,
          item.success_rate || 0
        ].join(','));
      });
    }
    
    return rows.join('\n');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const MetricCard: React.FC<{
    title: string;
    value: string;
    change?: number;
    icon: React.ReactNode;
    color?: string;
    subtitle?: string;
  }> = ({ title, value, change, icon, color = 'primary', subtitle }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{ color: `${color}.main`, mr: 1 }}>
            {icon}
          </Box>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" sx={{ mb: 1 }}>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {subtitle}
          </Typography>
        )}
        {change !== undefined && (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {change >= 0 ? (
              <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
            ) : (
              <TrendingDown sx={{ color: 'error.main', mr: 0.5 }} />
            )}
            <Typography
              variant="body2"
              sx={{
                color: change >= 0 ? 'success.main' : 'error.main',
              }}
            >
              {change >= 0 ? '+' : ''}{change.toFixed(1)}%
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  if (loading && !data) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box mb={4}>
          <Typography variant="h4" component="h1" gutterBottom>
            Payment Analytics
          </Typography>
          
          {/* Controls */}
          <Box display="flex" gap={2} flexWrap="wrap" alignItems="center" mb={3}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <Select
                value={timePeriod}
                label="Time Period"
                onChange={(e) => handleTimePeriodChange(e.target.value)}
              >
                <MenuItem value="1d">Last 24 Hours</MenuItem>
                <MenuItem value="7d">Last 7 Days</MenuItem>
                <MenuItem value="30d">Last 30 Days</MenuItem>
                <MenuItem value="90d">Last 90 Days</MenuItem>
                <MenuItem value="custom">Custom Range</MenuItem>
              </Select>
            </FormControl>

            {timePeriod === 'custom' && (
              <>
                <DatePicker
                  label="Start Date"
                  value={startDate}
                  onChange={(date) => date && setStartDate(date)}
                  slotProps={{ textField: { size: 'small' } }}
                />
                <DatePicker
                  label="End Date"
                  value={endDate}
                  onChange={(date) => date && setEndDate(date)}
                  slotProps={{ textField: { size: 'small' } }}
                />
              </>
            )}

            <FormControl size="small" sx={{ minWidth: 120 }}>
              <Select
                value={granularity}
                label="Granularity"
                onChange={(e) => setGranularity(e.target.value)}
              >
                <MenuItem value="hourly">Hourly</MenuItem>
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Switch
                  checked={realTimeMode}
                  onChange={(e) => setRealTimeMode(e.target.checked)}
                />
              }
              label="Real-time"
            />

            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadPaymentData}
              disabled={loading}
            >
              Refresh
            </Button>

            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={handleExportData}
              disabled={loading}
            >
              Export
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
        </Box>

        {data && (
          <>
            {/* Key Metrics */}
            <Grid container spacing={3} mb={4}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <Typography color="text.secondary" gutterBottom>
                          Total Payments
                        </Typography>
                        <Typography variant="h4">
                          {(data.total_payments || 0).toLocaleString()}
                        </Typography>
                      </Box>
                      <Payment color="primary" sx={{ fontSize: 40 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <Typography color="text.secondary" gutterBottom>
                          Success Rate
                        </Typography>
                        <Typography variant="h4" color="success.main">
                          {formatPercentage(data.success_rate || 0)}
                        </Typography>
                      </Box>
                      <CheckCircle color="success" sx={{ fontSize: 40 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <Typography color="text.secondary" gutterBottom>
                          Avg Processing Time
                        </Typography>
                        <Typography variant="h4">
                          {`${(data.average_processing_time || 0).toFixed(1)}s`}
                        </Typography>
                      </Box>
                      <Timeline color="info" sx={{ fontSize: 40 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box>
                        <Typography color="text.secondary" gutterBottom>
                          Failed Payments
                        </Typography>
                        <Typography variant="h4" color="error.main">
                          {(data.failed_payments || 0).toLocaleString()}
                        </Typography>
                      </Box>
                      <Error color="error" sx={{ fontSize: 40 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Payment Trends Chart */}
            <Grid container spacing={3} mb={4}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Payment Trends
                      {loading && <CircularProgress size={20} sx={{ ml: 2 }} />}
                    </Typography>
                    <ResponsiveContainer width="100%" height={400}>
                      <AreaChart data={data.daily_trends || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <RechartsTooltip 
                          formatter={(value: any, name: string) => {
                            if (name === 'amount') return [formatCurrency(value), 'Amount'];
                            if (name === 'success_rate') return [formatPercentage(value), 'Success Rate'];
                            return [value, name];
                          }}
                        />
                        <Legend />
                        <Area
                          type="monotone"
                          dataKey="count"
                          stroke="#8884d8"
                          fill="#8884d8"
                          fillOpacity={0.6}
                        />
                        <Area
                          type="monotone"
                          dataKey="amount"
                          stroke="#82ca9d"
                          fill="#82ca9d"
                          fillOpacity={0.6}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Payment Methods Analysis */}
            {data.payment_methods && data.payment_methods.length > 0 && (
              <Grid container spacing={3} mb={4}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Payment Methods Distribution
                      </Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={data.payment_methods}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ method, count }) => `${method}: ${count}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="count"
                          >
                            {data.payment_methods.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <RechartsTooltip
                            formatter={(value: number) => [value.toLocaleString(), 'Transactions']}
                          />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Payment Methods Performance
                      </Typography>
                      <TableContainer>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Method</TableCell>
                              <TableCell align="right">Count</TableCell>
                              <TableCell align="right">Amount</TableCell>
                              <TableCell align="right">Success Rate</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {data.payment_methods.map((method, index) => (
                              <TableRow key={method.method}>
                                <TableCell>
                                  <Box display="flex" alignItems="center">
                                    <Box
                                      sx={{
                                        width: 12,
                                        height: 12,
                                        borderRadius: '50%',
                                        bgcolor: COLORS[index % COLORS.length],
                                        mr: 1,
                                      }}
                                    />
                                    {method.method}
                                  </Box>
                                </TableCell>
                                <TableCell align="right">
                                  {method.count.toLocaleString()}
                                </TableCell>
                                <TableCell align="right">
                                  {formatCurrency(method.amount)}
                                </TableCell>
                                <TableCell align="right">
                                  <Chip
                                    label={formatPercentage(method.success_rate)}
                                    color={method.success_rate >= 95 ? 'success' : method.success_rate >= 90 ? 'warning' : 'error'}
                                    size="small"
                                  />
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}

            {/* Geographic Analysis */}
            {data.geographic_data && data.geographic_data.length > 0 && (
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Geographic Distribution
                      </Typography>
                      <TableContainer>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Country</TableCell>
                              <TableCell align="right">Transactions</TableCell>
                              <TableCell align="right">Amount</TableCell>
                              <TableCell align="right">Share</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {data.geographic_data.map((country, index) => (
                              <TableRow key={country.country}>
                                <TableCell>{country.country}</TableCell>
                                <TableCell align="right">
                                  {country.count.toLocaleString()}
                                </TableCell>
                                <TableCell align="right">
                                  {formatCurrency(country.amount)}
                                </TableCell>
                                <TableCell align="right">
                                  {data.total_amount 
                                    ? formatPercentage((country.amount / data.total_amount) * 100)
                                    : '0%'
                                  }
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}
          </>
        )}

        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
        >
          <Alert
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            severity={snackbar.severity}
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Container>
    </LocalizationProvider>
  );
};

export default PaymentAnalytics;
