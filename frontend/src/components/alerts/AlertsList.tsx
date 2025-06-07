import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Box,
  IconButton,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Error,
  Warning,
  Info,
  CheckCircle,
  Refresh,
  Clear,
} from '@mui/icons-material';
import { format } from 'date-fns';

interface AlertItem {
  id: string;
  type: 'error' | 'warning' | 'info' | 'success';
  message: string;
  timestamp: string;
  resolved: boolean;
}

interface AlertsListProps {
  alerts: AlertItem[];
  loading?: boolean;
  onRefresh?: () => void;
  onDismiss?: (alertId: string) => void;
}

const AlertsList: React.FC<AlertsListProps> = ({
  alerts = [],
  loading = false,
  onRefresh,
  onDismiss,
}) => {
  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'error':
        return <Error color="error" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'info':
        return <Info color="info" />;
      case 'success':
        return <CheckCircle color="success" />;
      default:
        return <Info color="info" />;
    }
  };

  const getAlertSeverity = (type: string): 'error' | 'warning' | 'info' | 'success' => {
    return type as 'error' | 'warning' | 'info' | 'success';
  };

  const activeAlerts = alerts.filter(alert => !alert.resolved);

  return (
    <Card elevation={2}>
      <CardHeader
        title="Active Alerts"
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={activeAlerts.length}
              color={activeAlerts.length > 0 ? 'error' : 'success'}
              size="small"
            />
            {onRefresh && (
              <Tooltip title="Refresh alerts">
                <IconButton onClick={onRefresh} disabled={loading}>
                  <Refresh />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        }
        sx={{ pb: 1 }}
      />
      <CardContent sx={{ pt: 0 }}>
        {activeAlerts.length === 0 ? (
          <Alert severity="success" variant="outlined">
            <Typography variant="body2">
              No active alerts. All systems are operating normally.
            </Typography>
          </Alert>
        ) : (
          <List disablePadding>
            {activeAlerts.map((alert, index) => (
              <React.Fragment key={alert.id}>
                <ListItem
                  sx={{
                    px: 0,
                    py: 1,
                    borderRadius: 1,
                    '&:hover': {
                      backgroundColor: 'grey.50',
                    },
                  }}
                  secondaryAction={
                    onDismiss && (
                      <Tooltip title="Dismiss alert">
                        <IconButton
                          edge="end"
                          onClick={() => onDismiss(alert.id)}
                          size="small"
                        >
                          <Clear fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )
                  }
                >
                  <ListItemIcon sx={{ minWidth: 36 }}>
                    {getAlertIcon(alert.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {alert.message}
                      </Typography>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        {format(new Date(alert.timestamp), 'MMM dd, HH:mm:ss')}
                      </Typography>
                    }
                  />
                </ListItem>
                {index < activeAlerts.length - 1 && (
                  <Box sx={{ borderBottom: 1, borderColor: 'divider', mx: 1 }} />
                )}
              </React.Fragment>
            ))}
          </List>
        )}

        {activeAlerts.length > 5 && (
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              Showing 5 of {activeAlerts.length} alerts
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default AlertsList; 