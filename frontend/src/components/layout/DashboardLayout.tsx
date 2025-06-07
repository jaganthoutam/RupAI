import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Divider,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Chip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Payment as PaymentIcon,
  Analytics as AnalyticsIcon,
  MonitorHeart as MonitorIcon,
  Security as SecurityIcon,
  Assessment as AuditIcon,
  Settings as SettingsIcon,
  Menu as MenuIcon,
  NotificationsActive as NotificationIcon,
  AccountCircle,
  Logout,
  Person,
  ChevronLeft,
  TrendingUp,
  People,
  AttachMoney,
  AccountBalanceWallet,
  SmartToy as AIIcon,
  Receipt,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const DRAWER_WIDTH = 280;

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const [open, setOpen] = useState(true);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, hasPermission } = useAuth();

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    handleProfileMenuClose();
    navigate('/login');
  };

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/',
      permission: 'read',
    },
    {
      text: 'AI Assistant',
      icon: <AIIcon />,
      path: '/ai-assistant',
      permission: 'read',
      badge: 'AI',
      badgeColor: 'primary' as const,
    },
    {
      text: 'Payments',
      icon: <PaymentIcon />,
      path: '/payments',
      permission: 'payments.read',
    },
    {
      text: 'Wallet Management',
      icon: <AccountBalanceWallet />,
      path: '/wallet-management',
      permission: 'wallets.read',
    },
    {
      text: 'Analytics',
      icon: <AnalyticsIcon />,
      path: '/analytics',
      permission: 'analytics.read',
      subItems: [
        {
          text: 'Payment Analytics',
          icon: <TrendingUp />,
          path: '/analytics/payments',
        },
        {
          text: 'User Analytics',
          icon: <People />,
          path: '/analytics/users',
        },
        {
          text: 'Revenue Analytics',
          icon: <AttachMoney />,
          path: '/analytics/revenue',
        },
      ],
    },
    {
      text: 'System Monitoring',
      icon: <MonitorIcon />,
      path: '/monitoring',
      permission: 'monitoring.read',
      subItems: [
        {
          text: 'System Health',
          icon: <MonitorIcon />,
          path: '/monitoring/system',
        },
        {
          text: 'Alerts',
          icon: <NotificationIcon />,
          path: '/monitoring/alerts',
        },
      ],
    },
    {
      text: 'Security',
      icon: <SecurityIcon />,
      path: '/security',
      permission: 'security.read',
      subItems: [
        {
          text: 'Fraud Detection',
          icon: <SecurityIcon />,
          path: '/security/fraud',
        },
      ],
    },
    {
      text: 'Audit Logs',
      icon: <AuditIcon />,
      path: '/audit/logs',
      permission: 'audit.read',
    },
    {
      text: 'User Management',
      icon: <Person />,
      path: '/users',
      permission: 'users.read',
    },
    {
      text: 'Subscription Management',
      icon: <Receipt />,
      path: '/subscriptions',
      permission: 'subscriptions.read',
    },
    {
      text: 'Settings',
      icon: <SettingsIcon />,
      path: '/settings',
      permission: 'settings.read',
    },
  ];

  const isActivePath = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const renderMenuItem = (item: any, isSubItem = false) => {
    if (!hasPermission(item.permission)) {
      return null;
    }

    const active = isActivePath(item.path);
    
    return (
      <ListItem key={item.path} disablePadding sx={{ display: 'block' }}>
        <ListItemButton
          onClick={() => navigate(item.path)}
          sx={{
            minHeight: 48,
            justifyContent: open ? 'initial' : 'center',
            px: 2.5,
            ml: isSubItem ? 2 : 0,
            backgroundColor: active ? theme.palette.primary.main + '20' : 'transparent',
            borderRight: active ? `3px solid ${theme.palette.primary.main}` : 'none',
            '&:hover': {
              backgroundColor: theme.palette.primary.main + '10',
            },
          }}
        >
          <ListItemIcon
            sx={{
              minWidth: 0,
              mr: open ? 3 : 'auto',
              justifyContent: 'center',
              color: active ? theme.palette.primary.main : 'inherit',
            }}
          >
            {item.icon}
          </ListItemIcon>
          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography
                  variant="body2"
                  sx={{
                    color: active ? theme.palette.primary.main : 'inherit',
                    fontWeight: active ? 600 : 400,
                  }}
                >
                  {item.text}
                </Typography>
                {item.badge && open && (
                  <Chip
                    label={item.badge}
                    size="small"
                    color={item.badgeColor || 'default'}
                    variant="outlined"
                    sx={{ fontSize: '0.7rem', height: '20px' }}
                  />
                )}
              </Box>
            }
            sx={{
              opacity: open ? 1 : 0,
            }}
          />
        </ListItemButton>
      </ListItem>
    );
  };

  const drawerContent = (
    <Box>
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: [1],
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <PaymentIcon sx={{ mr: 1, color: theme.palette.primary.main }} />
          {open && (
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600 }}>
              MCP Payments
            </Typography>
          )}
        </Box>
        <IconButton onClick={handleDrawerToggle}>
          <ChevronLeft />
        </IconButton>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <React.Fragment key={item.path}>
            {renderMenuItem(item)}
            {item.subItems && open && (
              <List component="div" disablePadding>
                {item.subItems.map((subItem) => renderMenuItem(subItem, true))}
              </List>
            )}
          </React.Fragment>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${open ? DRAWER_WIDTH : 64}px)` },
          ml: { sm: `${open ? DRAWER_WIDTH : 64}px` },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Enterprise Payments Dashboard
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              label={user?.role?.toUpperCase()}
              size="small"
              color="secondary"
              variant="outlined"
            />
            
            <IconButton color="inherit">
              <Badge badgeContent={4} color="error">
                <NotificationIcon />
              </Badge>
            </IconButton>
            
            <IconButton
              size="large"
              edge="end"
              aria-label="account of current user"
              aria-controls="profile-menu"
              aria-haspopup="true"
              onClick={handleProfileMenuOpen}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {user?.email?.charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{
          width: { sm: open ? DRAWER_WIDTH : 64 },
          flexShrink: { sm: 0 },
        }}
      >
        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={isMobile ? open : true}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: open ? DRAWER_WIDTH : 64,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              overflowX: 'hidden',
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${open ? DRAWER_WIDTH : 64}px)` },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar />
        {children}
      </Box>

      <Menu
        id="profile-menu"
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleProfileMenuClose}>
          <ListItemIcon>
            <Person fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem onClick={handleProfileMenuClose}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Settings
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default DashboardLayout; 