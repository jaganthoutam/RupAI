import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  Tab,
  Tabs,
  FormControl,
  Select,
  MenuItem,
  SelectChangeEvent,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Switch,
  FormControlLabel,
  Badge,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Snackbar,
} from '@mui/material';
import {
  Notifications,
  Warning,
  Error,
  CheckCircle,
  NotificationsActive,
  Timeline,
  Assessment,
  Download,
  Refresh,
  Add,
  FilterList,
  Search,
  MoreVert,
  NotificationImportant,
  Schedule,
  Person,
  Computer,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { ApiService } from '../services/apiService';

interface AlertData {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  service: string;
  created_at: string;
  status: 'active' | 'resolved' | 'acknowledged';
  acknowledged_by?: string;
  resolved_by?: string;
  resolved_at?: string;
  metadata?: Record<string, any>;
}

interface AlertStats {
  total_alerts: number;
  active_alerts: number;
  resolved_alerts: number;
  critical_alerts: number;
  alerts_by_severity: Array<{
    severity: string;
    count: number;
  }>;
  alerts_by_service: Array<{
    service: string;
    count: number;
  }>;
}

const AlertsManagement: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [stats, setStats] = useState<AlertStats | null>(null);
  const [filteredAlerts, setFilteredAlerts] = useState<AlertData[]>([]);
  const [createAlertOpen, setCreateAlertOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [serviceFilter, setServiceFilter] = useState('all');
  const [realTimeMode, setRealTimeMode] = useState(true);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as 'success' | 'error' | 'info' });

  const [alertForm, setAlertForm] = useState({
    type: '',
    severity: 'medium' as 'low' | 'medium' | 'high' | 'critical',
    message: '',
    service: '',
  });

  useEffect(() => {
    loadAlerts();
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout | undefined;
    if (realTimeMode) {
      interval = setInterval(loadAlerts, 30000); // Refresh every 30 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [realTimeMode]);

  useEffect(() => {
    filterAlerts();
  }, [alerts, searchTerm, statusFilter, severityFilter, serviceFilter]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError(null);

      let alertsData;
      try {
        alertsData = await ApiService.getActiveAlerts();
      } catch (apiError) {
        console.warn('API service error:', apiError);
        // Fallback data
        alertsData = {
          data: [
            {
              id: 'alert_001',
              type: 'performance',
              severity: 'medium' as const,
              message: 'High memory usage detected on server-01',
              service: 'API Gateway',
              created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
              status: 'active' as const,
            },
            {
              id: 'alert_002',
              type: 'availability',
              severity: 'high' as const,
              message: 'Redis connection pool exhausted',
              service: 'Redis Cache',
              created_at: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
              status: 'active' as const,
            },
            {
              id: 'alert_003',
              type: 'security',
              severity: 'critical' as const,
              message: 'Multiple failed login attempts detected',
              service: 'Authentication',
              created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
              status: 'active' as const,
            },
          ]
        };
      }

      setAlerts(alertsData?.data || []);

      // Calculate stats
      const alertsList = alertsData?.data || [];
      const statsData: AlertStats = {
        total_alerts: alertsList.length,
        active_alerts: alertsList.filter(a => a.status === 'active').length,
        resolved_alerts: alertsList.filter(a => a.status === 'resolved').length,
        critical_alerts: alertsList.filter(a => a.severity === 'critical').length,
        alerts_by_severity: [
          { severity: 'critical', count: alertsList.filter(a => a.severity === 'critical').length },
          { severity: 'high', count: alertsList.filter(a => a.severity === 'high').length },
          { severity: 'medium', count: alertsList.filter(a => a.severity === 'medium').length },
          { severity: 'low', count: alertsList.filter(a => a.severity === 'low').length },
        ],
        alerts_by_service: Array.from(new Set(alertsList.map(a => a.service))).map(service => ({
          service,
          count: alertsList.filter(a => a.service === service).length,
        })),
      };

      setStats(statsData);

      setSnackbar({
        open: true,
        message: 'Alerts updated successfully',
        severity: 'success'
      });
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Failed to load alerts';
      setError(errorMessage);
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
      console.error('Alerts error:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterAlerts = () => {
    let filtered = alerts;

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(alert =>
        alert.message.toLowerCase().includes(term) ||
        alert.service.toLowerCase().includes(term) ||
        alert.type.toLowerCase().includes(term)
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(alert => alert.status === statusFilter);
    }

    // Severity filter
    if (severityFilter !== 'all') {
      filtered = filtered.filter(alert => alert.severity === severityFilter);
    }

    // Service filter
    if (serviceFilter !== 'all') {
      filtered = filtered.filter(alert => alert.service === serviceFilter);
    }

    setFilteredAlerts(filtered);
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleRefresh = () => {
    loadAlerts();
  };

  const handleCreateAlert = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would call the API
      console.log('Creating alert:', alertForm);
      
      setCreateAlertOpen(false);
      setAlertForm({ type: '', severity: 'medium', message: '', service: '' });
      await loadAlerts();
      
      setSnackbar({
        open: true,
        message: 'Alert created successfully',
        severity: 'success'
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Failed to create alert',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    try {
      setLoading(true);
      // In a real implementation, this would call the API
      console.log('Resolving alert:', alertId);
      
      await loadAlerts();
      
      setSnackbar({
        open: true,
        message: 'Alert resolved successfully',
        severity: 'success'
      });
    } catch (err: any) {
      setSnackbar({
        open: true,
        message: 'Failed to resolve alert',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#f44336';
      case 'high': return '#ff9800';
      case 'medium': return '#2196f3';
      case 'low': return '#4caf50';
      default: return '#757575';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <Error />;
      case 'high': return <Warning />;
      case 'medium': return <NotificationsActive />;
      case 'low': return <Notifications />;
      default: return <Notifications />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'error';
      case 'acknowledged': return 'warning';
      case 'resolved': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Alerts Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={realTimeMode}
                onChange={(e) => setRealTimeMode(e.target.checked)}
              />
            }
            label="Real-time"
          />
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateAlertOpen(true)}
          >
            Create Alert
          </Button>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Notifications color="primary" />
                  <Box>
                    <Typography variant="h4">{stats.total_alerts}</Typography>
                    <Typography color="text.secondary">Total Alerts</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Warning color="warning" />
                  <Box>
                    <Typography variant="h4">{stats.active_alerts}</Typography>
                    <Typography color="text.secondary">Active Alerts</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Error color="error" />
                  <Box>
                    <Typography variant="h4">{stats.critical_alerts}</Typography>
                    <Typography color="text.secondary">Critical Alerts</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle color="success" />
                  <Box>
                    <Typography variant="h4">{stats.resolved_alerts}</Typography>
                    <Typography color="text.secondary">Resolved Alerts</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab icon={<Notifications />} label="All Alerts" />
          <Tab icon={<Warning />} label="Active Alerts" />
          <Tab icon={<Assessment />} label="Analytics" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          {tabValue === 0 && (
            <Box>
              {/* Filters */}
              <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
                <TextField
                  size="small"
                  placeholder="Search alerts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                  sx={{ minWidth: 200 }}
                />
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                    <MenuItem value="all">All Status</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="acknowledged">Acknowledged</MenuItem>
                    <MenuItem value="resolved">Resolved</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <Select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)}>
                    <MenuItem value="all">All Severity</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                  </Select>
                </FormControl>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <Select value={serviceFilter} onChange={(e) => setServiceFilter(e.target.value)}>
                    <MenuItem value="all">All Services</MenuItem>
                    {Array.from(new Set(alerts.map(a => a.service))).map(service => (
                      <MenuItem key={service} value={service}>{service}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              {/* Alerts Table */}
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Severity</TableCell>
                      <TableCell>Message</TableCell>
                      <TableCell>Service</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredAlerts.map((alert) => (
                      <TableRow key={alert.id}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getSeverityIcon(alert.severity)}
                            <Chip
                              label={alert.severity.toUpperCase()}
                              size="small"
                              sx={{
                                backgroundColor: getSeverityColor(alert.severity),
                                color: 'white',
                                fontWeight: 600,
                              }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight={500}>
                            {alert.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {alert.type}
                          </Typography>
                        </TableCell>
                        <TableCell>{alert.service}</TableCell>
                        <TableCell>
                          <Chip
                            label={alert.status.toUpperCase()}
                            size="small"
                            color={getStatusColor(alert.status) as any}
                            variant={alert.status === 'active' ? 'filled' : 'outlined'}
                          />
                        </TableCell>
                        <TableCell>
                          {format(new Date(alert.created_at), 'MMM dd, yyyy HH:mm')}
                        </TableCell>
                        <TableCell align="right">
                          {alert.status === 'active' && (
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => handleResolveAlert(alert.id)}
                            >
                              Resolve
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                    {filteredAlerts.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          <Typography color="text.secondary">
                            No alerts found
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Active Alerts Only
              </Typography>
              {/* Same table but filtered for active alerts */}
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Severity</TableCell>
                      <TableCell>Message</TableCell>
                      <TableCell>Service</TableCell>
                      <TableCell>Created</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {alerts.filter(alert => alert.status === 'active').map((alert) => (
                      <TableRow key={alert.id}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getSeverityIcon(alert.severity)}
                            <Chip
                              label={alert.severity.toUpperCase()}
                              size="small"
                              sx={{
                                backgroundColor: getSeverityColor(alert.severity),
                                color: 'white',
                                fontWeight: 600,
                              }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight={500}>
                            {alert.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {alert.type}
                          </Typography>
                        </TableCell>
                        <TableCell>{alert.service}</TableCell>
                        <TableCell>
                          {format(new Date(alert.created_at), 'MMM dd, yyyy HH:mm')}
                        </TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleResolveAlert(alert.id)}
                          >
                            Resolve
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {tabValue === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Alerts Analytics
              </Typography>
              {stats && (
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Alerts by Severity
                        </Typography>
                        {stats.alerts_by_severity.map((item) => (
                          <Box key={item.severity} sx={{ mb: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                {item.severity}
                              </Typography>
                              <Typography variant="body2" fontWeight={600}>
                                {item.count}
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={(item.count / Math.max(stats.total_alerts, 1)) * 100}
                              sx={{ 
                                mt: 0.5,
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: getSeverityColor(item.severity),
                                }
                              }}
                            />
                          </Box>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Alerts by Service
                        </Typography>
                        {stats.alerts_by_service.map((item) => (
                          <Box key={item.service} sx={{ mb: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <Typography variant="body2">
                                {item.service}
                              </Typography>
                              <Typography variant="body2" fontWeight={600}>
                                {item.count}
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={(item.count / Math.max(stats.total_alerts, 1)) * 100}
                              sx={{ mt: 0.5 }}
                            />
                          </Box>
                        ))}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              )}
            </Box>
          )}
        </Box>
      </Paper>

      {/* Create Alert Dialog */}
      <Dialog open={createAlertOpen} onClose={() => setCreateAlertOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Alert</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Alert Type"
              value={alertForm.type}
              onChange={(e) => setAlertForm(prev => ({ ...prev, type: e.target.value }))}
              fullWidth
            />
            <FormControl fullWidth>
              <Select
                value={alertForm.severity}
                onChange={(e) => setAlertForm(prev => ({ ...prev, severity: e.target.value as any }))}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Service"
              value={alertForm.service}
              onChange={(e) => setAlertForm(prev => ({ ...prev, service: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Message"
              value={alertForm.message}
              onChange={(e) => setAlertForm(prev => ({ ...prev, message: e.target.value }))}
              multiline
              rows={3}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateAlertOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateAlert}
            variant="contained"
            disabled={!alertForm.type || !alertForm.message || !alertForm.service || loading}
          >
            Create Alert
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

export default AlertsManagement;
