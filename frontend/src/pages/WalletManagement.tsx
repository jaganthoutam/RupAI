import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Tab,
  Tabs,
  Paper,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Fab,
  Menu,
  Divider,
} from '@mui/material';
import {
  AccountBalance,
  Add,
  Send,
  Receipt,
  Refresh,
  MoreVert,
  TrendingUp,
  TrendingDown,
  Wallet as WalletIcon,
  CreditCard,
  AttachMoney,
  SwapHoriz,
  History,
  AccountBalanceWallet,
  Download,
  Upload,
  FilterList,
  Search,
} from '@mui/icons-material';
import { Helmet } from 'react-helmet-async';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import numeral from 'numeral';

// Services
import { walletService } from '../services/walletService';
import { mcpService } from '../services/mcpService';

// Types
interface Wallet {
  id: string;
  customer_id: string;
  currency: string;
  balance: number;
  available_balance: number;
  pending_balance: number;
  status: 'active' | 'frozen' | 'suspended';
  created_at: string;
  updated_at: string;
}

interface WalletTransaction {
  id: string;
  wallet_id: string;
  type: 'credit' | 'debit' | 'transfer_in' | 'transfer_out';
  amount: number;
  currency: string;
  description: string;
  reference: string;
  status: 'completed' | 'pending' | 'failed';
  created_at: string;
  metadata?: any;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`wallet-tabpanel-${index}`}
    aria-labelledby={`wallet-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const WalletManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [createWalletOpen, setCreateWalletOpen] = useState(false);
  const [transferOpen, setTransferOpen] = useState(false);
  const [topUpOpen, setTopUpOpen] = useState(false);
  const [selectedWallet, setSelectedWallet] = useState<Wallet | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [currencyFilter, setCurrencyFilter] = useState('');

  // Form states
  const [walletForm, setWalletForm] = useState({
    customer_id: '',
    currency: 'USD',
    initial_balance: 0,
  });

  const [transferForm, setTransferForm] = useState({
    from_wallet_id: '',
    to_wallet_id: '',
    amount: 0,
    currency: 'USD',
    description: '',
  });

  const [topUpForm, setTopUpForm] = useState({
    wallet_id: '',
    amount: 0,
    payment_method: 'card',
    description: '',
  });

  const queryClient = useQueryClient();

  // Mock data for wallets since service doesn't exist yet
  const walletsData = {
    data: [
      {
        id: 'wallet_123456789',
        customer_id: 'cust_001',
        currency: 'USD',
        balance: 1250.50,
        available_balance: 1200.50,
        pending_balance: 50.00,
        status: 'active' as const,
        created_at: '2024-01-15T10:00:00Z',
        updated_at: '2024-01-15T15:30:00Z',
      },
      {
        id: 'wallet_987654321',
        customer_id: 'cust_002',
        currency: 'EUR',
        balance: 890.75,
        available_balance: 890.75,
        pending_balance: 0.00,
        status: 'active' as const,
        created_at: '2024-01-10T14:20:00Z',
        updated_at: '2024-01-15T12:10:00Z',
      },
    ],
    total: 2,
  };

  const transactionsData = {
    data: [
      {
        id: 'txn_001',
        wallet_id: 'wallet_123456789',
        type: 'credit' as const,
        amount: 500.00,
        currency: 'USD',
        description: 'Wallet top-up via card',
        reference: 'ref_001',
        status: 'completed' as const,
        created_at: '2024-01-15T15:30:00Z',
      },
      {
        id: 'txn_002',
        wallet_id: 'wallet_123456789',
        type: 'debit' as const,
        amount: 25.00,
        currency: 'USD',
        description: 'Payment to merchant',
        reference: 'ref_002',
        status: 'completed' as const,
        created_at: '2024-01-15T14:20:00Z',
      },
    ],
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'frozen': return 'warning';
      case 'suspended': return 'error';
      default: return 'default';
    }
  };

  const getTransactionTypeIcon = (type: string) => {
    switch (type) {
      case 'credit':
      case 'transfer_in':
        return <TrendingUp sx={{ color: 'success.main' }} />;
      case 'debit':
      case 'transfer_out':
        return <TrendingDown sx={{ color: 'error.main' }} />;
      default:
        return <SwapHoriz />;
    }
  };

  const formatCurrency = (amount: number, currency: string) => 
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount);

  const wallets = walletsData?.data || [];
  const totalWallets = walletsData?.total || 0;
  const transactions = transactionsData?.data || [];

  // Statistics calculations
  const totalBalance = wallets.reduce((sum, wallet) => sum + wallet.balance, 0);
  const activeWallets = wallets.filter(w => w.status === 'active').length;
  const currencies = [...new Set(wallets.map(w => w.currency))];

  return (
    <>
      <Helmet>
        <title>Wallet Management - MCP Payments</title>
        <meta name="description" content="Manage multi-currency wallets, transfers, and balances" />
      </Helmet>

      <Box sx={{ flexGrow: 1, p: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Wallet Management
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Manage multi-currency wallets and fund transfers
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={() => console.log('Refresh')}
            >
              Refresh
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setCreateWalletOpen(true)}
            >
              Create Wallet
            </Button>
          </Box>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Total Wallets
                    </Typography>
                    <Typography variant="h4">
                      {totalWallets.toLocaleString()}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    <WalletIcon />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Active Wallets
                    </Typography>
                    <Typography variant="h4">
                      {activeWallets.toLocaleString()}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'success.main' }}>
                    <AccountBalanceWallet />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Total Balance (USD)
                    </Typography>
                    <Typography variant="h4">
                      {formatCurrency(totalBalance, 'USD')}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'info.main' }}>
                    <AttachMoney />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Currencies
                    </Typography>
                    <Typography variant="h4">
                      {currencies.length}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'warning.main' }}>
                    <CreditCard />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Main Content Tabs */}
        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab icon={<WalletIcon />} label="Wallets Overview" />
              <Tab icon={<History />} label="Transaction History" />
              <Tab icon={<SwapHoriz />} label="Fund Transfers" />
            </Tabs>
          </Box>

          {/* Wallets Overview Tab */}
          <TabPanel value={tabValue} index={0}>
            {/* Filters */}
            <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
              <TextField
                label="Search Customer ID"
                variant="outlined"
                size="small"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
                sx={{ minWidth: 200 }}
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
                  <MenuItem value="frozen">Frozen</MenuItem>
                  <MenuItem value="suspended">Suspended</MenuItem>
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Currency</InputLabel>
                <Select
                  value={currencyFilter}
                  label="Currency"
                  onChange={(e) => setCurrencyFilter(e.target.value)}
                >
                  <MenuItem value="">All Currencies</MenuItem>
                  {currencies.map((currency) => (
                    <MenuItem key={currency} value={currency}>{currency}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                variant="outlined"
                startIcon={<Send />}
                onClick={() => setTransferOpen(true)}
              >
                Transfer Funds
              </Button>

              <Button
                variant="outlined"
                startIcon={<Upload />}
                onClick={() => setTopUpOpen(true)}
              >
                Top Up Wallet
              </Button>
            </Box>

            {/* Wallets Table */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Wallet ID</TableCell>
                    <TableCell>Customer ID</TableCell>
                    <TableCell>Currency</TableCell>
                    <TableCell align="right">Balance</TableCell>
                    <TableCell align="right">Available</TableCell>
                    <TableCell align="right">Pending</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {wallets.map((wallet) => (
                    <TableRow key={wallet.id} hover>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                        {wallet.id.substring(0, 8)}...
                      </TableCell>
                      <TableCell>{wallet.customer_id}</TableCell>
                      <TableCell>
                        <Chip label={wallet.currency} size="small" />
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                        {formatCurrency(wallet.balance, wallet.currency)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(wallet.available_balance, wallet.currency)}
                      </TableCell>
                      <TableCell align="right">
                        {formatCurrency(wallet.pending_balance, wallet.currency)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={wallet.status.toUpperCase()}
                          color={getStatusColor(wallet.status) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {format(new Date(wallet.created_at), 'MMM dd, yyyy')}
                      </TableCell>
                      <TableCell>
                        <IconButton
                          onClick={() => setSelectedWallet(wallet)}
                          size="small"
                        >
                          <Receipt />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <TablePagination
              rowsPerPageOptions={[5, 10, 25, 50]}
              component="div"
              count={totalWallets}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </TabPanel>

          {/* Transaction History Tab */}
          <TabPanel value={tabValue} index={1}>
            {selectedWallet ? (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Transaction History - {selectedWallet.currency} Wallet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Wallet ID: {selectedWallet.id}
                </Typography>

                <List>
                  {transactions.map((transaction: WalletTransaction) => (
                    <React.Fragment key={transaction.id}>
                      <ListItem>
                        <ListItemIcon>
                          {getTransactionTypeIcon(transaction.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="body1">
                                {transaction.description}
                              </Typography>
                              <Typography
                                variant="body1"
                                sx={{
                                  fontWeight: 'bold',
                                  color: transaction.type.includes('in') || transaction.type === 'credit'
                                    ? 'success.main'
                                    : 'error.main'
                                }}
                              >
                                {transaction.type.includes('in') || transaction.type === 'credit' ? '+' : '-'}
                                {formatCurrency(transaction.amount, transaction.currency)}
                              </Typography>
                            </Box>
                          }
                          secondary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="body2" color="text.secondary">
                                {format(new Date(transaction.created_at), 'MMM dd, yyyy HH:mm')}
                              </Typography>
                              <Chip
                                label={transaction.status.toUpperCase()}
                                size="small"
                                color={transaction.status === 'completed' ? 'success' : 'warning'}
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                      <Divider variant="inset" component="li" />
                    </React.Fragment>
                  ))}
                  {transactions.length === 0 && (
                    <ListItem>
                      <ListItemText
                        primary="No transactions found"
                        secondary="Select a wallet to view its transaction history"
                      />
                    </ListItem>
                  )}
                </List>
              </Box>
            ) : (
              <Alert severity="info">
                Select a wallet from the overview tab to view its transaction history.
              </Alert>
            )}
          </TabPanel>

          {/* Fund Transfers Tab */}
          <TabPanel value={tabValue} index={2}>
            <Typography variant="h6" gutterBottom>
              Recent Fund Transfers
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              View and manage fund transfers between wallets
            </Typography>

            <Button
              variant="contained"
              startIcon={<Send />}
              onClick={() => setTransferOpen(true)}
              sx={{ mb: 3 }}
            >
              New Transfer
            </Button>

            {/* Transfers would be displayed here */}
            <Alert severity="info">
              Transfer history and management features will be displayed here.
            </Alert>
          </TabPanel>
        </Paper>

        {/* Create Wallet Dialog */}
        <Dialog open={createWalletOpen} onClose={() => setCreateWalletOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Create New Wallet</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Customer ID"
                  value={walletForm.customer_id}
                  onChange={(e) => setWalletForm({ ...walletForm, customer_id: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={walletForm.currency}
                    label="Currency"
                    onChange={(e) => setWalletForm({ ...walletForm, currency: e.target.value })}
                  >
                    <MenuItem value="USD">USD</MenuItem>
                    <MenuItem value="EUR">EUR</MenuItem>
                    <MenuItem value="GBP">GBP</MenuItem>
                    <MenuItem value="INR">INR</MenuItem>
                    <MenuItem value="JPY">JPY</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Initial Balance"
                  value={walletForm.initial_balance}
                  onChange={(e) => setWalletForm({ ...walletForm, initial_balance: Number(e.target.value) })}
                  inputProps={{ min: 0, step: 0.01 }}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateWalletOpen(false)}>Cancel</Button>
            <Button
              onClick={() => {
                console.log('Creating wallet:', walletForm);
                setCreateWalletOpen(false);
              }}
              variant="contained"
              disabled={!walletForm.customer_id}
            >
              Create Wallet
            </Button>
          </DialogActions>
        </Dialog>

        {/* Transfer Funds Dialog */}
        <Dialog open={transferOpen} onClose={() => setTransferOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Transfer Funds</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="From Wallet ID"
                  value={transferForm.from_wallet_id}
                  onChange={(e) => setTransferForm({ ...transferForm, from_wallet_id: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="To Wallet ID"
                  value={transferForm.to_wallet_id}
                  onChange={(e) => setTransferForm({ ...transferForm, to_wallet_id: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Amount"
                  value={transferForm.amount}
                  onChange={(e) => setTransferForm({ ...transferForm, amount: Number(e.target.value) })}
                  inputProps={{ min: 0.01, step: 0.01 }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={transferForm.currency}
                    label="Currency"
                    onChange={(e) => setTransferForm({ ...transferForm, currency: e.target.value })}
                  >
                    <MenuItem value="USD">USD</MenuItem>
                    <MenuItem value="EUR">EUR</MenuItem>
                    <MenuItem value="GBP">GBP</MenuItem>
                    <MenuItem value="INR">INR</MenuItem>
                    <MenuItem value="JPY">JPY</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={2}
                  value={transferForm.description}
                  onChange={(e) => setTransferForm({ ...transferForm, description: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setTransferOpen(false)}>Cancel</Button>
            <Button
              onClick={() => {
                console.log('Transferring funds:', transferForm);
                setTransferOpen(false);
              }}
              variant="contained"
              disabled={!transferForm.from_wallet_id || !transferForm.to_wallet_id}
            >
              Transfer Funds
            </Button>
          </DialogActions>
        </Dialog>

        {/* Top Up Wallet Dialog */}
        <Dialog open={topUpOpen} onClose={() => setTopUpOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Top Up Wallet</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Wallet ID"
                  value={topUpForm.wallet_id}
                  onChange={(e) => setTopUpForm({ ...topUpForm, wallet_id: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Amount"
                  value={topUpForm.amount}
                  onChange={(e) => setTopUpForm({ ...topUpForm, amount: Number(e.target.value) })}
                  inputProps={{ min: 0.01, step: 0.01 }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={topUpForm.payment_method}
                    label="Payment Method"
                    onChange={(e) => setTopUpForm({ ...topUpForm, payment_method: e.target.value })}
                  >
                    <MenuItem value="card">Credit/Debit Card</MenuItem>
                    <MenuItem value="bank_transfer">Bank Transfer</MenuItem>
                    <MenuItem value="upi">UPI</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={2}
                  value={topUpForm.description}
                  onChange={(e) => setTopUpForm({ ...topUpForm, description: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setTopUpOpen(false)}>Cancel</Button>
            <Button
              onClick={() => {
                console.log('Topping up wallet:', topUpForm);
                setTopUpOpen(false);
              }}
              variant="contained"
              disabled={!topUpForm.wallet_id || topUpForm.amount <= 0}
            >
              Top Up Wallet
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </>
  );
};

export default WalletManagement; 