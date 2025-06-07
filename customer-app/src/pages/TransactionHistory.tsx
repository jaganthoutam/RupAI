import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material'
import {
  Search,
  FilterList,
  Download,
  Visibility,
  TrendingUp,
  TrendingDown,
  Payment,
  Refresh
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import apiService from '../services/apiService'

interface Transaction {
  id: string
  type: 'payment' | 'transfer' | 'refund' | 'deposit'
  amount: number
  currency: string
  status: 'completed' | 'pending' | 'failed' | 'cancelled'
  description: string
  recipient?: string
  sender?: string
  created_at: string
  updated_at: string
  metadata?: any
}

const TransactionHistory: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null)
  const [detailsOpen, setDetailsOpen] = useState(false)

  const { user } = useAuth()

  useEffect(() => {
    loadTransactions()
  }, [])

  const loadTransactions = async () => {
    try {
      setLoading(true)
      const response = await apiService.getTransactions()
      
      // Transform the response to match our interface
      const transformedTransactions = response.map((tx: any) => ({
        id: tx.id || `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: tx.type || 'payment',
        amount: tx.amount || 0,
        currency: tx.currency || 'USD',
        status: tx.status || 'completed',
        description: tx.description || 'Transaction',
        recipient: tx.recipient || tx.metadata?.recipient,
        sender: tx.sender || user?.email,
        created_at: tx.created_at || new Date().toISOString(),
        updated_at: tx.updated_at || tx.created_at || new Date().toISOString(),
        metadata: tx.metadata || {}
      }))

      setTransactions(transformedTransactions)
    } catch (err: any) {
      setError('Failed to load transactions')
    } finally {
      setLoading(false)
    }
  }

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleViewDetails = (transaction: Transaction) => {
    setSelectedTransaction(transaction)
    setDetailsOpen(true)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'pending':
        return 'warning'
      case 'failed':
        return 'error'
      case 'cancelled':
        return 'default'
      default:
        return 'default'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'payment':
        return <Payment />
      case 'transfer':
        return <TrendingUp />
      case 'deposit':
        return <TrendingDown />
      default:
        return <Payment />
    }
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const filteredTransactions = transactions.filter((transaction) => {
    const matchesSearch = transaction.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         transaction.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (transaction.recipient && transaction.recipient.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesStatus = statusFilter === 'all' || transaction.status === statusFilter
    const matchesType = typeFilter === 'all' || transaction.type === typeFilter

    return matchesSearch && matchesStatus && matchesType
  })

  const paginatedTransactions = filteredTransactions.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Transaction History
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        View and manage all your payment transactions.
      </Typography>

      {/* Filters and Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search transactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="failed">Failed</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={typeFilter}
                  label="Type"
                  onChange={(e) => setTypeFilter(e.target.value)}
                >
                  <MenuItem value="all">All Types</MenuItem>
                  <MenuItem value="payment">Payment</MenuItem>
                  <MenuItem value="transfer">Transfer</MenuItem>
                  <MenuItem value="refund">Refund</MenuItem>
                  <MenuItem value="deposit">Deposit</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box display="flex" gap={1}>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadTransactions}
                  disabled={loading}
                >
                  Refresh
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Download />}
                >
                  Export
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Transaction</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedTransactions.map((transaction) => (
                <TableRow key={transaction.id} hover>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Avatar sx={{ width: 40, height: 40 }}>
                        {getTypeIcon(transaction.type)}
                      </Avatar>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {transaction.description}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          ID: {transaction.id}
                        </Typography>
                        {transaction.recipient && (
                          <Typography variant="body2" color="text.secondary">
                            To: {transaction.recipient}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}
                      variant="outlined"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography
                      variant="body1"
                      sx={{
                        fontWeight: 600,
                        color: transaction.type === 'deposit' ? 'success.main' : 'text.primary'
                      }}
                    >
                      {transaction.type === 'deposit' ? '+' : ''}
                      {formatCurrency(transaction.amount, transaction.currency)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={transaction.status.charAt(0).toUpperCase() + transaction.status.slice(1)}
                      color={getStatusColor(transaction.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(transaction.created_at)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleViewDetails(transaction)}
                    >
                      <Visibility />
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
          count={filteredTransactions.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Card>

      {/* Transaction Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Transaction Details
        </DialogTitle>
        <DialogContent>
          {selectedTransaction && (
            <Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Transaction ID"
                        secondary={selectedTransaction.id}
                      />
                    </ListItem>
                    <Divider />
                    <ListItem>
                      <ListItemText
                        primary="Type"
                        secondary={selectedTransaction.type.charAt(0).toUpperCase() + selectedTransaction.type.slice(1)}
                      />
                    </ListItem>
                    <Divider />
                    <ListItem>
                      <ListItemText
                        primary="Amount"
                        secondary={formatCurrency(selectedTransaction.amount, selectedTransaction.currency)}
                      />
                    </ListItem>
                    <Divider />
                    <ListItem>
                      <ListItemText
                        primary="Status"
                        secondary={
                          <Chip
                            label={selectedTransaction.status.charAt(0).toUpperCase() + selectedTransaction.status.slice(1)}
                            color={getStatusColor(selectedTransaction.status) as any}
                            size="small"
                          />
                        }
                      />
                    </ListItem>
                  </List>
                </Grid>
                <Grid item xs={12} md={6}>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Description"
                        secondary={selectedTransaction.description}
                      />
                    </ListItem>
                    <Divider />
                    {selectedTransaction.recipient && (
                      <>
                        <ListItem>
                          <ListItemText
                            primary="Recipient"
                            secondary={selectedTransaction.recipient}
                          />
                        </ListItem>
                        <Divider />
                      </>
                    )}
                    <ListItem>
                      <ListItemText
                        primary="Created"
                        secondary={formatDate(selectedTransaction.created_at)}
                      />
                    </ListItem>
                    <Divider />
                    <ListItem>
                      <ListItemText
                        primary="Last Updated"
                        secondary={formatDate(selectedTransaction.updated_at)}
                      />
                    </ListItem>
                  </List>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default TransactionHistory 