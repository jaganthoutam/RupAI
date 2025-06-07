import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Paper,
  Avatar,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material'
import {
  ExpandMore,
  HelpOutline,
  Email,
  Phone,
  Chat,
  Description,
  CheckCircle,
  Schedule,
  Support,
  ContactSupport,
  QuestionAnswer
} from '@mui/icons-material'

const SupportPage: React.FC = () => {
  const [ticketForm, setTicketForm] = useState({
    subject: '',
    category: '',
    priority: 'medium',
    description: ''
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')

  const faqData = [
    {
      question: "How do I make a payment?",
      answer: "To make a payment, navigate to the Payments page, select your preferred payment method (card, bank transfer, wallet, or UPI), enter the amount and recipient details, and confirm the transaction. You'll receive a confirmation once the payment is processed."
    },
    {
      question: "What payment methods are supported?",
      answer: "We support multiple payment methods including credit/debit cards (Visa, Mastercard, American Express), bank transfers (ACH), digital wallets (PayPal, Apple Pay, Google Pay), and UPI for Indian customers."
    },
    {
      question: "How long do transactions take to process?",
      answer: "Transaction times vary by payment method: Card payments are usually instant, bank transfers take 1-3 business days, and UPI payments are processed within minutes. You'll receive real-time updates on your transaction status."
    },
    {
      question: "Is my financial information secure?",
      answer: "Yes, we use bank-level security including 256-bit SSL encryption, PCI DSS compliance, and never store your complete card details. All sensitive data is tokenized and encrypted."
    },
    {
      question: "How do I add money to my wallet?",
      answer: "Go to the Wallet page, click 'Add Funds', select your funding source (bank account or card), enter the amount, and confirm. Funds are typically available immediately for card funding or within 1-2 business days for bank transfers."
    },
    {
      question: "What are the transaction fees?",
      answer: "Our fees vary by payment method: Card payments have a 2.9% + $0.30 fee, bank transfers are $1.00 per transaction, and wallet-to-wallet transfers are free. Check our pricing page for the most current rates."
    },
    {
      question: "How do I dispute a transaction?",
      answer: "If you need to dispute a transaction, contact our support team immediately with your transaction ID and reason for dispute. We'll investigate and respond within 2-3 business days."
    },
    {
      question: "Can I cancel a payment?",
      answer: "Payments can only be cancelled if they haven't been processed yet. For instant payments (cards, UPI), cancellation may not be possible. For bank transfers, you may be able to cancel within a short window."
    }
  ]

  const handleTicketSubmit = async () => {
    setLoading(true)
    
    // Simulate ticket submission
    setTimeout(() => {
      setSuccess('Support ticket submitted successfully! We\'ll get back to you within 24 hours.')
      setTicketForm({
        subject: '',
        category: '',
        priority: 'medium',
        description: ''
      })
      setLoading(false)
    }, 1000)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Support Center
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Get help with your account, payments, and technical issues.
      </Typography>

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Contact Methods */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Contact Us
              </Typography>
              
              <List>
                <ListItem>
                  <ListItemIcon>
                    <Email color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Email Support"
                    secondary="support@mcppayments.com"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <Phone color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Phone Support"
                    secondary="+1 (555) 123-4567"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <Chat color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Live Chat"
                    secondary="24/7 available"
                  />
                </ListItem>
              </List>

              <Button
                fullWidth
                variant="contained"
                startIcon={<Chat />}
                sx={{
                  mt: 2,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                }}
              >
                Start Live Chat
              </Button>
            </CardContent>
          </Card>

          {/* Support Hours */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Support Hours
              </Typography>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Schedule color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Email & Chat"
                    secondary="24/7 Available"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Phone color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Phone Support"
                    secondary="Mon-Fri: 9AM-6PM EST"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Support Ticket Form */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <Avatar sx={{ bgcolor: 'primary.light' }}>
                  <ContactSupport />
                </Avatar>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Submit a Support Ticket
                </Typography>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Subject"
                    value={ticketForm.subject}
                    onChange={(e) => setTicketForm({ ...ticketForm, subject: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={ticketForm.category}
                      label="Category"
                      onChange={(e) => setTicketForm({ ...ticketForm, category: e.target.value })}
                    >
                      <MenuItem value="payment">Payment Issues</MenuItem>
                      <MenuItem value="account">Account Problems</MenuItem>
                      <MenuItem value="technical">Technical Support</MenuItem>
                      <MenuItem value="billing">Billing Questions</MenuItem>
                      <MenuItem value="security">Security Concerns</MenuItem>
                      <MenuItem value="other">Other</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Priority</InputLabel>
                    <Select
                      value={ticketForm.priority}
                      label="Priority"
                      onChange={(e) => setTicketForm({ ...ticketForm, priority: e.target.value })}
                    >
                      <MenuItem value="low">Low</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                      <MenuItem value="urgent">Urgent</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip
                      label={ticketForm.priority.toUpperCase()}
                      color={
                        ticketForm.priority === 'urgent' ? 'error' :
                        ticketForm.priority === 'high' ? 'warning' :
                        ticketForm.priority === 'medium' ? 'primary' : 'default'
                      }
                      size="small"
                    />
                    <Typography variant="body2" color="text.secondary">
                      Response time: {
                        ticketForm.priority === 'urgent' ? '2-4 hours' :
                        ticketForm.priority === 'high' ? '4-8 hours' :
                        ticketForm.priority === 'medium' ? '12-24 hours' : '24-48 hours'
                      }
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Description"
                    multiline
                    rows={4}
                    value={ticketForm.description}
                    onChange={(e) => setTicketForm({ ...ticketForm, description: e.target.value })}
                    placeholder="Please provide detailed information about your issue..."
                  />
                </Grid>
              </Grid>

              <Button
                variant="contained"
                onClick={handleTicketSubmit}
                disabled={loading || !ticketForm.subject || !ticketForm.category || !ticketForm.description}
                sx={{
                  mt: 3,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                }}
              >
                {loading ? 'Submitting...' : 'Submit Ticket'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* FAQ Section */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={3}>
            <Avatar sx={{ bgcolor: 'primary.light' }}>
              <QuestionAnswer />
            </Avatar>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Frequently Asked Questions
            </Typography>
          </Box>

          {faqData.map((faq, index) => (
            <Accordion key={index}>
              <AccordionSummary
                expandIcon={<ExpandMore />}
                aria-controls={`faq-content-${index}`}
                id={`faq-header-${index}`}
              >
                <Box display="flex" alignItems="center" gap={2}>
                  <HelpOutline color="primary" fontSize="small" />
                  <Typography variant="subtitle1">{faq.question}</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary">
                  {faq.answer}
                </Typography>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>

      {/* Resource Links */}
      <Grid container spacing={2} sx={{ mt: 2 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center', '&:hover': { boxShadow: 4 } }}>
            <Description sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              User Guide
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Complete guide to using our platform
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center', '&:hover': { boxShadow: 4 } }}>
            <Support sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              API Docs
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Developer documentation and API reference
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center', '&:hover': { boxShadow: 4 } }}>
            <CheckCircle sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              Status Page
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time system status and updates
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center', '&:hover': { boxShadow: 4 } }}>
            <HelpOutline sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              Community
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Join our community forum for tips and discussion
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default SupportPage 