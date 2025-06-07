import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Paper,
  Tab,
  Tabs,
  FormControl,
  FormLabel,
  FormGroup,
  FormControlLabel,
  Switch,
  TextField,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar,
  Chip,
  Select,
  MenuItem,
  LinearProgress,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Security,
  Notifications,
  VpnKey,
  Save,
  Refresh,
  Add,
  Delete,
  Edit,
  Visibility,
  VisibilityOff,
  Person,
  Business,
  Storage,
  Lock,
  NotificationsActive,
  Email,
  Sms,
} from '@mui/icons-material';
import { ApiService } from '../services/apiService';

interface SystemSettings {
  maintenance_mode: boolean;
  max_concurrent_requests: number;
  session_timeout: number;
  password_policy: {
    min_length: number;
    require_uppercase: boolean;
    require_lowercase: boolean;
    require_numbers: boolean;
    require_symbols: boolean;
  };
  rate_limiting: {
    enabled: boolean;
    requests_per_minute: number;
  };
  audit_retention_days: number;
  backup_enabled: boolean;
  backup_schedule: string;
}

interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  date_format: string;
  notifications: {
    email: boolean;
    sms: boolean;
    push: boolean;
    digest: boolean;
  };
  dashboard: {
    refresh_interval: number;
    default_view: string;
    charts_animation: boolean;
  };
}

interface ApiKey {
  id: string;
  name: string;
  key: string;
  service: string;
  created_at: string;
  last_used: string;
  status: 'active' | 'inactive' | 'revoked';
  expires_at?: string;
}

interface NotificationSettings {
  email_notifications: boolean;
  sms_notifications: boolean;
  webhook_notifications: boolean;
  alert_channels: string[];
  escalation_rules: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  notification_templates: {
    payment_success: boolean;
    payment_failure: boolean;
    fraud_detected: boolean;
    system_alert: boolean;
  };
}

const Settings: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as 'success' | 'error' | 'info' });

  // Settings states
  const [systemSettings, setSystemSettings] = useState<SystemSettings>({
    maintenance_mode: false,
    max_concurrent_requests: 1000,
    session_timeout: 3600,
    password_policy: {
      min_length: 8,
      require_uppercase: true,
      require_lowercase: true,
      require_numbers: true,
      require_symbols: false,
    },
    rate_limiting: {
      enabled: true,
      requests_per_minute: 60,
    },
    audit_retention_days: 365,
    backup_enabled: true,
    backup_schedule: 'daily',
  });

  const [userPreferences, setUserPreferences] = useState<UserPreferences>({
    theme: 'light',
    language: 'en',
    timezone: 'UTC',
    date_format: 'MM/dd/yyyy',
    notifications: {
      email: true,
      sms: false,
      push: true,
      digest: true,
    },
    dashboard: {
      refresh_interval: 30000,
      default_view: 'dashboard',
      charts_animation: true,
    },
  });

  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    {
      id: 'key_001',
      name: 'Stripe API Key',
      key: 'sk_test_***************',
      service: 'Stripe',
      created_at: '2024-01-01T00:00:00Z',
      last_used: '2024-01-15T10:30:00Z',
      status: 'active',
    },
    {
      id: 'key_002',
      name: 'Razorpay API Key',
      key: 'rzp_test_***************',
      service: 'Razorpay',
      created_at: '2024-01-05T00:00:00Z',
      last_used: '2024-01-14T15:45:00Z',
      status: 'active',
    },
  ]);

  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>({
    email_notifications: true,
    sms_notifications: false,
    webhook_notifications: true,
    alert_channels: ['email', 'webhook'],
    escalation_rules: {
      low: 30,
      medium: 15,
      high: 5,
      critical: 1,
    },
    notification_templates: {
      payment_success: true,
      payment_failure: true,
      fraud_detected: true,
      system_alert: true,
    },
  });

  // Dialog states
  const [apiKeyDialogOpen, setApiKeyDialogOpen] = useState(false);
  const [showApiKey, setShowApiKey] = useState<string | null>(null);
  const [newApiKey, setNewApiKey] = useState({
    name: '',
    service: '',
    key: '',
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError(null);

      // In a real implementation, these would be separate API calls
      // For now, we'll use the current state as default values
      
      setSnackbar({
        open: true,
        message: 'Settings loaded successfully',
        severity: 'success'
      });
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to load settings';
      setError(errorMessage);
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
      console.error('Settings error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSaveSystemSettings = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would call the API
      console.log('Saving system settings:', systemSettings);
      
      setSnackbar({
        open: true,
        message: 'System settings saved successfully',
        severity: 'success'
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Failed to save system settings',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveUserPreferences = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would call the API
      console.log('Saving user preferences:', userPreferences);
      
      setSnackbar({
        open: true,
        message: 'User preferences saved successfully',
        severity: 'success'
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Failed to save user preferences',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveNotificationSettings = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would call the API
      console.log('Saving notification settings:', notificationSettings);
      
      setSnackbar({
        open: true,
        message: 'Notification settings saved successfully',
        severity: 'success'
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Failed to save notification settings',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApiKey = async () => {
    try {
      setLoading(true);
      
      const newKey: ApiKey = {
        id: `key_${Date.now()}`,
        name: newApiKey.name,
        key: newApiKey.key || `${newApiKey.service.toLowerCase()}_${Math.random().toString(36).substr(2, 20)}`,
        service: newApiKey.service,
        created_at: new Date().toISOString(),
        last_used: 'Never',
        status: 'active',
      };

      setApiKeys(prev => [...prev, newKey]);
      setApiKeyDialogOpen(false);
      setNewApiKey({ name: '', service: '', key: '' });
      
      setSnackbar({
        open: true,
        message: 'API key created successfully',
        severity: 'success'
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Failed to create API key',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteApiKey = async (keyId: string) => {
    try {
      setLoading(true);
      setApiKeys(prev => prev.filter(key => key.id !== keyId));
      
      setSnackbar({
        open: true,
        message: 'API key deleted successfully',
        severity: 'success'
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Failed to delete API key',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'warning';
      case 'revoked': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadSettings}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab icon={<SettingsIcon />} label="System Settings" />
          <Tab icon={<Person />} label="User Preferences" />
          <Tab icon={<VpnKey />} label="API Keys" />
          <Tab icon={<Notifications />} label="Notifications" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {/* System Settings Tab */}
          {tabValue === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                System Configuration
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="General Settings" />
                    <CardContent>
                      <FormGroup>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={systemSettings.maintenance_mode}
                              onChange={(e) => setSystemSettings(prev => ({
                                ...prev,
                                maintenance_mode: e.target.checked
                              }))}
                            />
                          }
                          label="Maintenance Mode"
                        />
                        <Box sx={{ mt: 2 }}>
                          <TextField
                            label="Max Concurrent Requests"
                            type="number"
                            value={systemSettings.max_concurrent_requests}
                            onChange={(e) => setSystemSettings(prev => ({
                              ...prev,
                              max_concurrent_requests: parseInt(e.target.value)
                            }))}
                            fullWidth
                            size="small"
                          />
                        </Box>
                        <Box sx={{ mt: 2 }}>
                          <TextField
                            label="Session Timeout (seconds)"
                            type="number"
                            value={systemSettings.session_timeout}
                            onChange={(e) => setSystemSettings(prev => ({
                              ...prev,
                              session_timeout: parseInt(e.target.value)
                            }))}
                            fullWidth
                            size="small"
                          />
                        </Box>
                      </FormGroup>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Security Settings" />
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        Password Policy
                      </Typography>
                      <FormGroup>
                        <TextField
                          label="Minimum Length"
                          type="number"
                          value={systemSettings.password_policy.min_length}
                          onChange={(e) => setSystemSettings(prev => ({
                            ...prev,
                            password_policy: {
                              ...prev.password_policy,
                              min_length: parseInt(e.target.value)
                            }
                          }))}
                          size="small"
                          sx={{ mb: 1 }}
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={systemSettings.password_policy.require_uppercase}
                              onChange={(e) => setSystemSettings(prev => ({
                                ...prev,
                                password_policy: {
                                  ...prev.password_policy,
                                  require_uppercase: e.target.checked
                                }
                              }))}
                            />
                          }
                          label="Require Uppercase"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={systemSettings.password_policy.require_lowercase}
                              onChange={(e) => setSystemSettings(prev => ({
                                ...prev,
                                password_policy: {
                                  ...prev.password_policy,
                                  require_lowercase: e.target.checked
                                }
                              }))}
                            />
                          }
                          label="Require Lowercase"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={systemSettings.password_policy.require_numbers}
                              onChange={(e) => setSystemSettings(prev => ({
                                ...prev,
                                password_policy: {
                                  ...prev.password_policy,
                                  require_numbers: e.target.checked
                                }
                              }))}
                            />
                          }
                          label="Require Numbers"
                        />
                      </FormGroup>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<Save />}
                      onClick={handleSaveSystemSettings}
                      disabled={loading}
                    >
                      Save System Settings
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* User Preferences Tab */}
          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                User Preferences
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Display Settings" />
                    <CardContent>
                      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                        <FormLabel>Theme</FormLabel>
                        <Select
                          value={userPreferences.theme}
                          onChange={(e) => setUserPreferences(prev => ({
                            ...prev,
                            theme: e.target.value as any
                          }))}
                        >
                          <MenuItem value="light">Light</MenuItem>
                          <MenuItem value="dark">Dark</MenuItem>
                          <MenuItem value="auto">Auto</MenuItem>
                        </Select>
                      </FormControl>

                      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                        <FormLabel>Language</FormLabel>
                        <Select
                          value={userPreferences.language}
                          onChange={(e) => setUserPreferences(prev => ({
                            ...prev,
                            language: e.target.value
                          }))}
                        >
                          <MenuItem value="en">English</MenuItem>
                          <MenuItem value="es">Spanish</MenuItem>
                          <MenuItem value="fr">French</MenuItem>
                          <MenuItem value="de">German</MenuItem>
                        </Select>
                      </FormControl>

                      <TextField
                        label="Timezone"
                        value={userPreferences.timezone}
                        onChange={(e) => setUserPreferences(prev => ({
                          ...prev,
                          timezone: e.target.value
                        }))}
                        fullWidth
                        size="small"
                      />
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Dashboard Settings" />
                    <CardContent>
                      <TextField
                        label="Refresh Interval (ms)"
                        type="number"
                        value={userPreferences.dashboard.refresh_interval}
                        onChange={(e) => setUserPreferences(prev => ({
                          ...prev,
                          dashboard: {
                            ...prev.dashboard,
                            refresh_interval: parseInt(e.target.value)
                          }
                        }))}
                        fullWidth
                        size="small"
                        sx={{ mb: 2 }}
                      />

                      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                        <FormLabel>Default View</FormLabel>
                        <Select
                          value={userPreferences.dashboard.default_view}
                          onChange={(e) => setUserPreferences(prev => ({
                            ...prev,
                            dashboard: {
                              ...prev.dashboard,
                              default_view: e.target.value
                            }
                          }))}
                        >
                          <MenuItem value="dashboard">Dashboard</MenuItem>
                          <MenuItem value="payments">Payments</MenuItem>
                          <MenuItem value="analytics">Analytics</MenuItem>
                          <MenuItem value="monitoring">Monitoring</MenuItem>
                        </Select>
                      </FormControl>

                      <FormControlLabel
                        control={
                          <Switch
                            checked={userPreferences.dashboard.charts_animation}
                            onChange={(e) => setUserPreferences(prev => ({
                              ...prev,
                              dashboard: {
                                ...prev.dashboard,
                                charts_animation: e.target.checked
                              }
                            }))}
                          />
                        }
                        label="Enable Chart Animations"
                      />
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<Save />}
                      onClick={handleSaveUserPreferences}
                      disabled={loading}
                    >
                      Save Preferences
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* API Keys Tab */}
          {tabValue === 2 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  API Key Management
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setApiKeyDialogOpen(true)}
                >
                  Add API Key
                </Button>
              </Box>

              <List>
                {apiKeys.map((apiKey) => (
                  <ListItem key={apiKey.id} divider>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1">{apiKey.name}</Typography>
                          <Chip
                            label={apiKey.status.toUpperCase()}
                            size="small"
                            color={getStatusColor(apiKey.status) as any}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Service: {apiKey.service}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Key: {showApiKey === apiKey.id ? apiKey.key : '***************'}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Last used: {apiKey.last_used}
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        size="small"
                        onClick={() => setShowApiKey(showApiKey === apiKey.id ? null : apiKey.id)}
                      >
                        {showApiKey === apiKey.id ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteApiKey(apiKey.id)}
                      >
                        <Delete />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Notifications Tab */}
          {tabValue === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Notification Settings
      </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Notification Channels" />
                    <CardContent>
                      <FormGroup>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={notificationSettings.email_notifications}
                              onChange={(e) => setNotificationSettings(prev => ({
                                ...prev,
                                email_notifications: e.target.checked
                              }))}
                            />
                          }
                          label="Email Notifications"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={notificationSettings.sms_notifications}
                              onChange={(e) => setNotificationSettings(prev => ({
                                ...prev,
                                sms_notifications: e.target.checked
                              }))}
                            />
                          }
                          label="SMS Notifications"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={notificationSettings.webhook_notifications}
                              onChange={(e) => setNotificationSettings(prev => ({
                                ...prev,
                                webhook_notifications: e.target.checked
                              }))}
                            />
                          }
                          label="Webhook Notifications"
                        />
                      </FormGroup>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card>
                    <CardHeader title="Alert Templates" />
                    <CardContent>
                      <FormGroup>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={notificationSettings.notification_templates.payment_success}
                              onChange={(e) => setNotificationSettings(prev => ({
                                ...prev,
                                notification_templates: {
                                  ...prev.notification_templates,
                                  payment_success: e.target.checked
                                }
                              }))}
                            />
                          }
                          label="Payment Success"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={notificationSettings.notification_templates.payment_failure}
                              onChange={(e) => setNotificationSettings(prev => ({
                                ...prev,
                                notification_templates: {
                                  ...prev.notification_templates,
                                  payment_failure: e.target.checked
                                }
                              }))}
                            />
                          }
                          label="Payment Failure"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={notificationSettings.notification_templates.fraud_detected}
                              onChange={(e) => setNotificationSettings(prev => ({
                                ...prev,
                                notification_templates: {
                                  ...prev.notification_templates,
                                  fraud_detected: e.target.checked
                                }
                              }))}
                            />
                          }
                          label="Fraud Detected"
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={notificationSettings.notification_templates.system_alert}
                              onChange={(e) => setNotificationSettings(prev => ({
                                ...prev,
                                notification_templates: {
                                  ...prev.notification_templates,
                                  system_alert: e.target.checked
                                }
                              }))}
                            />
                          }
                          label="System Alerts"
                        />
                      </FormGroup>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12}>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<Save />}
                      onClick={handleSaveNotificationSettings}
                      disabled={loading}
                    >
                      Save Notification Settings
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          )}
        </Box>
      </Paper>

      {/* API Key Creation Dialog */}
      <Dialog open={apiKeyDialogOpen} onClose={() => setApiKeyDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New API Key</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Key Name"
              value={newApiKey.name}
              onChange={(e) => setNewApiKey(prev => ({ ...prev, name: e.target.value }))}
              fullWidth
            />
            <FormControl fullWidth>
              <FormLabel>Service</FormLabel>
              <Select
                value={newApiKey.service}
                onChange={(e) => setNewApiKey(prev => ({ ...prev, service: e.target.value }))}
              >
                <MenuItem value="Stripe">Stripe</MenuItem>
                <MenuItem value="Razorpay">Razorpay</MenuItem>
                <MenuItem value="PayPal">PayPal</MenuItem>
                <MenuItem value="Square">Square</MenuItem>
                <MenuItem value="Custom">Custom</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="API Key (optional - auto-generated if empty)"
              value={newApiKey.key}
              onChange={(e) => setNewApiKey(prev => ({ ...prev, key: e.target.value }))}
              fullWidth
              multiline
              rows={2}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApiKeyDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateApiKey}
            variant="contained"
            disabled={!newApiKey.name || !newApiKey.service || loading}
          >
            Create API Key
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings;
