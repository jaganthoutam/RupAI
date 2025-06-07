import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material'
import {
  Subscriptions,
  CheckCircle,
  Cancel,
  Add,
  Star,
  Diamond,
  Whatshot
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import apiService from '../services/apiService'

interface Subscription {
  id: string
  plan_name: string
  status: 'active' | 'cancelled' | 'paused' | 'expired'
  amount: number
  currency: string
  billing_cycle: 'monthly' | 'yearly'
  next_billing_date: string
  created_at: string
}

interface Plan {
  id: string
  name: string
  description: string
  amount: number
  currency: string
  billing_cycle: 'monthly' | 'yearly'
  features: string[]
}

const SubscriptionsPage: React.FC = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [newSubscriptionOpen, setNewSubscriptionOpen] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState('')

  const { user } = useAuth()

  useEffect(() => {
    loadSubscriptionData()
  }, [])

  const loadSubscriptionData = async () => {
    try {
      setLoading(true)
      
      // For now, use mock data since we don't have subscription APIs implemented
      const mockSubscriptions: Subscription[] = [
        {
          id: 'sub_1',
          plan_name: 'Premium Plan',
          status: 'active',
          amount: 29.99,
          currency: 'USD',
          billing_cycle: 'monthly',
          next_billing_date: '2024-08-01',
          created_at: '2024-01-01'
        }
      ]

      const mockPlans: Plan[] = [
        {
          id: 'plan_1',
          name: 'Basic Plan',
          description: 'Perfect for personal use',
          amount: 9.99,
          currency: 'USD',
          billing_cycle: 'monthly',
          features: ['Up to 10 transactions/month', 'Basic support', 'Standard processing']
        },
        {
          id: 'plan_2',
          name: 'Premium Plan',
          description: 'Great for small businesses',
          amount: 29.99,
          currency: 'USD',
          billing_cycle: 'monthly',
          features: ['Unlimited transactions', 'Priority support', 'Advanced analytics', 'API access']
        },
        {
          id: 'plan_3',
          name: 'Enterprise Plan',
          description: 'For large organizations',
          amount: 99.99,
          currency: 'USD',
          billing_cycle: 'monthly',
          features: ['Everything in Premium', 'Dedicated support', 'Custom integrations', 'SLA guarantee']
        }
      ]

      setSubscriptions(mockSubscriptions)
      setPlans(mockPlans)
    } catch (err: any) {
      setError('Failed to load subscription data')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success'
      case 'paused':
        return 'warning'
      case 'cancelled':
      case 'expired':
        return 'error'
      default:
        return 'default'
    }
  }

  const getPlanIcon = (planName: string) => {
    if (planName.toLowerCase().includes('enterprise')) return <Diamond />
    if (planName.toLowerCase().includes('premium')) return <Star />
    return <Whatshot />
  }

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency
    }).format(amount)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Subscriptions
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your subscription plans and billing.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Current Subscriptions */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Your Subscriptions
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setNewSubscriptionOpen(true)}
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              }}
            >
              New Subscription
            </Button>
          </Box>

          {loading ? (
            <CircularProgress />
          ) : subscriptions.length > 0 ? (
            <List>
              {subscriptions.map((subscription) => (
                <ListItem key={subscription.id} sx={{ border: 1, borderColor: 'divider', borderRadius: 2, mb: 2 }}>
                  <ListItemIcon>
                    <Avatar sx={{ bgcolor: 'primary.light' }}>
                      <Subscriptions />
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={2}>
                        <Typography variant="h6">{subscription.plan_name}</Typography>
                        <Chip
                          label={subscription.status}
                          color={getStatusColor(subscription.status) as any}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {formatCurrency(subscription.amount, subscription.currency)} / {subscription.billing_cycle}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Next billing: {new Date(subscription.next_billing_date).toLocaleDateString()}
                        </Typography>
                      </Box>
                    }
                  />
                  <Box display="flex" gap={1}>
                    <Button variant="outlined" size="small">
                      Manage
                    </Button>
                    <Button variant="outlined" color="error" size="small">
                      Cancel
                    </Button>
                  </Box>
                </ListItem>
              ))}
            </List>
          ) : (
            <Alert severity="info">
              You don't have any active subscriptions. Choose a plan below to get started.
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Available Plans */}
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
        Available Plans
      </Typography>

      <Grid container spacing={3}>
        {plans.map((plan) => (
          <Grid item xs={12} md={4} key={plan.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                '&:hover': {
                  boxShadow: 4
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Avatar sx={{ bgcolor: 'primary.light' }}>
                    {getPlanIcon(plan.name)}
                  </Avatar>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {plan.name}
                  </Typography>
                </Box>

                <Typography variant="body2" color="text.secondary" paragraph>
                  {plan.description}
                </Typography>

                <Box mb={3}>
                  <Typography variant="h4" sx={{ fontWeight: 600 }}>
                    {formatCurrency(plan.amount, plan.currency)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    per {plan.billing_cycle.replace('ly', '')}
                  </Typography>
                </Box>

                <List dense>
                  {plan.features.map((feature, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <CheckCircle color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={feature}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>

              <Box p={2}>
                <Button
                  fullWidth
                  variant="contained"
                  onClick={() => {
                    setSelectedPlan(plan.id)
                    setNewSubscriptionOpen(true)
                  }}
                  sx={{
                    background: plan.name.includes('Premium')
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : 'primary.main'
                  }}
                >
                  Subscribe
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* New Subscription Dialog */}
      <Dialog open={newSubscriptionOpen} onClose={() => setNewSubscriptionOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Subscription</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Select Plan</InputLabel>
              <Select
                value={selectedPlan}
                label="Select Plan"
                onChange={(e) => setSelectedPlan(e.target.value)}
              >
                {plans.map((plan) => (
                  <MenuItem key={plan.id} value={plan.id}>
                    {plan.name} - {formatCurrency(plan.amount, plan.currency)}/{plan.billing_cycle}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Alert severity="info">
              Your subscription will be activated immediately and you'll be charged {' '}
              {selectedPlan && plans.find(p => p.id === selectedPlan) && 
                formatCurrency(plans.find(p => p.id === selectedPlan)!.amount, 'USD')
              } today.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewSubscriptionOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={!selectedPlan}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }}
          >
            Subscribe Now
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default SubscriptionsPage 