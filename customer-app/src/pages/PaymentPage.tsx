import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  RadioGroup,
  FormControlLabel,
  Radio,
  InputAdornment,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material'
import {
  CreditCard,
  AccountBalanceWallet,
  QrCode2,
  AccountBalance,
  Security,
  CheckCircle,
  Payment as PaymentIcon,
  Person,
  Email,
  Phone
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import { usePayment } from '../contexts/PaymentContext'
import apiService from '../services/apiService'
import { useNavigate } from 'react-router-dom'

interface PaymentData {
  amount: string
  currency: string
  recipient: string
  description: string
  method: 'card' | 'wallet' | 'bank' | 'upi'
  cardNumber?: string
  expiryDate?: string
  cvv?: string
  cardHolderName?: string
  accountNumber?: string
  routingNumber?: string
  upiId?: string
}

const steps = ['Payment Details', 'Payment Method', 'Confirmation']
const currencies = ['USD', 'EUR', 'GBP', 'INR', 'CAD', 'AUD']

const PaymentPage: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [paymentData, setPaymentData] = useState<PaymentData>({
    amount: '',
    currency: 'USD',
    recipient: '',
    description: '',
    method: 'card'
  })
  const [paymentId, setPaymentId] = useState('')

  const { user } = useAuth()
  const navigate = useNavigate()

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prevActiveStep) => prevActiveStep + 1)
      setError('')
    }
  }

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1)
    setError('')
  }

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 0:
        if (!paymentData.amount || !paymentData.recipient || !paymentData.description) {
          setError('Please fill in all required fields')
          return false
        }
        if (parseFloat(paymentData.amount) <= 0) {
          setError('Amount must be greater than 0')
          return false
        }
        break
      case 1:
        if (paymentData.method === 'card') {
          if (!paymentData.cardNumber || !paymentData.expiryDate || !paymentData.cvv || !paymentData.cardHolderName) {
            setError('Please fill in all card details')
            return false
          }
        } else if (paymentData.method === 'bank') {
          if (!paymentData.accountNumber || !paymentData.routingNumber) {
            setError('Please fill in bank account details')
            return false
          }
        } else if (paymentData.method === 'upi') {
          if (!paymentData.upiId) {
            setError('Please enter UPI ID')
            return false
          }
        }
        break
    }
    return true
  }

  const handlePayment = async () => {
    setLoading(true)
    setError('')

    try {
      const paymentRequest = {
        amount: parseFloat(paymentData.amount),
        currency: paymentData.currency,
        method: paymentData.method,
        customer_id: user?.id || 'customer_123',
        idempotency_key: `payment_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        metadata: {
          recipient: paymentData.recipient,
          description: paymentData.description
        }
      }

      const response = await apiService.createPayment(paymentRequest)
      setPaymentId(response.payment_id || response.id)
      setSuccess(true)
      setActiveStep(activeStep + 1)
    } catch (err: any) {
      setError(err.message || 'Payment failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const renderPaymentDetails = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Payment Details
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Amount"
            type="number"
            value={paymentData.amount}
            onChange={(e) => setPaymentData({ ...paymentData, amount: e.target.value })}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>
            }}
            required
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Currency</InputLabel>
            <Select
              value={paymentData.currency}
              label="Currency"
              onChange={(e) => setPaymentData({ ...paymentData, currency: e.target.value })}
            >
              {currencies.map((currency) => (
                <MenuItem key={currency} value={currency}>
                  {currency}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Recipient"
            value={paymentData.recipient}
            onChange={(e) => setPaymentData({ ...paymentData, recipient: e.target.value })}
            placeholder="Enter email or phone number"
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Description"
            value={paymentData.description}
            onChange={(e) => setPaymentData({ ...paymentData, description: e.target.value })}
            placeholder="What's this payment for?"
            multiline
            rows={3}
            required
          />
        </Grid>
      </Grid>
    </Box>
  )

  const renderPaymentMethod = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Payment Method
      </Typography>
      
      <FormControl fullWidth sx={{ mb: 3 }}>
        <RadioGroup
          value={paymentData.method}
          onChange={(e) => setPaymentData({ ...paymentData, method: e.target.value as any })}
        >
          <Paper sx={{ p: 2, mb: 2 }}>
            <FormControlLabel
              value="card"
              control={<Radio />}
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <CreditCard color="primary" />
                  <Typography>Credit/Debit Card</Typography>
                </Box>
              }
            />
          </Paper>
          
          <Paper sx={{ p: 2, mb: 2 }}>
            <FormControlLabel
              value="wallet"
              control={<Radio />}
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <AccountBalanceWallet color="primary" />
                  <Typography>Digital Wallet</Typography>
                </Box>
              }
            />
          </Paper>
          
          <Paper sx={{ p: 2, mb: 2 }}>
            <FormControlLabel
              value="bank"
              control={<Radio />}
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <AccountBalance color="primary" />
                  <Typography>Bank Transfer</Typography>
                </Box>
              }
            />
          </Paper>
          
          <Paper sx={{ p: 2, mb: 2 }}>
            <FormControlLabel
              value="upi"
              control={<Radio />}
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  <QrCode2 color="primary" />
                  <Typography>UPI</Typography>
                </Box>
              }
            />
          </Paper>
        </RadioGroup>
      </FormControl>

      {/* Card Details */}
      {paymentData.method === 'card' && (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Card Details
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Card Holder Name"
                value={paymentData.cardHolderName || ''}
                onChange={(e) => setPaymentData({ ...paymentData, cardHolderName: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Card Number"
                value={paymentData.cardNumber || ''}
                onChange={(e) => setPaymentData({ ...paymentData, cardNumber: e.target.value })}
                placeholder="1234 5678 9012 3456"
                required
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Expiry Date"
                value={paymentData.expiryDate || ''}
                onChange={(e) => setPaymentData({ ...paymentData, expiryDate: e.target.value })}
                placeholder="MM/YY"
                required
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="CVV"
                value={paymentData.cvv || ''}
                onChange={(e) => setPaymentData({ ...paymentData, cvv: e.target.value })}
                placeholder="123"
                required
              />
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Bank Details */}
      {paymentData.method === 'bank' && (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Bank Account Details
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Account Number"
                value={paymentData.accountNumber || ''}
                onChange={(e) => setPaymentData({ ...paymentData, accountNumber: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Routing Number"
                value={paymentData.routingNumber || ''}
                onChange={(e) => setPaymentData({ ...paymentData, routingNumber: e.target.value })}
                required
              />
            </Grid>
          </Grid>
        </Box>
      )}

      {/* UPI Details */}
      {paymentData.method === 'upi' && (
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            UPI Details
          </Typography>
          <TextField
            fullWidth
            label="UPI ID"
            value={paymentData.upiId || ''}
            onChange={(e) => setPaymentData({ ...paymentData, upiId: e.target.value })}
            placeholder="yourname@paytm"
            required
          />
        </Box>
      )}
    </Box>
  )

  const renderConfirmation = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Confirm Payment
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <List>
          <ListItem>
            <ListItemIcon>
              <PaymentIcon color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Amount"
              secondary={`${paymentData.currency} ${parseFloat(paymentData.amount).toFixed(2)}`}
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <Person color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Recipient"
              secondary={paymentData.recipient}
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <CreditCard color="primary" />
            </ListItemIcon>
            <ListItemText
              primary="Payment Method"
              secondary={paymentData.method.toUpperCase()}
            />
          </ListItem>
        </List>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="body2" color="text.secondary">
          Description: {paymentData.description}
        </Typography>
      </Paper>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          Please review your payment details carefully. This action cannot be undone.
        </Typography>
      </Alert>
    </Box>
  )

  const renderSuccess = () => (
    <Box textAlign="center">
      <CheckCircle color="success" sx={{ fontSize: 64, mb: 2 }} />
      <Typography variant="h5" gutterBottom>
        Payment Successful!
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Your payment has been processed successfully.
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Payment ID: {paymentId}
      </Typography>
      <Box display="flex" gap={2} justifyContent="center" mt={3}>
        <Button
          variant="contained"
          onClick={() => navigate('/transactions')}
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          }}
        >
          View Transaction
        </Button>
        <Button
          variant="outlined"
          onClick={() => {
            setActiveStep(0)
            setPaymentData({
              amount: '',
              currency: 'USD',
              recipient: '',
              description: '',
              method: 'card'
            })
            setSuccess(false)
            setPaymentId('')
          }}
        >
          Make Another Payment
        </Button>
      </Box>
    </Box>
  )

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Make Payment
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Send money securely to anyone, anywhere in the world.
      </Typography>

      <Card sx={{ maxWidth: 800, mx: 'auto' }}>
        <CardContent sx={{ p: 4 }}>
          {!success && (
            <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {success ? (
            renderSuccess()
          ) : (
            <>
              {activeStep === 0 && renderPaymentDetails()}
              {activeStep === 1 && renderPaymentMethod()}
              {activeStep === 2 && renderConfirmation()}

              <Box display="flex" justifyContent="space-between" mt={4}>
                <Button
                  disabled={activeStep === 0}
                  onClick={handleBack}
                  variant="outlined"
                >
                  Back
                </Button>
                
                {activeStep === steps.length - 1 ? (
                  <Button
                    onClick={handlePayment}
                    disabled={loading}
                    variant="contained"
                    sx={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      minWidth: 120
                    }}
                  >
                    {loading ? (
                      <CircularProgress size={24} color="inherit" />
                    ) : (
                      'Pay Now'
                    )}
                  </Button>
                ) : (
                  <Button
                    onClick={handleNext}
                    variant="contained"
                    sx={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    }}
                  >
                    Next
                  </Button>
                )}
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  )
}

export default PaymentPage 