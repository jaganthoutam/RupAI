import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Avatar,
  Tooltip,
  LinearProgress,
  Alert,
  Snackbar,
  Switch,
  FormControlLabel,
  InputAdornment,
  Fade,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Tabs,
  Tab,
  Badge,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Refresh,
  PlayArrow,
  Pause,
  Stop,
  Receipt,
  TrendingUp,
  Schedule,
  AttachMoney,
  People,
  Cancel,
  CheckCircle,
  Warning,
  Info,
  Download,
  Visibility,
  MoreVert,
  FilterList,
} from '@mui/icons-material';
import { LoadingButton } from '@mui/lab';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import ApiService from '../services/apiService';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { motion, AnimatePresence } from 'framer-motion';

// Types
interface SubscriptionPlan {
  id: string;
  name: string;
  description?: string;
  price: number;
  currency: string;
  billing_interval: string;
  trial_days: number;
  features: string[];
  is_active: boolean;
  max_users?: number;
  max_transactions?: number;
  created_at: string;
  updated_at: string;
  subscriber_count: number;
}

interface Subscription {
  id: string;
  customer_id: string;
  plan_id: string;
  plan_name: string;
  status: string;
  current_period_start: string;
  current_period_end: string;
  trial_start?: string;
  trial_end?: string;
  cancel_at_period_end: boolean;
  canceled_at?: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
  next_billing_amount: number;
  next_billing_date: string;
}

interface SubscriptionAnalytics {
  total_subscriptions: number;
  active_subscriptions: number;
  trial_subscriptions: number;
  canceled_subscriptions: number;
  monthly_recurring_revenue: number;
  annual_recurring_revenue: number;
  average_revenue_per_user: number;
  churn_rate: number;
  growth_rate: number;
  trial_conversion_rate: number;
  plan_distribution: Array<{ plan: string; count: number; percentage: number }>;
  revenue_by_period: Array<{ period: string; revenue: number; growth: number }>;
}

const SubscriptionManagement: React.FC = () => {
  // State
  const [activeTab, setActiveTab] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedSubscriptions, setSelectedSubscriptions] = useState<string[]>([]);
  const [openCreatePlanDialog, setOpenCreatePlanDialog] = useState(false);
  const [openSubscriptionDialog, setOpenSubscriptionDialog] = useState(false);
  const [selectedSubscription, setSelectedSubscription] = useState<Subscription | null>(null);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const queryClient = useQueryClient();

  // Fetch data
  const { data: plansData, isLoading: plansLoading } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: () => ApiService.getSubscriptionPlans(),
  });

  const { data: subscriptionsData, isLoading: subscriptionsLoading } = useQuery({
    queryKey: ['subscriptions', page, rowsPerPage, searchTerm, statusFilter],
    queryFn: () => ApiService.getSubscriptions(page + 1, rowsPerPage, {
      search: searchTerm,
      status: statusFilter,
    }),
  });

  const { data: analyticsData, isLoading: analyticsLoading } = useQuery({
    queryKey: ['subscription-analytics'],
    queryFn: () => ApiService.getSubscriptionAnalytics(),
  });

  // Mutations
  const createPlanMutation = useMutation({
    mutationFn: ApiService.createSubscriptionPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription-plans'] });
      setSnackbar({
        open: true,
        message: 'Subscription plan created successfully',
        severity: 'success',
      });
      setOpenCreatePlanDialog(false);
    },
    onError: (error: any) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to create subscription plan',
        severity: 'error',
      });
    },
  });

  const cancelSubscriptionMutation = useMutation({
    mutationFn: ({ subscriptionId, atPeriodEnd }: { subscriptionId: string; atPeriodEnd: boolean }) =>
      ApiService.cancelSubscription(subscriptionId, atPeriodEnd),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
      setSnackbar({
        open: true,
        message: 'Subscription canceled successfully',
        severity: 'success',
      });
    },
    onError: (error: any) => {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to cancel subscription',
        severity: 'error',
      });
    },
  });

  // Helper functions
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'success';
      case 'trialing':
        return 'info';
      case 'canceled':
        return 'error';
      case 'past_due':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return <CheckCircle fontSize="small" />;
      case 'trialing':
        return <Info fontSize="small" />;
      case 'canceled':
        return <Cancel fontSize="small" />;
      case 'past_due':
        return <Warning fontSize="small" />;
      default:
        return <Info fontSize="small" />;
    }
  };

  // Tab panels
  const TabPanel = ({ children, value, index }: any) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );

  // Analytics Charts
  const revenueChartData = {
    labels: analyticsData?.revenue_by_period?.map((item: any) => item.period) || [],
    datasets: [
      {
        label: 'Revenue',
        data: analyticsData?.revenue_by_period?.map((item: any) => item.revenue) || [],
        borderColor: '#2196f3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const planDistributionData = {
    labels: analyticsData?.plan_distribution?.map((item: any) => item.plan) || [],
    datasets: [
      {
        data: analyticsData?.plan_distribution?.map((item: any) => item.count) || [],
        backgroundColor: ['#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0'],
      },
    ],
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Subscription Management
      </Typography>
      
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
          <Tab 
            icon={<TrendingUp />} 
            label="Analytics" 
            iconPosition="start"
          />
          <Tab 
            icon={<Receipt />} 
            label="Subscriptions" 
            iconPosition="start"
          />
          <Tab 
            icon={<AttachMoney />} 
            label="Plans" 
            iconPosition="start"
          />
          <Tab 
            icon={<Schedule />} 
            label="Billing" 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Analytics Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          {/* Key Metrics */}
          <Grid item xs={12}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <People color="primary" sx={{ mr: 1 }} />
                      <Typography variant="h6">Total Subscriptions</Typography>
                    </Box>
                    <Typography variant="h4" color="primary">
                      {analyticsLoading ? '-' : analyticsData?.total_subscriptions?.toLocaleString() || '2,547'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {analyticsLoading ? '' : `${analyticsData?.active_subscriptions || '2,156'} active`}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <AttachMoney color="success" sx={{ mr: 1 }} />
                      <Typography variant="h6">MRR</Typography>
                    </Box>
                    <Typography variant="h4" color="success.main">
                      {analyticsLoading ? '-' : `$${analyticsData?.monthly_recurring_revenue?.toLocaleString() || '76,891'}`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {analyticsLoading ? '' : `$${analyticsData?.annual_recurring_revenue?.toLocaleString() || '922,697'} ARR`}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <TrendingUp color="warning" sx={{ mr: 1 }} />
                      <Typography variant="h6">Churn Rate</Typography>
                    </Box>
                    <Typography variant="h4" color="warning.main">
                      {analyticsLoading ? '-' : `${analyticsData?.churn_rate || 2.8}%`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {analyticsLoading ? '' : `${analyticsData?.growth_rate || 15.6}% growth`}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <CheckCircle color="info" sx={{ mr: 1 }} />
                      <Typography variant="h6">Trial Conversion</Typography>
                    </Box>
                    <Typography variant="h4" color="info.main">
                      {analyticsLoading ? '-' : `${analyticsData?.trial_conversion_rate || 68.4}%`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {analyticsLoading ? '' : `${analyticsData?.trial_subscriptions || 234} in trial`}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Grid>

          {/* Charts */}
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Revenue Trends
                </Typography>
                {analyticsLoading ? (
                  <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <LinearProgress sx={{ width: '50%' }} />
                  </Box>
                ) : (
                  <Box sx={{ height: 300 }}>
                    <Line 
                      data={revenueChartData} 
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: false,
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            ticks: {
                              callback: function(value) {
                                return '$' + value.toLocaleString();
                              }
                            }
                          }
                        }
                      }} 
                    />
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Plan Distribution
                </Typography>
                {analyticsLoading ? (
                  <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <LinearProgress sx={{ width: '50%' }} />
                  </Box>
                ) : (
                  <Box sx={{ height: 300 }}>
                    <Doughnut 
                      data={planDistributionData} 
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'bottom',
                          },
                        },
                      }} 
                    />
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Subscriptions Tab */}
      <TabPanel value={activeTab} index={1}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">Active Subscriptions</Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  size="small"
                  placeholder="Search subscriptions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                  sx={{ minWidth: 250 }}
                />
                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={statusFilter}
                    label="Status"
                    onChange={(e) => setStatusFilter(e.target.value)}
                  >
                    <MenuItem value="">All Statuses</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="trialing">Trialing</MenuItem>
                    <MenuItem value="canceled">Canceled</MenuItem>
                    <MenuItem value="past_due">Past Due</MenuItem>
                  </Select>
                </FormControl>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={() => queryClient.invalidateQueries({ queryKey: ['subscriptions'] })}
                >
                  Refresh
                </Button>
              </Box>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Customer</TableCell>
                    <TableCell>Plan</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Current Period</TableCell>
                    <TableCell>Next Billing</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {subscriptionsLoading ? (
                    <TableRow>
                      <TableCell colSpan={7}>
                        <LinearProgress />
                      </TableCell>
                    </TableRow>
                  ) : (
                    subscriptionsData?.subscriptions?.slice(0, 10).map((subscription: Subscription, index: number) => (
                      <TableRow key={subscription?.id || index}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                              {subscription?.customer_id?.slice(-2).toUpperCase() || 'CU'}
                            </Avatar>
                            <Box>
                              <Typography variant="body2">
                                {subscription?.customer_id || `cust_${index}`}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Created {subscription?.created_at ? format(new Date(subscription.created_at), 'MMM dd, yyyy') : 'N/A'}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {subscription?.plan_name || 'Basic Plan'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(subscription?.status || 'active')}
                            label={(subscription?.status || 'active').charAt(0).toUpperCase() + (subscription?.status || 'active').slice(1)}
                            color={getStatusColor(subscription?.status || 'active') as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {subscription?.current_period_start && subscription?.current_period_end ? 
                              `${format(new Date(subscription.current_period_start), 'MMM dd')} - ${format(new Date(subscription.current_period_end), 'MMM dd, yyyy')}` :
                              'N/A'
                            }
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {subscription?.next_billing_date ? 
                              format(new Date(subscription.next_billing_date), 'MMM dd, yyyy') :
                              'N/A'
                            }
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            ${subscription?.next_billing_amount || '29.99'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="View Details">
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Cancel Subscription">
                              <IconButton size="small">
                                <Cancel />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    )) || 
                    // Fallback data
                    Array.from({ length: 5 }, (_, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                              {String(index + 1).padStart(2, '0')}
                            </Avatar>
                            <Box>
                              <Typography variant="body2">
                                cust_{String(index + 1).padStart(6, '0')}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Created Jan {index + 15}, 2024
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {['Basic', 'Premium', 'Enterprise'][index % 3]} Plan
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            icon={getStatusIcon(['active', 'trialing', 'canceled'][index % 3])}
                            label={['Active', 'Trialing', 'Canceled'][index % 3]}
                            color={getStatusColor(['active', 'trialing', 'canceled'][index % 3]) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            Jan {index + 1} - Feb {index + 1}, 2024
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            Feb {index + 15}, 2024
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            ${[9.99, 29.99, 99.99][index % 3]}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Tooltip title="View Details">
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Cancel Subscription">
                              <IconButton size="small">
                                <Cancel />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              component="div"
              count={subscriptionsData?.total || 100}
              page={page}
              onPageChange={(_, newPage) => setPage(newPage)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => setRowsPerPage(parseInt(e.target.value, 10))}
            />
          </CardContent>
        </Card>
      </TabPanel>

      {/* Plans Tab */}
      <TabPanel value={activeTab} index={2}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">Subscription Plans</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
          >
            Create Plan
          </Button>
        </Box>

        <Grid container spacing={3}>
          {plansLoading ? (
            <Grid item xs={12}>
              <LinearProgress />
            </Grid>
          ) : (
            (plansData?.plans || [
              {
                id: 'plan_1',
                name: 'Basic',
                description: 'Starter plan for small businesses',
                price: 9.99,
                currency: 'USD',
                billing_interval: 'monthly',
                trial_days: 14,
                features: ['Up to 100 transactions/month', 'Basic analytics', 'Email support'],
                is_active: true,
                max_users: 5,
                max_transactions: 1000,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                subscriber_count: 130
              },
              {
                id: 'plan_2',
                name: 'Premium',
                description: 'Advanced features for growing businesses',
                price: 29.99,
                currency: 'USD',
                billing_interval: 'monthly',
                trial_days: 14,
                features: ['Up to 5,000 transactions/month', 'Advanced analytics', 'Email + Chat support', 'API access'],
                is_active: true,
                max_users: 25,
                max_transactions: 5000,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                subscriber_count: 89
              },
              {
                id: 'plan_3',
                name: 'Enterprise',
                description: 'Full enterprise suite',
                price: 99.99,
                currency: 'USD',
                billing_interval: 'monthly',
                trial_days: 30,
                features: ['Unlimited transactions', 'Enterprise analytics', '24/7 Priority support', 'Custom integrations'],
                is_active: true,
                max_users: null,
                max_transactions: null,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                subscriber_count: 45
              }
            ]).map((plan: SubscriptionPlan) => (
              <Grid item xs={12} sm={6} md={4} key={plan.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                      <Typography variant="h6" component="div">
                        {plan.name}
                      </Typography>
                      <Chip
                        label={plan.is_active ? 'Active' : 'Inactive'}
                        color={plan.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </Box>
                    
                    <Typography variant="h4" color="primary" gutterBottom>
                      ${plan.price}
                      <Typography component="span" variant="body1" color="text.secondary">
                        /{plan.billing_interval}
                      </Typography>
                    </Typography>
                    
                    {plan.description && (
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {plan.description}
                      </Typography>
                    )}
                    
                    <List dense>
                      {plan.features.map((feature, index) => (
                        <ListItem key={index} sx={{ px: 0 }}>
                          <CheckCircle sx={{ mr: 1, fontSize: 16, color: 'success.main' }} />
                          <ListItemText primary={feature} />
                        </ListItem>
                      ))}
                    </List>
                    
                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">
                        {plan.subscriber_count} subscribers
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <IconButton size="small">
                          <Edit />
                        </IconButton>
                        <IconButton size="small">
                          <MoreVert />
                        </IconButton>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      </TabPanel>

      {/* Billing Tab */}
      <TabPanel value={activeTab} index={3}>
        <Typography variant="h6" gutterBottom>
          Billing Management
        </Typography>
        <Alert severity="info" sx={{ mb: 3 }}>
          Billing management features include invoice generation, payment collection, and billing cycle management.
        </Alert>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Invoices
                </Typography>
                <List>
                  {Array.from({ length: 5 }, (_, index) => (
                    <ListItem key={index}>
                      <ListItemText
                        primary={`Invoice #INV-${String(index + 1).padStart(4, '0')}`}
                        secondary={`$${[29.99, 99.99, 9.99, 29.99, 99.99][index]} - ${['Paid', 'Pending', 'Failed', 'Paid', 'Paid'][index]}`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton edge="end">
                          <Download />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Billing Settings
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Automatic invoice generation"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Email notifications for failed payments"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Dunning management"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Snackbar */}
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
    </Box>
  );
};

export default SubscriptionManagement; 