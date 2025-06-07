import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  IconButton,
  Tooltip,
  Avatar,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Error,
  Pending,
  Refresh,
  MoreVert,
} from '@mui/icons-material';
import { format } from 'date-fns';

interface Transaction {
  id: string;
  amount: number;
  currency: string;
  status: 'completed' | 'pending' | 'failed' | 'refunded';
  method: string;
  customer: string;
  timestamp: string;
}

interface RecentTransactionsProps {
  transactions: Transaction[];
  loading?: boolean;
  onRefresh?: () => void;
  onViewDetails?: (transactionId: string) => void;
}

const RecentTransactions: React.FC<RecentTransactionsProps> = ({
  transactions = [],
  loading = false,
  onRefresh,
  onViewDetails,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'failed':
        return 'error';
      case 'refunded':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle fontSize="small" color="success" />;
      case 'pending':
        return <Pending fontSize="small" color="warning" />;
      case 'failed':
        return <Error fontSize="small" color="error" />;
      case 'refunded':
        return <Warning fontSize="small" color="action" />;
      default:
        return <Pending fontSize="small" color="action" />;
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  // Sample data if no transactions provided
  const sampleTransactions: Transaction[] = [
    {
      id: 'txn_1234567890',
      amount: 99.99,
      currency: 'USD',
      status: 'completed',
      method: 'Card',
      customer: 'john.doe@example.com',
      timestamp: new Date().toISOString(),
    },
    {
      id: 'txn_1234567891',
      amount: 150.00,
      currency: 'USD',
      status: 'pending',
      method: 'Bank Transfer',
      customer: 'jane.smith@example.com',
      timestamp: new Date(Date.now() - 300000).toISOString(),
    },
    {
      id: 'txn_1234567892',
      amount: 75.50,
      currency: 'USD',
      status: 'completed',
      method: 'Wallet',
      customer: 'bob.wilson@example.com',
      timestamp: new Date(Date.now() - 600000).toISOString(),
    },
  ];

  const displayTransactions = transactions.length > 0 ? transactions : sampleTransactions;

  return (
    <Card elevation={2}>
      <CardHeader
        title="Recent Transactions"
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {onRefresh && (
              <Tooltip title="Refresh transactions">
                <IconButton onClick={onRefresh} disabled={loading}>
                  <Refresh />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        }
        sx={{ pb: 1 }}
      />
      <CardContent sx={{ pt: 0 }}>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Transaction</TableCell>
                <TableCell>Customer</TableCell>
                <TableCell>Method</TableCell>
                <TableCell align="right">Amount</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Time</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {displayTransactions.slice(0, 10).map((transaction) => (
                <TableRow
                  key={transaction.id}
                  sx={{
                    '&:hover': {
                      backgroundColor: 'grey.50',
                    },
                  }}
                >
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {transaction.id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                        {transaction.customer.charAt(0).toUpperCase()}
                      </Avatar>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 120 }}>
                        {transaction.customer}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {transaction.method}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight={500}>
                      {formatCurrency(transaction.amount, transaction.currency)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={getStatusIcon(transaction.status)}
                      label={transaction.status.charAt(0).toUpperCase() + transaction.status.slice(1)}
                      size="small"
                      color={getStatusColor(transaction.status) as any}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {format(new Date(transaction.timestamp), 'MMM dd, HH:mm')}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    {onViewDetails && (
                      <Tooltip title="View details">
                        <IconButton
                          size="small"
                          onClick={() => onViewDetails(transaction.id)}
                        >
                          <MoreVert fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {displayTransactions.length > 10 && (
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              Showing 10 of {displayTransactions.length} transactions
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default RecentTransactions; 