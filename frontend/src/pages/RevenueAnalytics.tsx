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
  Container,
  CircularProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Assessment,
  Timeline,
  Download,
  Refresh,
  FilterList,
  AccountBalance,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import { MCPService } from '../services/mcpService';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import ApiService, { RevenueAnalyticsData } from '../services/apiService';

interface RevenueMetrics {
  totalRevenue: number;
  monthlyRevenue: number;
  revenueGrowth: number;
  averageTransactionValue: number;
  transactionCount: number;
  conversionRate: number;
}

interface RevenueData {
  date: string;
  revenue: number;
  transactions: number;
  averageValue: number;
}

interface RevenueByMethod {
  method: string;
  revenue: number;
  percentage: number;
  color: string;
}

interface RevenueByRegion {
  region: string;
  revenue: number;
  growth: number;
  transactions: number;
}

const RevenueAnalytics: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [timePeriod, setTimePeriod] = useState('7d');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RevenueAnalyticsData | null>(null);
  const [breakdown, setBreakdown] = useState('daily');
  const [currency, setCurrency] = useState('USD');
  const [startDate, setStartDate] = useState(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000));
  const [endDate, setEndDate] = useState(new Date());
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as 'success' | 'error' | 'info' });

  const loadRevenueData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to get data from MCP service first (AI-powered analytics)
      let revenueData;
      try {
        revenueData = await MCPService.generateRevenueAnalytics({
          start_date: startDate,
          end_date: endDate,
          breakdown,
          currency,
        });
      } catch (mcpError) {
        console.warn('MCP service unavailable, falling back to direct API:', mcpError);
        // Fallback to direct API service
        revenueData = await ApiService.getRevenueAnalytics(startDate, endDate, breakdown, currency);
      }

      setData(revenueData);
      setSnackbar({
        open: true,
        message: 'Revenue analytics updated successfully',
        severity: 'success'
      });
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to load revenue analytics';
      setError(errorMessage);
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
      console.error('Revenue analytics error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRevenueData();
  }, [timePeriod, breakdown, currency, startDate, endDate]);

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
        message: 'Preparing revenue report for download...',
        severity: 'info'
      });

      const reportData = await MCPService.generateAuditReport({
        report_type: 'revenue_analytics',
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
      link.download = `revenue_analytics_${startDate.toISOString().split('T')[0]}_${endDate.toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setSnackbar({
        open: true,
        message: 'Revenue report downloaded successfully',
        severity: 'success'
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Failed to export revenue data',
        severity: 'error'
      });
    }
  };

  const generateCSV = (data: any) => {
    if (!data) return '';
    
    const headers = ['Date', 'Revenue', 'Transactions', 'Average Amount'];
    const rows = [headers.join(',')];
    
    if (data.revenue_trends) {
      data.revenue_trends.forEach((item: any) => {
        rows.push([
          item.date,
          item.revenue || 0,
          item.transactions || 0,
          item.revenue && item.transactions ? (item.revenue / item.transactions).toFixed(2) : '0'
        ].join(','));
      });
    }
    
    return rows.join('\n');
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

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
            Revenue Analytics
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
                value={breakdown}
                label="Breakdown"
                onChange={(e) => setBreakdown(e.target.value)}
              >
                <MenuItem value="hourly">Hourly</MenuItem>
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 100 }}>
              <Select
                value={currency}
                label="Currency"
                onChange={(e) => setCurrency(e.target.value)}
              >
                <MenuItem value="USD">USD</MenuItem>
                <MenuItem value="EUR">EUR</MenuItem>
                <MenuItem value="GBP">GBP</MenuItem>
                <MenuItem value="INR">INR</MenuItem>
                <MenuItem value="JPY">JPY</MenuItem>
              </Select>
            </FormControl>

            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadRevenueData}
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
                          Total Revenue
                        </Typography>
                        <Typography variant="h4">
                          {formatCurrency(data.total_revenue || 0)}
                        </Typography>
                      </Box>
                      <AttachMoney color="primary" sx={{ fontSize: 40 }} />
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
                          Monthly Revenue
                        </Typography>
                        <Typography variant="h4">
                          {formatCurrency(data.monthly_revenue || 0)}
                        </Typography>
                      </Box>
                      <AccountBalance color="primary" sx={{ fontSize: 40 }} />
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
                          Revenue Growth
                        </Typography>
                        <Typography variant="h4" color={data.revenue_growth >= 0 ? 'success.main' : 'error.main'}>
                          {formatPercentage(data.revenue_growth || 0)}
                        </Typography>
                      </Box>
                      {data.revenue_growth >= 0 ? (
                        <TrendingUp color="success" sx={{ fontSize: 40 }} />
                      ) : (
                        <TrendingDown color="error" sx={{ fontSize: 40 }} />
                      )}
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
                          Profit Margin
                        </Typography>
                        <Typography variant="h4">
                          {formatPercentage(data.profit_margin || 0)}
                        </Typography>
                      </Box>
                      <FilterList color="primary" sx={{ fontSize: 40 }} />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Revenue Trends Chart */}
            <Grid container spacing={3} mb={4}>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Revenue Trends
                      {loading && <CircularProgress size={20} sx={{ ml: 2 }} />}
                    </Typography>
                    <ResponsiveContainer width="100%" height={400}>
                      <AreaChart data={data.revenue_trends || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <RechartsTooltip 
                          formatter={(value: any, name: string) => {
                            if (name === 'revenue') return [formatCurrency(value), 'Revenue'];
                            return [value, name];
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="revenue"
                          stroke="#8884d8"
                          fill="#8884d8"
                          fillOpacity={0.6}
                        />
                        <Area
                          type="monotone"
                          dataKey="transactions"
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

            {/* Revenue Forecast */}
            {data.revenue_forecast && data.revenue_forecast.length > 0 && (
              <Grid container spacing={3} mb={4}>
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Revenue Forecast
                      </Typography>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={data.revenue_forecast}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <RechartsTooltip 
                            formatter={(value: any) => [formatCurrency(value), 'Predicted Revenue']}
                          />
                          <Line
                            type="monotone"
                            dataKey="predicted_revenue"
                            stroke="#ff7300"
                            strokeDasharray="5 5"
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            )}

            {/* Top Merchants */}
            {data.top_merchants && data.top_merchants.length > 0 && (
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Top Merchants by Revenue
                      </Typography>
                      <TableContainer>
                        <Table>
                          <TableHead>
                            <TableRow>
                              <TableCell>Merchant</TableCell>
                              <TableCell align="right">Revenue</TableCell>
                              <TableCell align="right">Growth</TableCell>
                              <TableCell align="center">Status</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {data.top_merchants.map((merchant: { merchant_id: string; name: string; revenue: number; growth: number }, index: number) => (
                              <TableRow key={merchant.merchant_id}>
                                <TableCell>
                                  <Box>
                                    <Typography variant="body2" fontWeight="bold">
                                      {merchant.name}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      ID: {merchant.merchant_id}
                                    </Typography>
                                  </Box>
                                </TableCell>
                                <TableCell align="right">
                                  <Typography variant="body2" fontWeight="bold">
                                    {formatCurrency(merchant.revenue)}
                                  </Typography>
                                </TableCell>
                                <TableCell align="right">
                                  <Typography
                                    variant="body2"
                                    color={merchant.growth >= 0 ? 'success.main' : 'error.main'}
                                  >
                                    {formatPercentage(merchant.growth)}
                                  </Typography>
                                </TableCell>
                                <TableCell align="center">
                                  <Chip
                                    label={merchant.growth >= 10 ? 'Growing' : merchant.growth >= 0 ? 'Stable' : 'Declining'}
                                    color={merchant.growth >= 10 ? 'success' : merchant.growth >= 0 ? 'default' : 'error'}
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

export default RevenueAnalytics;
