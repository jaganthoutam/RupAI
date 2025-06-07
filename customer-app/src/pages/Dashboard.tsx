import React, { useState, useEffect } from 'react'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress,
  Avatar,
  Divider,
  Paper
} from '@mui/material'
import {
  Payment,
  AccountBalanceWallet,
  TrendingUp,
  History,
  Add,
  Send,
  Refresh,
  ArrowUpward,
  ArrowDownward,
  CheckCircle,
  Schedule,
  Error
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import { usePayment } from '../contexts/PaymentContext'
import { useNavigate } from 'react-router-dom'
import apiService from '../services/apiService'

interface DashboardStats {
  totalBalance: number
  monthlySpending: number
  pendingTransactions: number
  completedTransactions: number
}

interface RecentTransaction {
  id: string
  type: 'sent' | 'received' | 'payment'
  amount: number
  currency: string
  description: string
  status: 'completed' | 'pending' | 'failed'
  timestamp: string
  recipient?: string
}

const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [stats, setStats] = useState<DashboardStats>({
    totalBalance: 0,
    monthlySpending: 0,
    pendingTransactions: 0,
    completedTransactions: 0
  })
  const [recentTransactions, setRecentTransactions] = useState<RecentTransaction[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load wallet balance
      const walletResponse = await apiService.getWallets()
      const totalBalance = walletResponse.reduce((sum: number, wallet: any) => sum + wallet.balance, 0)
      
      // Load recent transactions
      const transactionsResponse = await apiService.getTransactions()
      const recentTx = transactionsResponse.slice(0, 5).map((tx: any) => ({
        id: tx.id,
        type: tx.type || 'payment',
        amount: tx.amount,
        currency: tx.currency || 'USD',
        description: tx.description || 'Payment',
        status: tx.status || 'completed',
        timestamp: tx.created_at || new Date().toISOString(),
        recipient: tx.recipient
      }))

      // Calculate stats
      const currentMonth = new Date().getMonth()
      const monthlyTx = transactionsResponse.filter((tx: any) => {
        const txMonth = new Date(tx.created_at || new Date()).getMonth()
        return txMonth === currentMonth
      })
      
      const monthlySpending = monthlyTx.reduce((sum: number, tx: any) => sum + (tx.amount || 0), 0)
      const pendingCount = transactionsResponse.filter((tx: any) => tx.status === 'pending').length
      const completedCount = transactionsResponse.filter((tx: any) => tx.status === 'completed').length

      setStats({
        totalBalance,
        monthlySpending,
        pendingTransactions: pendingCount,
        completedTransactions: completedCount
      })
      
      setRecentTransactions(recentTx)
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />
      case 'pending':
        return <Schedule color="warning" />
      case 'failed':
        return <Error color="error" />
      default:
        return <Schedule color="action" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'pending':
        return 'warning'
      case 'failed':
        return 'error'
      default:
        return 'default'
    }
  }

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency
    }).format(amount)
  }

  return (
    <Box>
      {/* Welcome Section */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          Welcome back, {user?.name || 'User'}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here's what's happening with your payments today.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Total Balance
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {formatCurrency(stats.totalBalance)}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}>
                  <AccountBalanceWallet />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Monthly Spending
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {formatCurrency(stats.monthlySpending)}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'error.light' }}>
                  <TrendingUp />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Pending
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {stats.pendingTransactions}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.light' }}>
                  <Schedule />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Completed
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 600 }}>
                    {stats.completedTransactions}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.light' }}>
                  <CheckCircle />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<Payment />}
                  onClick={() => navigate('/pay')}
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    borderRadius: 2
                  }}
                >
                  Make Payment
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Send />}
                  onClick={() => navigate('/wallet')}
                >
                  Send Money
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={() => navigate('/wallet')}
                >
                  Add Funds
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<History />}
                  onClick={() => navigate('/transactions')}
                >
                  View All Transactions
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Transactions */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Recent Transactions
                </Typography>
                <IconButton onClick={loadDashboardData} disabled={loading}>
                  <Refresh />
                </IconButton>
              </Box>
              
              {loading && <LinearProgress sx={{ mb: 2 }} />}
              
              <List>
                {recentTransactions.map((transaction, index) => (
                  <React.Fragment key={transaction.id}>
                    <ListItem sx={{ px: 0 }}>
                      <ListItemIcon>
                        {transaction.type === 'sent' ? (
                          <ArrowUpward color="error" />
                        ) : transaction.type === 'received' ? (
                          <ArrowDownward color="success" />
                        ) : (
                          <Payment color="primary" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" justifyContent="space-between">
                            <Typography variant="body1" sx={{ fontWeight: 500 }}>
                              {transaction.description}
                            </Typography>
                            <Typography
                              variant="body1"
                              sx={{
                                fontWeight: 600,
                                color: transaction.type === 'sent' ? 'error.main' : 'success.main'
                              }}
                            >
                              {transaction.type === 'sent' ? '-' : '+'}
                              {formatCurrency(transaction.amount, transaction.currency)}
                            </Typography>
                          </Box>
                        }
                        secondary={
                          <Box display="flex" alignItems="center" justifyContent="space-between" mt={1}>
                            <Typography variant="body2" color="text.secondary">
                              {new Date(transaction.timestamp).toLocaleDateString()}
                            </Typography>
                            <Box display="flex" alignItems="center" gap={1}>
                              {getStatusIcon(transaction.status)}
                              <Chip
                                label={transaction.status}
                                size="small"
                                color={getStatusColor(transaction.status) as any}
                                variant="outlined"
                              />
                            </Box>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < recentTransactions.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
                
                {recentTransactions.length === 0 && !loading && (
                  <ListItem>
                    <ListItemText
                      primary="No recent transactions"
                      secondary="Start making payments to see your transaction history here."
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard 