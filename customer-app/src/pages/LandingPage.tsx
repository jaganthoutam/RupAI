import React from 'react'
import { 
  Box, 
  Container, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  Avatar,
  Chip,
  Paper,
  LinearProgress
} from '@mui/material'
import { 
  Payment, 
  Security, 
  Speed, 
  Analytics, 
  Wallet, 
  Support,
  Star,
  TrendingUp,
  Shield,
  Psychology,
  AttachMoney,
  CreditCard
} from '@mui/icons-material'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'

const LandingPage: React.FC = () => {
  const navigate = useNavigate()

  const features = [
    {
      icon: <Psychology color="primary" />,
      title: "AI-Powered Optimization",
      description: "Smart payment routing with 98.5% success rate using machine learning algorithms",
      value: "98.5%",
      metric: "Success Rate"
    },
    {
      icon: <Shield color="primary" />,
      title: "Advanced Fraud Detection",
      description: "Real-time fraud prevention with AI pattern recognition and risk scoring",
      value: "99.9%",
      metric: "Fraud Prevention"
    },
    {
      icon: <Speed color="primary" />,
      title: "Lightning Fast Processing",
      description: "Sub-second payment processing with intelligent provider selection",
      value: "<150ms",
      metric: "Processing Time"
    },
    {
      icon: <AttachMoney color="primary" />,
      title: "Cost Optimization",
      description: "Dynamic routing to minimize transaction fees and maximize savings",
      value: "35%",
      metric: "Cost Reduction"
    },
    {
      icon: <Analytics color="primary" />,
      title: "Real-time Analytics",
      description: "Comprehensive insights and reporting with AI-driven recommendations",
      value: "24/7",
      metric: "Monitoring"
    },
    {
      icon: <Support color="primary" />,
      title: "AI Assistant Support",
      description: "Intelligent chat support with MCP protocol integration",
      value: "Instant",
      metric: "Response Time"
    }
  ]

  const stats = [
    { label: "Payments Processed", value: "$2.3B+", growth: "+125%" },
    { label: "Active Users", value: "250K+", growth: "+89%" },
    { label: "Countries Supported", value: "45+", growth: "+67%" },
    { label: "Uptime", value: "99.99%", growth: "Consistent" }
  ]

  const paymentMethods = [
    { name: "Credit Cards", logo: <CreditCard />, supported: true },
    { name: "Bank Transfers", logo: <Payment />, supported: true },
    { name: "Digital Wallets", logo: <Wallet />, supported: true },
    { name: "UPI (India)", logo: <Payment />, supported: true },
    { name: "Cryptocurrencies", logo: <AttachMoney />, supported: true },
    { name: "Buy Now Pay Later", logo: <CreditCard />, supported: true }
  ]

  return (
    <Box sx={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ pt: 8, pb: 6 }}>
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <Box textAlign="center" color="white" mb={6}>
            <Typography variant="h1" component="h1" gutterBottom sx={{ fontWeight: 700, fontSize: { xs: '2.5rem', md: '3.5rem' } }}>
              MCP Payments Enterprise
            </Typography>
            <Typography variant="h5" component="h2" gutterBottom sx={{ opacity: 0.9, mb: 4 }}>
              The Future of Intelligent Payment Processing
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.8, maxWidth: '800px', mx: 'auto', mb: 6, lineHeight: 1.6 }}>
              Experience next-generation payment infrastructure powered by AI, with enterprise-grade security, 
              fraud detection, and optimization that adapts to your business needs in real-time.
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Button 
                variant="contained" 
                size="large" 
                sx={{ 
                  bgcolor: 'white', 
                  color: 'primary.main', 
                  px: 4, 
                  py: 1.5,
                  fontWeight: 600,
                  '&:hover': { bgcolor: 'grey.100' }
                }}
                onClick={() => navigate('/auth')}
              >
                Start Free Trial
              </Button>
              <Button 
                variant="outlined" 
                size="large" 
                sx={{ 
                  borderColor: 'white', 
                  color: 'white', 
                  px: 4, 
                  py: 1.5,
                  fontWeight: 600,
                  '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' }
                }}
                onClick={() => navigate('/auth')}
              >
                See Demo
              </Button>
            </Box>
          </Box>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          <Grid container spacing={4} sx={{ mb: 8 }}>
            {stats.map((stat, index) => (
              <Grid item xs={6} md={3} key={index}>
                <Paper 
                  sx={{ 
                    p: 3, 
                    textAlign: 'center', 
                    background: 'rgba(255,255,255,0.1)', 
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    color: 'white'
                  }}
                >
                  <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8, mb: 1 }}>
                    {stat.label}
                  </Typography>
                  <Chip 
                    label={stat.growth} 
                    size="small" 
                    sx={{ 
                      bgcolor: 'rgba(76, 175, 80, 0.2)', 
                      color: '#4caf50',
                      fontWeight: 600
                    }} 
                    icon={<TrendingUp sx={{ fontSize: '16px !important' }} />}
                  />
                </Paper>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Container>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <Typography 
            variant="h2" 
            component="h2" 
            textAlign="center" 
            color="white" 
            gutterBottom 
            sx={{ fontWeight: 600, mb: 6 }}
          >
            Intelligent Payment Features
          </Typography>
          
          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} lg={4} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Card 
                    sx={{ 
                      height: '100%', 
                      background: 'rgba(255,255,255,0.95)', 
                      backdropFilter: 'blur(10px)',
                      transition: 'transform 0.3s ease-in-out',
                      '&:hover': { 
                        transform: 'translateY(-8px)',
                        boxShadow: '0 20px 40px rgba(0,0,0,0.1)'
                      }
                    }}
                  >
                    <CardContent sx={{ p: 4 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                        <Avatar sx={{ bgcolor: 'primary.light', mr: 2, width: 56, height: 56 }}>
                          {feature.icon}
                        </Avatar>
                        <Box>
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {feature.title}
                          </Typography>
                          <Chip 
                            label={`${feature.value} ${feature.metric}`} 
                            size="small" 
                            color="primary" 
                            sx={{ mt: 0.5 }}
                          />
                        </Box>
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                        {feature.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Container>

      {/* Payment Methods */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <Typography 
            variant="h2" 
            component="h2" 
            textAlign="center" 
            color="white" 
            gutterBottom 
            sx={{ fontWeight: 600, mb: 6 }}
          >
            Universal Payment Support
          </Typography>
          
          <Grid container spacing={3}>
            {paymentMethods.map((method, index) => (
              <Grid item xs={6} md={4} lg={2} key={index}>
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Paper 
                    sx={{ 
                      p: 3, 
                      textAlign: 'center', 
                      background: 'rgba(255,255,255,0.9)',
                      transition: 'all 0.3s ease-in-out',
                      '&:hover': { 
                        background: 'rgba(255,255,255,1)',
                        transform: 'scale(1.05)'
                      }
                    }}
                  >
                    <Avatar sx={{ bgcolor: 'primary.light', mx: 'auto', mb: 2, width: 48, height: 48 }}>
                      {method.logo}
                    </Avatar>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                      {method.name}
                    </Typography>
                    <Chip 
                      label="Supported" 
                      size="small" 
                      color="success"
                      icon={<Star sx={{ fontSize: '14px !important' }} />}
                    />
                  </Paper>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>
      </Container>

      {/* CTA Section */}
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
        >
          <Paper 
            sx={{ 
              p: 6, 
              background: 'rgba(255,255,255,0.95)', 
              backdropFilter: 'blur(10px)',
              borderRadius: 3
            }}
          >
            <Typography variant="h3" component="h2" gutterBottom sx={{ fontWeight: 600 }}>
              Ready to Transform Your Payments?
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 4, lineHeight: 1.6 }}>
              Join thousands of businesses using MCP Payments for intelligent, 
              secure, and optimized payment processing.
            </Typography>
            
            <Box sx={{ mb: 4 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Implementation Progress
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={100} 
                sx={{ 
                  height: 8, 
                  borderRadius: 4,
                  bgcolor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    bgcolor: 'success.main'
                  }
                }} 
              />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                100% Complete - All Features Ready
              </Typography>
            </Box>

            <Button 
              variant="contained" 
              size="large" 
              sx={{ 
                px: 6, 
                py: 2, 
                fontSize: '1.1rem',
                fontWeight: 600
              }}
              onClick={() => navigate('/auth')}
            >
              Start Your Journey
            </Button>
          </Paper>
        </motion.div>
      </Container>
    </Box>
  )
}

export default LandingPage 