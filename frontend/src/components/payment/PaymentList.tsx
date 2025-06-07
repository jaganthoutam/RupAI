import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Typography,
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Tooltip,
  Avatar,
} from '@mui/material';
import {
  Visibility,
  Refresh,
  Download,
  FilterList,
  Search,
  Payment as PaymentIcon,
  CheckCircle,
  Cancel,
  HourglassEmpty,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { Payment, PaymentStatus, PaymentMethod } from '../../types/payment';
import PaymentService from '../../services/paymentService';

interface PaymentListProps {
  onPaymentSelect?: (payment: Payment) => void;
  refreshTrigger?: number;
}

const PaymentList: React.FC<PaymentListProps> = ({ onPaymentSelect, refreshTrigger }) => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [methodFilter, setMethodFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');

  const getStatusIcon = (status: PaymentStatus) => {
    switch (status) {
      case PaymentStatus.COMPLETED:
        return <CheckCircle sx={{ color: 'success.main' }} />;
      case PaymentStatus.FAILED:
        return <ErrorIcon sx={{ color: 'error.main' }} />;
      case PaymentStatus.CANCELLED:
        return <Cancel sx={{ color: 'warning.main' }} />;
      case PaymentStatus.PENDING:
      case PaymentStatus.PROCESSING:
        return <HourglassEmpty sx={{ color: 'info.main' }} />;
      default:
        return <PaymentIcon />;
    }
  };

  const getStatusColor = (status: PaymentStatus): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    switch (status) {
      case PaymentStatus.COMPLETED:
        return 'success';
      case PaymentStatus.FAILED:
        return 'error';
      case PaymentStatus.CANCELLED:
        return 'warning';
      case PaymentStatus.PENDING:
        return 'info';
      case PaymentStatus.PROCESSING:
        return 'primary';
      case PaymentStatus.REFUNDED:
        return 'secondary';
      default:
        return 'default';
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    const symbols: Record<string, string> = {
      USD: '$',
      EUR: '€',
      GBP: '£',
      INR: '₹',
      JPY: '¥',
    };
    const symbol = symbols[currency] || currency;
    return `${symbol}${amount.toLocaleString()}`;
  };

  const fetchPayments = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        page: page + 1,
        limit: rowsPerPage,
        ...(statusFilter && { status: statusFilter }),
        ...(methodFilter && { method: methodFilter }),
        ...(searchTerm && { customer_id: searchTerm }),
      };

      const response = await PaymentService.getPayments(params);
      
      // Ensure payments is always an array
      const paymentsArray = Array.isArray(response?.payments) ? response.payments : [];
      setPayments(paymentsArray);
      setTotalCount(response?.total || paymentsArray.length);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to fetch payments';
      setError(errorMsg);
      // Set empty array on error to prevent undefined errors
      setPayments([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, [page, rowsPerPage, statusFilter, methodFilter, searchTerm, refreshTrigger]);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleRefresh = () => {
    fetchPayments();
  };

  const handlePaymentClick = (payment: Payment) => {
    onPaymentSelect?.(payment);
  };

  return (
    <Card>
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PaymentIcon />
            <Typography variant="h6">Payments</Typography>
          </Box>
        }
        action={
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Refresh">
              <IconButton onClick={handleRefresh} disabled={loading}>
                <Refresh />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export">
              <IconButton>
                <Download />
              </IconButton>
            </Tooltip>
          </Box>
        }
      />
      <CardContent>
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
              {Object.values(PaymentStatus).map((status) => (
                <MenuItem key={status} value={status}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getStatusIcon(status)}
                    {status.toUpperCase()}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Method</InputLabel>
            <Select
              value={methodFilter}
              label="Method"
              onChange={(e) => setMethodFilter(e.target.value)}
            >
              <MenuItem value="">All Methods</MenuItem>
              {Object.values(PaymentMethod).map((method) => (
                <MenuItem key={method} value={method}>
                  {method.replace('_', ' ').toUpperCase()}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            startIcon={<FilterList />}
            onClick={() => {
              setStatusFilter('');
              setMethodFilter('');
              setSearchTerm('');
            }}
          >
            Clear Filters
          </Button>
        </Box>

        {/* Table */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Payment ID</TableCell>
                <TableCell>Customer</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Method</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">Loading payments...</Typography>
                  </TableCell>
                </TableRow>
              ) : error ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography color="error">{error}</Typography>
                  </TableCell>
                </TableRow>
              ) : !Array.isArray(payments) || payments.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">No payments found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                payments.map((payment) => (
                  <TableRow
                    key={payment.id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => handlePaymentClick(payment)}
                  >
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                          {payment.id.slice(-3)}
                        </Avatar>
                        <Typography variant="body2" fontFamily="monospace">
                          {payment.id.length > 10 ? `${payment.id.slice(0, 10)}...` : payment.id}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {payment.customer_id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {formatCurrency(payment.amount, payment.currency)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={payment.method.replace('_', ' ').toUpperCase()}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(payment.status)}
                        label={payment.status.toUpperCase()}
                        color={getStatusColor(payment.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {format(new Date(payment.created_at), 'MMM dd, yyyy')}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {format(new Date(payment.created_at), 'HH:mm:ss')}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            handlePaymentClick(payment);
                          }}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        {!loading && !error && Array.isArray(payments) && payments.length > 0 && (
          <TablePagination
            component="div"
            count={totalCount}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        )}
      </CardContent>
    </Card>
  );
};

export default PaymentList; 