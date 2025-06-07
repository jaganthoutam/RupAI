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
  TextField,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Divider,
  Alert,
  LinearProgress,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Search,
  FilterList,
  Download,
  Refresh,
  Visibility,
  ExpandMore,
  Security,
  Person,
  Payment,
  Settings,
  Error,
  CheckCircle,
  Warning,
  Info,
  Schedule,
  Computer,
  LocationOn,
} from '@mui/icons-material';
import { mcpService } from '../services/mcpService';
import { ApiService } from '../services/apiService';

interface AuditLog {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  action: string;
  resource: string;
  resourceId: string;
  status: 'success' | 'failure' | 'warning';
  ip: string;
  userAgent: string;
  details: Record<string, any>;
  correlationId?: string;
  sessionId?: string;
  location?: string;
}

interface AuditFilters {
  dateRange: '1h' | '24h' | '7d' | '30d' | 'custom';
  status: 'all' | 'success' | 'failure' | 'warning';
  action: 'all' | 'login' | 'payment' | 'wallet' | 'admin' | 'settings';
  user: string;
  resource: string;
  ip: string;
}

interface AuditStats {
  totalLogs: number;
  successCount: number;
  failureCount: number;
  warningCount: number;
  uniqueUsers: number;
  uniqueIPs: number;
}

const AuditLogs: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [realTimeMode, setRealTimeMode] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [filters, setFilters] = useState<AuditFilters>({
    dateRange: '24h',
    status: 'all',
    action: 'all',
    user: '',
    resource: '',
    ip: '',
  });
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<AuditLog[]>([]);
  const [stats, setStats] = useState<AuditStats>({
    totalLogs: 0,
    successCount: 0,
    failureCount: 0,
    warningCount: 0,
    uniqueUsers: 0,
    uniqueIPs: 0,
  });

  useEffect(() => {
    loadAuditLogs();
  }, [filters]);

  useEffect(() => {
    let interval: NodeJS.Timeout | undefined;
    if (realTimeMode) {
      interval = setInterval(loadAuditLogs, 10000); // Refresh every 10 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [realTimeMode, filters]);

  useEffect(() => {
    filterLogs();
  }, [auditLogs, searchTerm]);

  const loadAuditLogs = async () => {
    setLoading(true);
    try {
      // Call the real API instead of using mock data
      const auditData = await ApiService.getAuditLogs({
        start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
        end_date: new Date(),
        page: 1,
        limit: 100
      });
      
      // Transform API response to match component interface
      const transformedLogs: AuditLog[] = auditData.logs?.map((log: any) => ({
        id: log.id,
        timestamp: log.timestamp,
        userId: log.user_id,
        userName: log.user_id, // API doesn't provide userName, using user_id
        action: log.action,
        resource: log.entity_type,
        resourceId: log.entity_id,
        status: log.result === 'success' ? 'success' : log.result === 'failed' ? 'failure' : 'warning',
        ip: log.ip_address,
        userAgent: log.user_agent,
        location: 'Unknown', // API doesn't provide location
        correlationId: log.id, // Using log id as correlation id
        sessionId: log.id, // Using log id as session id
        details: log.changes || {}
      })) || [];
      
      setAuditLogs(transformedLogs);
      
      // Calculate stats from the logs
      const calculatedStats: AuditStats = {
        totalLogs: transformedLogs.length,
        successCount: transformedLogs.filter(log => log.status === 'success').length,
        failureCount: transformedLogs.filter(log => log.status === 'failure').length,
        warningCount: transformedLogs.filter(log => log.status === 'warning').length,
        uniqueUsers: new Set(transformedLogs.map(log => log.userId)).size,
        uniqueIPs: new Set(transformedLogs.map(log => log.ip)).size,
      };
      
      setStats(calculatedStats);
    } catch (error) {
      console.error('Error loading audit logs:', error);
      // Fallback to empty data on error
      setAuditLogs([]);
      setStats({
        totalLogs: 0,
        successCount: 0,
        failureCount: 0,
        warningCount: 0,
        uniqueUsers: 0,
        uniqueIPs: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const filterLogs = () => {
    let filtered = auditLogs;

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(log =>
        log.userName.toLowerCase().includes(term) ||
        log.action.toLowerCase().includes(term) ||
        log.resource.toLowerCase().includes(term) ||
        log.ip.includes(term) ||
        log.correlationId?.toLowerCase().includes(term) ||
        JSON.stringify(log.details).toLowerCase().includes(term)
      );
    }

    // Status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(log => log.status === filters.status);
    }

    // Action filter
    if (filters.action !== 'all') {
      filtered = filtered.filter(log => log.action.startsWith(filters.action));
    }

    // User filter
    if (filters.user) {
      filtered = filtered.filter(log =>
        log.userName.toLowerCase().includes(filters.user.toLowerCase())
      );
    }

    // Resource filter
    if (filters.resource) {
      filtered = filtered.filter(log =>
        log.resource.toLowerCase().includes(filters.resource.toLowerCase())
      );
    }

    // IP filter
    if (filters.ip) {
      filtered = filtered.filter(log => log.ip.includes(filters.ip));
    }

    setFilteredLogs(filtered);
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleFilterChange = (field: keyof AuditFilters, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleLogClick = (log: AuditLog) => {
    setSelectedLog(log);
    setDetailsOpen(true);
  };

  const handleRefresh = () => {
    loadAuditLogs();
  };

  const handleExport = () => {
    console.log('Exporting audit logs...');
    // Implementation for exporting logs
  };

  const clearFilters = () => {
    setFilters({
      dateRange: '24h',
      status: 'all',
      action: 'all',
      user: '',
      resource: '',
      ip: '',
    });
    setSearchTerm('');
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'failure': return <Error sx={{ color: 'error.main' }} />;
      case 'warning': return <Warning sx={{ color: 'warning.main' }} />;
      default: return <Info sx={{ color: 'info.main' }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'success';
      case 'failure': return 'error';
      case 'warning': return 'warning';
      default: return 'info';
    }
  };

  const getActionIcon = (action: string) => {
    if (action.startsWith('auth')) return <Security />;
    if (action.startsWith('payment')) return <Payment />;
    if (action.startsWith('wallet')) return <Person />;
    if (action.startsWith('admin')) return <Settings />;
    return <Info />;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
      <Typography variant="h4" gutterBottom>
        Audit Logs
      </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={realTimeMode}
                onChange={(e) => setRealTimeMode(e.target.checked)}
                color="primary"
              />
            }
            label="Real-time"
          />
          <Tooltip title="Refresh logs">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export logs">
            <IconButton onClick={handleExport}>
              <Download />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Real-time Alert */}
      {realTimeMode && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Real-time monitoring is active. Logs refresh automatically every 10 seconds.
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="primary">
                {stats.totalLogs.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Logs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="success.main">
                {stats.successCount.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Success
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="error.main">
                {stats.failureCount.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Failures
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography variant="h6" color="warning.main">
                {stats.warningCount.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Warnings
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography variant="h6">
                {stats.uniqueUsers.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Unique Users
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Typography variant="h6">
                {stats.uniqueIPs.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Unique IPs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <Select
                  value={filters.dateRange}
                  onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                >
                  <MenuItem value="1h">Last hour</MenuItem>
                  <MenuItem value="24h">Last 24 hours</MenuItem>
                  <MenuItem value="7d">Last 7 days</MenuItem>
                  <MenuItem value="30d">Last 30 days</MenuItem>
                  <MenuItem value="custom">Custom range</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <Select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="success">Success</MenuItem>
                  <MenuItem value="failure">Failure</MenuItem>
                  <MenuItem value="warning">Warning</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <Select
                  value={filters.action}
                  onChange={(e) => handleFilterChange('action', e.target.value)}
                >
                  <MenuItem value="all">All Actions</MenuItem>
                  <MenuItem value="auth">Authentication</MenuItem>
                  <MenuItem value="payment">Payments</MenuItem>
                  <MenuItem value="wallet">Wallet</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="settings">Settings</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                placeholder="User filter..."
                value={filters.user}
                onChange={(e) => handleFilterChange('user', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={1}>
              <Button
                fullWidth
                variant="outlined"
                onClick={clearFilters}
                startIcon={<FilterList />}
              >
                Clear
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="audit logs tabs">
          <Tab label={`All Logs (${filteredLogs.length})`} />
          <Tab label="Recent Activity" />
          <Tab label="Failed Events" />
          <Tab label="Admin Actions" />
        </Tabs>
      </Paper>

      {/* Logs Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Resource</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredLogs.map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Schedule sx={{ mr: 1, color: 'text.secondary' }} />
                        <Typography variant="body2">
                          {formatDateTime(log.timestamp)}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getStatusIcon(log.status)}
                        <Chip
                          label={log.status}
                          size="small"
                          color={getStatusColor(log.status) as any}
                          sx={{ ml: 1 }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {log.userName}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {log.userId}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getActionIcon(log.action)}
                        <Typography variant="body2" sx={{ ml: 1 }}>
                          {log.action}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          {log.resource}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                          {log.resourceId}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Computer sx={{ mr: 1, color: 'text.secondary' }} />
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {log.ip}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <LocationOn sx={{ mr: 1, color: 'text.secondary' }} />
                        <Typography variant="body2">
                          {log.location || 'Unknown'}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleLogClick(log)}
                        color="primary"
                      >
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Log Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Audit Log Details
          {selectedLog && (
            <Chip
              label={selectedLog.status}
              size="small"
              color={getStatusColor(selectedLog.status) as any}
              sx={{ ml: 2 }}
            />
          )}
        </DialogTitle>
        <DialogContent>
          {selectedLog && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Timestamp
                  </Typography>
                  <Typography variant="body1">
                    {formatDateTime(selectedLog.timestamp)}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    User
                  </Typography>
                  <Typography variant="body1">
                    {selectedLog.userName} ({selectedLog.userId})
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Action
                  </Typography>
                  <Typography variant="body1">
                    {selectedLog.action}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Resource
                  </Typography>
                  <Typography variant="body1">
                    {selectedLog.resource} ({selectedLog.resourceId})
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    IP Address
                  </Typography>
                  <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                    {selectedLog.ip}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Location
                  </Typography>
                  <Typography variant="body1">
                    {selectedLog.location || 'Unknown'}
                  </Typography>
                </Grid>
                {selectedLog.correlationId && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Correlation ID
                    </Typography>
                    <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                      {selectedLog.correlationId}
                    </Typography>
                  </Grid>
                )}
                {selectedLog.sessionId && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Session ID
                    </Typography>
                    <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
                      {selectedLog.sessionId}
                    </Typography>
                  </Grid>
                )}
              </Grid>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">User Agent</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
                    {selectedLog.userAgent}
      </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">Event Details</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <pre style={{ fontSize: '14px', overflow: 'auto' }}>
                    {JSON.stringify(selectedLog.details, null, 2)}
                  </pre>
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
          <Button variant="contained" onClick={handleExport}>
            Export Log
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AuditLogs;
