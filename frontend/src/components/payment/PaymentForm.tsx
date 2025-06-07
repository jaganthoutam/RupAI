import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Alert,
  CircularProgress,
  Grid,
  Chip,
  InputAdornment,
} from '@mui/material';
import {
  Payment as PaymentIcon,
  CreditCard,
  AccountBalance,
  Wallet,
  QrCode,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import toast from 'react-hot-toast';
import { PaymentMethod, CreatePaymentRequest } from '../../types/payment';
import PaymentService from '../../services/paymentService';

// Validation schema with proper typing
const schema = yup.object({
  amount: yup
    .number()
    .required('Amount is required')
    .min(0.01, 'Amount must be greater than 0')
    .max(1000000, 'Amount exceeds maximum limit'),
  currency: yup
    .string()
    .required('Currency is required')
    .oneOf(['USD', 'EUR', 'GBP', 'INR', 'JPY'], 'Invalid currency'),
  method: yup
    .mixed<PaymentMethod>()
    .required('Payment method is required')
    .oneOf(Object.values(PaymentMethod), 'Invalid payment method'),
  customer_id: yup
    .string()
    .required('Customer ID is required')
    .min(3, 'Customer ID must be at least 3 characters'),
  description: yup.string().optional(),
  metadata: yup.object().optional(),
});

interface PaymentFormProps {
  onSuccess?: (payment: any) => void;
  onError?: (error: string) => void;
}

const PaymentForm: React.FC<PaymentFormProps> = ({ onSuccess, onError }) => {
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      amount: 0,
      currency: 'USD',
      method: PaymentMethod.CARD,
      customer_id: '',
      description: '',
      metadata: {},
    },
  });

  const getPaymentMethodIcon = (method: PaymentMethod) => {
    switch (method) {
      case PaymentMethod.CARD:
        return <CreditCard />;
      case PaymentMethod.BANK_TRANSFER:
        return <AccountBalance />;
      case PaymentMethod.WALLET:
        return <Wallet />;
      case PaymentMethod.UPI:
        return <QrCode />;
      default:
        return <PaymentIcon />;
    }
  };

  const getCurrencySymbol = (currency: string) => {
    const symbols: Record<string, string> = {
      USD: '$',
      EUR: '€',
      GBP: '£',
      INR: '₹',
      JPY: '¥',
    };
    return symbols[currency] || currency;
  };

  const onSubmit = async (data: any) => {
    setLoading(true);
    setSubmitError(null);

    try {
      // Transform data to match CreatePaymentRequest
      const paymentData: CreatePaymentRequest = {
        amount: data.amount,
        currency: data.currency,
        method: data.method,
        customer_id: data.customer_id,
        description: data.description || undefined,
        metadata: data.metadata || undefined,
      };

      const response = await PaymentService.createPayment(paymentData);
      
      if (response.success) {
        toast.success('Payment created successfully!');
        reset();
        onSuccess?.(response.payment);
      } else {
        const errorMsg = response.error || 'Failed to create payment';
        setSubmitError(errorMsg);
        onError?.(errorMsg);
        toast.error(errorMsg);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'An error occurred';
      setSubmitError(errorMsg);
      onError?.(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card sx={{ maxWidth: 600, mx: 'auto' }}>
      <CardHeader
        title={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PaymentIcon color="primary" />
            <Typography variant="h6">Create New Payment</Typography>
          </Box>
        }
        subheader="Enter payment details below"
      />
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={3}>
            {/* Amount and Currency */}
            <Grid item xs={12} sm={8}>
              <Controller
                name="amount"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Amount"
                    type="number"
                    fullWidth
                    inputProps={{ min: 0.01, step: 0.01 }}
                    error={!!errors.amount}
                    helperText={errors.amount?.message}
                    InputProps={{
                      startAdornment: (
                        <Controller
                          name="currency"
                          control={control}
                          render={({ field: currencyField }) => (
                            <InputAdornment position="start">
                              {getCurrencySymbol(currencyField.value)}
                            </InputAdornment>
                          )}
                        />
                      ),
                    }}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <Controller
                name="currency"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.currency}>
                    <InputLabel>Currency</InputLabel>
                    <Select {...field} label="Currency">
                      <MenuItem value="USD">USD</MenuItem>
                      <MenuItem value="EUR">EUR</MenuItem>
                      <MenuItem value="GBP">GBP</MenuItem>
                      <MenuItem value="INR">INR</MenuItem>
                      <MenuItem value="JPY">JPY</MenuItem>
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>

            {/* Payment Method */}
            <Grid item xs={12}>
              <Controller
                name="method"
                control={control}
                render={({ field }) => (
                  <FormControl fullWidth error={!!errors.method}>
                    <InputLabel>Payment Method</InputLabel>
                    <Select {...field} label="Payment Method">
                      {Object.values(PaymentMethod).map((method) => (
                        <MenuItem key={method} value={method}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getPaymentMethodIcon(method)}
                            <span>{method.replace('_', ' ').toUpperCase()}</span>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}
              />
            </Grid>

            {/* Customer ID */}
            <Grid item xs={12}>
              <Controller
                name="customer_id"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Customer ID"
                    fullWidth
                    error={!!errors.customer_id}
                    helperText={errors.customer_id?.message}
                    placeholder="Enter customer identifier"
                  />
                )}
              />
            </Grid>

            {/* Description */}
            <Grid item xs={12}>
              <Controller
                name="description"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="Description (Optional)"
                    fullWidth
                    multiline
                    rows={2}
                    error={!!errors.description}
                    helperText={errors.description?.message}
                    placeholder="Enter payment description"
                  />
                )}
              />
            </Grid>

            {/* Error Alert */}
            {submitError && (
              <Grid item xs={12}>
                <Alert severity="error" onClose={() => setSubmitError(null)}>
                  {submitError}
                </Alert>
              </Grid>
            )}

            {/* Submit Button */}
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ mt: 2 }}
                startIcon={loading ? <CircularProgress size={20} /> : <PaymentIcon />}
              >
                {loading ? 'Creating Payment...' : 'Create Payment'}
              </Button>
            </Grid>
          </Grid>
        </form>

        {/* Payment Methods Info */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Supported Payment Methods:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {Object.values(PaymentMethod).map((method) => (
              <Chip
                key={method}
                icon={getPaymentMethodIcon(method)}
                label={method.replace('_', ' ').toUpperCase()}
                size="small"
                variant="outlined"
              />
            ))}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PaymentForm; 