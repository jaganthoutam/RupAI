import React, { useState } from 'react';
import {
  Box,
  Grid,
  Tabs,
  Tab,
  Paper,
  Typography,
  Fade,
} from '@mui/material';
import { Payment as PaymentIcon, Add, List } from '@mui/icons-material';
import { Helmet } from 'react-helmet-async';
import PaymentForm from '../components/payment/PaymentForm';
import PaymentList from '../components/payment/PaymentList';
import { Payment } from '../types/payment';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`payment-tabpanel-${index}`}
      aria-labelledby={`payment-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Fade in={true} timeout={300}>
          <Box sx={{ pt: 3 }}>
            {children}
          </Box>
        </Fade>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `payment-tab-${index}`,
    'aria-controls': `payment-tabpanel-${index}`,
  };
}

const Payments: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setSelectedPayment(null);
  };

  const handlePaymentSuccess = (payment: Payment) => {
    // Switch to payments list tab
    setTabValue(1);
    // Trigger refresh of payment list
    setRefreshTrigger(prev => prev + 1);
    setSelectedPayment(payment);
  };

  const handlePaymentSelect = (payment: Payment) => {
    setSelectedPayment(payment);
    // Here you could open a modal or navigate to a detail page
    console.log('Selected payment:', payment);
  };

  return (
    <>
      <Helmet>
        <title>Payments - MCP Payments Dashboard</title>
        <meta name="description" content="Create and manage payments in the MCP payments system" />
      </Helmet>

      <Box sx={{ flexGrow: 1, p: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Payments Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Create new payments and manage existing transactions
          </Typography>
        </Box>

        {/* Main Content */}
        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="payment management tabs"
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab
                icon={<Add />}
                label="Create Payment"
                {...a11yProps(0)}
                sx={{ minHeight: 64 }}
              />
              <Tab
                icon={<List />}
                label="Payment List"
                {...a11yProps(1)}
                sx={{ minHeight: 64 }}
              />
            </Tabs>
          </Box>

          {/* Create Payment Tab */}
          <TabPanel value={tabValue} index={0}>
            <Box sx={{ p: 3 }}>
              <Grid container spacing={3} justifyContent="center">
                <Grid item xs={12} lg={8}>
                  <PaymentForm
                    onSuccess={handlePaymentSuccess}
                    onError={(error) => console.error('Payment error:', error)}
                  />
                </Grid>
              </Grid>
            </Box>
          </TabPanel>

          {/* Payment List Tab */}
          <TabPanel value={tabValue} index={1}>
            <Box sx={{ p: 3 }}>
              <PaymentList
                onPaymentSelect={handlePaymentSelect}
                refreshTrigger={refreshTrigger}
              />
            </Box>
          </TabPanel>
        </Paper>

        {/* Selected Payment Details - Could be expanded into a modal */}
        {selectedPayment && (
          <Paper sx={{ mt: 3, p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Selected Payment Details
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Payment ID
                </Typography>
                <Typography variant="body2" fontFamily="monospace">
                  {selectedPayment.id}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Amount
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {selectedPayment.currency} {selectedPayment.amount}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Status
                </Typography>
                <Typography variant="body2">
                  {selectedPayment.status.toUpperCase()}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Method
                </Typography>
                <Typography variant="body2">
                  {selectedPayment.method.replace('_', ' ').toUpperCase()}
                </Typography>
              </Grid>
              {selectedPayment.description && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Description
                  </Typography>
                  <Typography variant="body2">
                    {selectedPayment.description}
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Paper>
        )}
      </Box>
    </>
  );
};

export default Payments; 