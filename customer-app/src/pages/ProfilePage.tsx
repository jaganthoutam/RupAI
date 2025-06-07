import React, { useState, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Avatar,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  Divider,
  Paper
} from '@mui/material'
import {
  Person,
  Edit,
  Security,
  Notifications,
  CreditCard,
  History,
  CheckCircle,
  Warning
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import apiService from '../services/apiService'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

const ProfilePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [editMode, setEditMode] = useState(false)
  
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    country: ''
  })

  const [notifications, setNotifications] = useState({
    email: true,
    sms: false,
    push: true,
    marketing: false
  })

  const { user, updateUser } = useAuth()

  useEffect(() => {
    if (user) {
      setProfileData({
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || '',
        address: '',
        city: '',
        country: ''
      })
    }
  }, [user])

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue)
  }

  const handleProfileUpdate = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await updateUser(profileData)
      setSuccess('Profile updated successfully!')
      setEditMode(false)
    } catch (err: any) {
      setError(err.message || 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const handleNotificationChange = (key: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setNotifications(prev => ({
      ...prev,
      [key]: event.target.checked
    }))
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Profile
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Manage your account settings and preferences.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {/* Profile Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={3}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                bgcolor: 'primary.main',
                fontSize: '2rem'
              }}
            >
              {user?.name?.charAt(0)?.toUpperCase() || 'U'}
            </Avatar>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                {user?.name || 'User'}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {user?.email}
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                <CheckCircle color="success" fontSize="small" />
                <Typography variant="body2" color="success.main">
                  Verified Account
                </Typography>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<Person />} label="Personal Info" />
          <Tab icon={<Security />} label="Security" />
          <Tab icon={<Notifications />} label="Notifications" />
          <Tab icon={<CreditCard />} label="Payment Methods" />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          {/* Personal Information */}
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Personal Information
            </Typography>
            <Button
              startIcon={<Edit />}
              onClick={() => setEditMode(!editMode)}
              variant={editMode ? "outlined" : "contained"}
            >
              {editMode ? 'Cancel' : 'Edit Profile'}
            </Button>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Full Name"
                value={profileData.name}
                onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                disabled={!editMode}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={profileData.email}
                onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                disabled={!editMode}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone"
                value={profileData.phone}
                onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                disabled={!editMode}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Country"
                value={profileData.country}
                onChange={(e) => setProfileData({ ...profileData, country: e.target.value })}
                disabled={!editMode}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                value={profileData.address}
                onChange={(e) => setProfileData({ ...profileData, address: e.target.value })}
                disabled={!editMode}
                multiline
                rows={2}
              />
            </Grid>
          </Grid>

          {editMode && (
            <Box mt={3} display="flex" gap={2}>
              <Button
                variant="contained"
                onClick={handleProfileUpdate}
                disabled={loading}
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                }}
              >
                {loading ? <CircularProgress size={24} /> : 'Save Changes'}
              </Button>
              <Button variant="outlined" onClick={() => setEditMode(false)}>
                Cancel
              </Button>
            </Box>
          )}
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {/* Security Settings */}
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Security Settings
          </Typography>

          <List>
            <ListItem>
              <ListItemIcon>
                <Security color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Change Password"
                secondary="Update your account password"
              />
              <Button variant="outlined" size="small">
                Change
              </Button>
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <CheckCircle color="success" />
              </ListItemIcon>
              <ListItemText
                primary="Two-Factor Authentication"
                secondary="Enabled - Your account is protected with 2FA"
              />
              <Button variant="outlined" size="small" color="error">
                Disable
              </Button>
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <History color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Login Activity"
                secondary="View recent login history and active sessions"
              />
              <Button variant="outlined" size="small">
                View
              </Button>
            </ListItem>
          </List>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          {/* Notification Settings */}
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Notification Preferences
          </Typography>

          <List>
            <ListItem>
              <ListItemIcon>
                <Notifications color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Email Notifications"
                secondary="Receive email notifications for important updates"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.email}
                    onChange={handleNotificationChange('email')}
                  />
                }
                label=""
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <Notifications color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="SMS Notifications"
                secondary="Receive SMS notifications for transactions"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.sms}
                    onChange={handleNotificationChange('sms')}
                  />
                }
                label=""
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <Notifications color="primary" />
              </ListItemIcon>
              <ListItemText
                primary="Push Notifications"
                secondary="Receive push notifications on your device"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.push}
                    onChange={handleNotificationChange('push')}
                  />
                }
                label=""
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemIcon>
                <Warning color="warning" />
              </ListItemIcon>
              <ListItemText
                primary="Marketing Communications"
                secondary="Receive promotional emails and offers"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.marketing}
                    onChange={handleNotificationChange('marketing')}
                  />
                }
                label=""
              />
            </ListItem>
          </List>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          {/* Payment Methods */}
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Payment Methods
          </Typography>

          <Alert severity="info" sx={{ mb: 3 }}>
            Manage your saved payment methods for faster checkout.
          </Alert>

          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <CreditCard sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              No Payment Methods Added
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Add a payment method to make transactions faster and easier.
            </Typography>
            <Button
              variant="contained"
              startIcon={<CreditCard />}
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              }}
            >
              Add Payment Method
            </Button>
          </Paper>
        </TabPanel>
      </Card>
    </Box>
  )
}

export default ProfilePage 