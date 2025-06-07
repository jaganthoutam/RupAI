import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Avatar,
  Tooltip,
  LinearProgress,
  Alert,
  Snackbar,
  Switch,
  FormControlLabel,
  InputAdornment,
  Fade,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Refresh,
  PersonAdd,
  SecurityUpdate,
  VisibilityOff,
  Visibility,
  FilterList,
  Download,
  Upload,
  Block,
  CheckCircle,
  Person,
  AdminPanelSettings,
  Work,
  Analytics,
  AccountCircle,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { ApiService } from '../services/apiService';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'operator' | 'analyst' | 'user' | 'guest';
  permissions: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
  total_transactions: number;
  total_spent: number;
}

interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  admin_users: number;
  operator_users: number;
  regular_users: number;
  new_users_today: number;
  new_users_this_week: number;
  new_users_this_month: number;
}

interface UserFormData {
  email: string;
  name: string;
  password: string;
  role: string;
  permissions: string[];
}

const ROLE_COLORS = {
  admin: '#f44336',
  operator: '#ff9800',
  analyst: '#2196f3',
  user: '#4caf50',
  guest: '#9e9e9e',
};

const ROLE_ICONS = {
  admin: <AdminPanelSettings />,
  operator: <Work />,
  analyst: <Analytics />,
  user: <Person />,
  guest: <AccountCircle />,
};

const AVAILABLE_PERMISSIONS = [
  'payments.read',
  'payments.write',
  'payments.delete',
  'wallets.read',
  'wallets.write',
  'analytics.read',
  'analytics.write',
  'users.read',
  'users.write',
  'users.delete',
  'compliance.read',
  'system.admin',
];

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' as 'success' | 'error' | 'info' });

  // Table state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [totalUsers, setTotalUsers] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Dialog state
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState<'create' | 'edit' | 'permissions'>('create');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<UserFormData>({
    email: '',
    name: '',
    password: '',
    role: 'user',
    permissions: [],
  });
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    loadUsers();
    loadStats();
  }, [page, rowsPerPage, searchTerm, roleFilter, statusFilter]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await ApiService.getUsers(page + 1, rowsPerPage, {
        search: searchTerm || undefined,
        role: roleFilter || undefined,
        active: statusFilter === 'active' ? true : statusFilter === 'inactive' ? false : undefined,
      });

      setUsers(response.users || []);
      setTotalUsers(response.total || 0);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load users';
      setError(errorMessage);
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
      console.error('Load users error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const statsResponse = await ApiService.getUserStats();
      setStats(statsResponse);
    } catch (err: any) {
      console.error('Load user stats error:', err);
    }
  };

  const handleCreateUser = async () => {
    try {
      setLoading(true);
      await ApiService.createUser(formData);
      
      setSnackbar({
        open: true,
        message: 'User created successfully',
        severity: 'success'
      });
      
      setOpenDialog(false);
      resetForm();
      loadUsers();
      loadStats();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create user';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async () => {
    if (!selectedUser) return;

    try {
      setLoading(true);
      await ApiService.updateUser(selectedUser.id, {
        name: formData.name,
        role: formData.role as any,
        permissions: formData.permissions,
      });
      
      setSnackbar({
        open: true,
        message: 'User updated successfully',
        severity: 'success'
      });
      
      setOpenDialog(false);
      resetForm();
      loadUsers();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update user';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: string, userName: string) => {
    if (!window.confirm(`Are you sure you want to delete user "${userName}"?`)) {
      return;
    }

    try {
      setLoading(true);
      await ApiService.deleteUser(userId);
      
      setSnackbar({
        open: true,
        message: 'User deleted successfully',
        severity: 'success'
      });
      
      loadUsers();
      loadStats();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete user';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId: string, currentStatus: boolean) => {
    try {
      setLoading(true);
      if (currentStatus) {
        await ApiService.deactivateUser(userId);
      } else {
        await ApiService.activateUser(userId);
      }
      
      setSnackbar({
        open: true,
        message: `User ${currentStatus ? 'deactivated' : 'activated'} successfully`,
        severity: 'success'
      });
      
      loadUsers();
      loadStats();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update user status';
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const openCreateDialog = () => {
    setDialogMode('create');
    resetForm();
    setOpenDialog(true);
  };

  const openEditDialog = (user: User) => {
    setDialogMode('edit');
    setSelectedUser(user);
    setFormData({
      email: user.email,
      name: user.name,
      password: '',
      role: user.role,
      permissions: user.permissions,
    });
    setOpenDialog(true);
  };

  const openPermissionsDialog = (user: User) => {
    setDialogMode('permissions');
    setSelectedUser(user);
    setFormData({
      email: user.email,
      name: user.name,
      password: '',
      role: user.role,
      permissions: user.permissions,
    });
    setOpenDialog(true);
  };

  const resetForm = () => {
    setFormData({
      email: '',
      name: '',
      password: '',
      role: 'user',
      permissions: [],
    });
    setSelectedUser(null);
    setShowPassword(false);
  };

  const handleFormSubmit = () => {
    if (dialogMode === 'create') {
      handleCreateUser();
    } else if (dialogMode === 'edit' || dialogMode === 'permissions') {
      handleUpdateUser();
    }
  };

  const handlePermissionToggle = (permission: string) => {
    const isSelected = formData.permissions.includes(permission);
    let newPermissions;
    
    if (isSelected) {
      newPermissions = formData.permissions.filter(p => p !== permission);
    } else {
      newPermissions = [...formData.permissions, permission];
    }
    
    setFormData({ ...formData, permissions: newPermissions });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusChip = (isActive: boolean) => (
    <Chip
      label={isActive ? 'Active' : 'Inactive'}
      color={isActive ? 'success' : 'default'}
      size="small"
      icon={isActive ? <CheckCircle /> : <Block />}
    />
  );

  const getRoleChip = (role: string) => (
    <Chip
      label={role.toUpperCase()}
      size="small"
      sx={{
        backgroundColor: ROLE_COLORS[role as keyof typeof ROLE_COLORS],
        color: 'white',
      }}
      icon={ROLE_ICONS[role as keyof typeof ROLE_ICONS]}
    />
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          User Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => { loadUsers(); loadStats(); }}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PersonAdd />}
            onClick={openCreateDialog}
          >
            Add User
          </Button>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Person />
                </Avatar>
                <Box>
                  <Typography variant="h6">{stats.total_users}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Users
                  </Typography>
                  <Typography variant="caption" color="success.main">
                    {stats.active_users} active
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <PersonAdd />
                </Avatar>
                <Box>
                  <Typography variant="h6">{stats.new_users_this_month}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    New This Month
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {stats.new_users_this_week} this week
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <AdminPanelSettings />
                </Avatar>
                <Box>
                  <Typography variant="h6">{stats.admin_users}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Administrators
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {stats.operator_users} operators
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
                <Avatar sx={{ bgcolor: 'error.main', mr: 2 }}>
                  <Block />
                </Avatar>
                <Box>
                  <Typography variant="h6">{stats.inactive_users}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Inactive Users
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {((stats.inactive_users / stats.total_users) * 100).toFixed(1)}% of total
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                label="Search users"
                variant="outlined"
                size="small"
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
            <Grid item xs={12} sm={3} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Role</InputLabel>
                <Select
                  value={roleFilter}
                  label="Role"
                  onChange={(e) => setRoleFilter(e.target.value)}
                >
                  <MenuItem value="">All Roles</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="operator">Operator</MenuItem>
                  <MenuItem value="analyst">Analyst</MenuItem>
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="guest">Guest</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  label="Status"
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Transactions</TableCell>
                <TableCell>Total Spent</TableCell>
                <TableCell>Last Login</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <AnimatePresence>
                {users.map((user) => (
                  <motion.tr
                    key={user.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <Avatar sx={{ mr: 2, bgcolor: ROLE_COLORS[user.role] }}>
                          {user.name.charAt(0).toUpperCase()}
                        </Avatar>
                        <Box>
                          <Typography variant="subtitle2">{user.name}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {user.email}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>{getRoleChip(user.role)}</TableCell>
                    <TableCell>{getStatusChip(user.is_active)}</TableCell>
                    <TableCell>{user.total_transactions.toLocaleString()}</TableCell>
                    <TableCell>{formatCurrency(user.total_spent)}</TableCell>
                    <TableCell>
                      {user.last_login ? formatDateTime(user.last_login) : 'Never'}
                    </TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell align="center">
                      <Tooltip title="Edit User">
                        <IconButton
                          size="small"
                          onClick={() => openEditDialog(user)}
                        >
                          <Edit />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Manage Permissions">
                        <IconButton
                          size="small"
                          onClick={() => openPermissionsDialog(user)}
                        >
                          <SecurityUpdate />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={user.is_active ? 'Deactivate' : 'Activate'}>
                        <IconButton
                          size="small"
                          onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                          color={user.is_active ? 'warning' : 'success'}
                        >
                          {user.is_active ? <Block /> : <CheckCircle />}
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete User">
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteUser(user.id, user.name)}
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={totalUsers}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Card>

      {/* User Dialog */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'create' && 'Create New User'}
          {dialogMode === 'edit' && 'Edit User'}
          {dialogMode === 'permissions' && 'Manage Permissions'}
        </DialogTitle>
        <DialogContent>
          {dialogMode !== 'permissions' && (
            <>
              <TextField
                autoFocus
                margin="dense"
                label="Email"
                type="email"
                fullWidth
                variant="outlined"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                disabled={dialogMode === 'edit'}
                sx={{ mb: 2 }}
              />
              <TextField
                margin="dense"
                label="Full Name"
                fullWidth
                variant="outlined"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                sx={{ mb: 2 }}
              />
              {dialogMode === 'create' && (
                <TextField
                  margin="dense"
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  fullWidth
                  variant="outlined"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{ mb: 2 }}
                />
              )}
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Role</InputLabel>
                <Select
                  value={formData.role}
                  label="Role"
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                >
                  <MenuItem value="user">User</MenuItem>
                  <MenuItem value="analyst">Analyst</MenuItem>
                  <MenuItem value="operator">Operator</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="guest">Guest</MenuItem>
                </Select>
              </FormControl>
            </>
          )}

          {/* Permissions Section */}
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            Permissions
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <List dense>
            {AVAILABLE_PERMISSIONS.map((permission) => (
              <ListItem key={permission} dense>
                <ListItemText
                  primary={permission}
                  secondary={`Access to ${permission.split('.')[0]} module`}
                />
                <ListItemSecondaryAction>
                  <Checkbox
                    edge="end"
                    checked={formData.permissions.includes(permission)}
                    onChange={() => handlePermissionToggle(permission)}
                  />
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            onClick={handleFormSubmit}
            variant="contained"
            disabled={
              !formData.email ||
              !formData.name ||
              (dialogMode === 'create' && !formData.password)
            }
          >
            {dialogMode === 'create' && 'Create User'}
            {dialogMode === 'edit' && 'Update User'}
            {dialogMode === 'permissions' && 'Update Permissions'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default UserManagement; 