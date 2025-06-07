import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Tabs,
  Tab,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Chip,
  Alert,
  CircularProgress,
  Paper,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'
import {
  AccountBalanceWallet,
  Add,
  Send,
  TrendingUp,
  TrendingDown,
  CreditCard,
  AccountBalance,
  QrCode2,
  History,
  Refresh,
  Security
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import apiService from '../services/apiService'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`wallet-tabpanel-${index}`}
      aria-labelledby={`wallet-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

interface WalletBalance {
  currency: string
  balance: number
  available: number
  pending: number
}

interface Transaction {
  id: string
  type: 'credit' | 'debit'
  amount: number
  currency: string
  description: string
  status: string
  timestamp: string
}

const WalletPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0)
  const [wallets, setWallets] = useState<WalletBalance[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [addFundsOpen, setAddFundsOpen] = useState(false)
  const [sendMoneyOpen, setSendMoneyOpen] = useState(false)
  
  // Add Funds form
  const [addFundsData, setAddFundsData] = useState({
    amount: '',
    currency: 'USD',
    method: 'card'
  })
  
  // Send Money form
  const [sendMoneyData, setSendMoneyData] = useState({
    amount: '',
    currency: 'USD',
    recipient: '',
    description: ''
  })

  const { user } = useAuth()

  useEffect(() => {
    loadWalletData()
  }, [])

  const loadWalletData = async () => {
    try {
      setLoading(true)
      
      // Load wallet balances
      const walletsResponse = await apiService.getWallets()
      const walletBalances = walletsResponse.map((wallet: any) => ({
        currency: wallet.currency || 'USD',
        balance: wallet.balance || 0,
        available: wallet.available_balance || wallet.balance || 0,
        pending: wallet.pending_balance || 0
      }))
      
      // Load transactions for the first wallet (or create a default one)
      let walletTransactions: Transaction[] = []
      if (walletsResponse.length > 0) {
        const firstWalletId = walletsResponse[0].id
        const transactionsResponse = await apiService.getTransactions(firstWalletId)
        walletTransactions = transactionsResponse.slice(0, 10).map((tx: any) => ({
          id: tx.id,
          type: tx.amount > 0 ? 'credit' : 'debit',
          amount: Math.abs(tx.amount),
          currency: tx.currency || 'USD',
          description: tx.description || 'Transaction',
          status: tx.status || 'completed',
          timestamp: tx.created_at || new Date().toISOString()
        }))
      }

      setWallets(walletBalances)
      setTransactions(walletTransactions)
    } catch (err: any) {
      setError('Failed to load wallet data')
    } finally {
      setLoading(false)
    }
  }

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue)
  }

  const handleAddFunds = async () => {
    try {
      // Simulate add funds API call
      const response = await apiService.createPayment({
        amount: parseFloat(addFundsData.amount),
        currency: addFundsData.currency,
        payment_method: addFundsData.method,
        customer_id: user?.id || 'customer_123',
        metadata: {
          type: 'add_funds',
          description: 'Add funds to wallet'
        }
      })
      
      setAddFundsOpen(false)
      setAddFundsData({ amount: '', currency: 'USD', method: 'card' })
      loadWalletData() // Refresh data
    } catch (err: any) {
      setError('Failed to add funds')
    }
  }

  const handleSendMoney = async () => {
    try {
      // Simulate send money API call
      const response = await apiService.createPayment({
        amount: parseFloat(sendMoneyData.amount),
        currency: sendMoneyData.currency,
        payment_method: 'wallet',
        customer_id: user?.id || 'customer_123',
        metadata: {
          type: 'send_money',
          recipient: sendMoneyData.recipient,
          description: sendMoneyData.description
        }
      })
      
      setSendMoneyOpen(false)
      setSendMoneyData({ amount: '', currency: 'USD', recipient: '', description: '' })
      loadWalletData() // Refresh data
    } catch (err: any) {
      setError('Failed to send money')
    }
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency
    }).format(amount)
  }

  const getTotalBalance = () => {
    return wallets.reduce((total, wallet) => total + wallet.balance, 0)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Wallet
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your digital wallet, add funds, and send money securely.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Wallet Overview */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  <AccountBalanceWallet fontSize="large" />
                </Avatar>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Total Balance
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 600 }}>
                    {formatCurrency(getTotalBalance(), 'USD')}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Quick Actions
                </Typography>
                <Button
                  startIcon={<Refresh />}
                  onClick={loadWalletData}
                  disabled={loading}
                  size="small"
                >
                  Refresh
                </Button>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<Add />}
                    onClick={() => setAddFundsOpen(true)}
                    sx={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      py: 1.5
                    }}
                  >
                    Add Funds
                  </Button>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Send />}
                    onClick={() => setSendMoneyOpen(true)}
                    sx={{ py: 1.5 }}
                  >
                    Send Money
                  </Button>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<QrCode2 />}
                    sx={{ py: 1.5 }}
                  >
                    QR Code
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs for different sections */}
      <Card>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Balances" />
          <Tab label="Transactions" />
          <Tab label="Settings" />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          {/* Wallet Balances */}
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Currency Balances
          </Typography>
          {loading ? (
            <CircularProgress />
          ) : (
            <Grid container spacing={2}>
              {wallets.map((wallet) => (
                <Grid item xs={12} sm={6} md={4} key={wallet.currency}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="h6" color="primary" gutterBottom>
                      {wallet.currency}
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
                      {formatCurrency(wallet.balance, wallet.currency)}
                    </Typography>
                    <Box display="flex" justifyContent="space-between" mt={2}>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Available
                        </Typography>
                        <Typography variant="body1" color="success.main">
                          {formatCurrency(wallet.available, wallet.currency)}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Pending
                        </Typography>
                        <Typography variant="body1" color="warning.main">
                          {formatCurrency(wallet.pending, wallet.currency)}
                        </Typography>
                      </Box>
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {/* Transaction History */}
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Recent Transactions
          </Typography>
          {loading ? (
            <CircularProgress />
          ) : (
            <List>
              {transactions.map((transaction, index) => (
                <React.Fragment key={transaction.id}>
                  <ListItem>
                    <ListItemIcon>
                      <Avatar
                        sx={{
                          bgcolor: transaction.type === 'credit' ? 'success.light' : 'error.light',
                          width: 40,
                          height: 40
                        }}
                      >
                        {transaction.type === 'credit' ? <TrendingUp /> : <TrendingDown />}
                      </Avatar>
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
                              color: transaction.type === 'credit' ? 'success.main' : 'error.main'
                            }}
                          >
                            {transaction.type === 'credit' ? '+' : '-'}
                            {formatCurrency(transaction.amount, transaction.currency)}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box display="flex" alignItems="center" justifyContent="space-between" mt={1}>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(transaction.timestamp).toLocaleDateString()}
                          </Typography>
                          <Chip
                            label={transaction.status}
                            size="small"
                            color={transaction.status === 'completed' ? 'success' : 'warning'}
                            variant="outlined"
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < transactions.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          {/* Wallet Settings */}
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Wallet Settings
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Security color="primary" />
                  <Typography variant="h6">Security</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Manage your wallet security settings and preferences.
                </Typography>
                <Button variant="outlined" size="small">
                  Manage Security
                </Button>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <History color="primary" />
                  <Typography variant="h6">Limits</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  View and request changes to your transaction limits.
                </Typography>
                <Button variant="outlined" size="small">
                  View Limits
                </Button>
              </Paper>
            </Grid>
          </Grid>
        </TabPanel>
      </Card>

      {/* Add Funds Dialog */}
      <Dialog open={addFundsOpen} onClose={() => setAddFundsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Funds to Wallet</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  value={addFundsData.amount}
                  onChange={(e) => setAddFundsData({ ...addFundsData, amount: e.target.value })}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={addFundsData.currency}
                    label="Currency"
                    onChange={(e) => setAddFundsData({ ...addFundsData, currency: e.target.value })}
                  >
                    <MenuItem value="USD">USD</MenuItem>
                    <MenuItem value="EUR">EUR</MenuItem>
                    <MenuItem value="GBP">GBP</MenuItem>
                    <MenuItem value="INR">INR</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={addFundsData.method}
                    label="Payment Method"
                    onChange={(e) => setAddFundsData({ ...addFundsData, method: e.target.value })}
                  >
                    <MenuItem value="card">Credit/Debit Card</MenuItem>
                    <MenuItem value="bank">Bank Transfer</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddFundsOpen(false)}>Cancel</Button>
          <Button onClick={handleAddFunds} variant="contained">
            Add Funds
          </Button>
        </DialogActions>
      </Dialog>

      {/* Send Money Dialog */}
      <Dialog open={sendMoneyOpen} onClose={() => setSendMoneyOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Send Money</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  value={sendMoneyData.amount}
                  onChange={(e) => setSendMoneyData({ ...sendMoneyData, amount: e.target.value })}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={sendMoneyData.currency}
                    label="Currency"
                    onChange={(e) => setSendMoneyData({ ...sendMoneyData, currency: e.target.value })}
                  >
                    <MenuItem value="USD">USD</MenuItem>
                    <MenuItem value="EUR">EUR</MenuItem>
                    <MenuItem value="GBP">GBP</MenuItem>
                    <MenuItem value="INR">INR</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Recipient"
                  value={sendMoneyData.recipient}
                  onChange={(e) => setSendMoneyData({ ...sendMoneyData, recipient: e.target.value })}
                  placeholder="Email or phone number"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={sendMoneyData.description}
                  onChange={(e) => setSendMoneyData({ ...sendMoneyData, description: e.target.value })}
                  placeholder="What's this for?"
                  multiline
                  rows={2}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSendMoneyOpen(false)}>Cancel</Button>
          <Button onClick={handleSendMoney} variant="contained">
            Send Money
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default WalletPage 