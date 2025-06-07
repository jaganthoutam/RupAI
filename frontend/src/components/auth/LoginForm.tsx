import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
  Chip,
  Avatar,
  Container,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  AdminPanelSettings,
  Security,
} from '@mui/icons-material';
import { LoadingButton } from '@mui/lab';
import { useAuth } from '../../contexts/AuthContext';
import { motion } from 'framer-motion';

interface LoginFormProps {
  onSuccess?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [loginAttempts, setLoginAttempts] = useState(0);

  const handleChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: '',
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!validateForm()) return;

    try {
      const success = await login(formData.email, formData.password);
      
      if (success) {
        // Call onSuccess callback if provided
        onSuccess?.();
        
        // Navigate to dashboard after successful login
        navigate('/', { replace: true });
      } else {
        setLoginAttempts(prev => prev + 1);
      }
    } catch (error) {
      console.error('Login error:', error);
      setLoginAttempts(prev => prev + 1);
    }
  };

  const handleTogglePassword = () => {
    setShowPassword(prev => !prev);
  };

  const demoCredentials = [
    { email: 'admin@payment.com', password: 'admin123456', role: 'Admin' },
    { email: 'operator@payment.com', password: 'operator123', role: 'Operator' },
    { email: 'viewer@payment.com', password: 'viewer123', role: 'Viewer' },
  ];

  const fillDemoCredentials = (creds: { email: string; password: string }) => {
    setFormData(creds);
    setErrors({});
  };

  return (
    <Container maxWidth="sm">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            py: 4,
          }}
        >
          <Card
            sx={{
              width: '100%',
              maxWidth: 480,
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
              borderRadius: 3,
            }}
          >
            <CardContent sx={{ p: 4 }}>
              {/* Header */}
              <Box sx={{ textAlign: 'center', mb: 4 }}>
                <Avatar
                  sx={{
                    mx: 'auto',
                    mb: 2,
                    width: 64,
                    height: 64,
                    bgcolor: 'primary.main',
                  }}
                >
                  <AdminPanelSettings sx={{ fontSize: 32 }} />
                </Avatar>
                <Typography variant="h4" component="h1" gutterBottom>
                  Admin Login
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Enter your credentials to access the payment administration panel
                </Typography>
              </Box>

              {/* Login Attempts Warning */}
              {loginAttempts >= 3 && (
                <Alert severity="warning" sx={{ mb: 3 }}>
                  Multiple failed login attempts detected. Please verify your credentials.
                </Alert>
              )}

              {/* Login Form */}
              <Box component="form" onSubmit={handleSubmit} noValidate>
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={formData.email}
                  onChange={handleChange('email')}
                  error={!!errors.email}
                  helperText={errors.email}
                  margin="normal"
                  required
                  autoComplete="email"
                  autoFocus
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Email color="action" />
                      </InputAdornment>
                    ),
                  }}
                />

                <TextField
                  fullWidth
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleChange('password')}
                  error={!!errors.password}
                  helperText={errors.password}
                  margin="normal"
                  required
                  autoComplete="current-password"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock color="action" />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={handleTogglePassword}
                          edge="end"
                          aria-label="toggle password visibility"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />

                <LoadingButton
                  fullWidth
                  type="submit"
                  variant="contained"
                  loading={isLoading}
                  loadingPosition="start"
                  startIcon={<Security />}
                  sx={{ mt: 3, mb: 2, py: 1.5 }}
                  size="large"
                >
                  Sign In
                </LoadingButton>
              </Box>

              {/* Demo Credentials */}
              <Divider sx={{ my: 3 }}>
                <Chip label="Demo Credentials" size="small" />
              </Divider>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 1 }}>
                  Click to auto-fill demo credentials:
                </Typography>
                {demoCredentials.map((cred, index) => (
                  <Button
                    key={index}
                    variant="outlined"
                    size="small"
                    onClick={() => fillDemoCredentials(cred)}
                    sx={{ textTransform: 'none' }}
                  >
                    {cred.role}: {cred.email}
                  </Button>
                ))}
              </Box>

              {/* Security Notice */}
              <Alert severity="info" sx={{ mt: 3 }}>
                <Typography variant="caption">
                  🔒 This is a secure admin panel. All login attempts are monitored and logged.
                </Typography>
              </Alert>
            </CardContent>
          </Card>
        </Box>
      </motion.div>
    </Container>
  );
};

export default LoginForm; 