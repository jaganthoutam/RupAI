import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import Cookies from 'js-cookie'
import { AuthService, User, AuthResponse } from '../services/apiService'
import { toast } from 'react-toastify'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => Promise<void>
  updateUser: (userData: Partial<User>) => Promise<void>
}

interface RegisterData {
  email: string
  password: string
  name: string
  phone?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = !!user

  useEffect(() => {
    initializeAuth()
  }, [])

  const initializeAuth = async () => {
    try {
      const token = Cookies.get('auth_token')
      if (token) {
        const userProfile = await AuthService.getProfile()
        setUser(userProfile)
      }
    } catch (error) {
      console.error('Auth initialization error:', error)
      Cookies.remove('auth_token')
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string): Promise<void> => {
    try {
      setIsLoading(true)
      const response: AuthResponse = await AuthService.login(email, password)
      
      // Store token
      Cookies.set('auth_token', response.access_token, {
        expires: response.expires_in / (24 * 60 * 60), // Convert seconds to days
        secure: window.location.protocol === 'https:',
        sameSite: 'strict'
      })
      
      setUser(response.user)
      toast.success(`Welcome back, ${response.user.name}!`)
    } catch (error: any) {
      console.error('Login error:', error)
      toast.error(error.response?.data?.detail || 'Login failed. Please try again.')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (userData: RegisterData): Promise<void> => {
    try {
      setIsLoading(true)
      const response: AuthResponse = await AuthService.register(userData)
      
      // Store token
      Cookies.set('auth_token', response.access_token, {
        expires: response.expires_in / (24 * 60 * 60),
        secure: window.location.protocol === 'https:',
        sameSite: 'strict'
      })
      
      setUser(response.user)
      toast.success(`Welcome to MCP Payments, ${response.user.name}!`)
    } catch (error: any) {
      console.error('Registration error:', error)
      toast.error(error.response?.data?.detail || 'Registration failed. Please try again.')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async (): Promise<void> => {
    try {
      await AuthService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      Cookies.remove('auth_token')
      toast.info('You have been logged out successfully.')
    }
  }

  const updateUser = async (userData: Partial<User>): Promise<void> => {
    try {
      const updatedUser = await AuthService.updateProfile(userData)
      setUser(updatedUser)
      toast.success('Profile updated successfully!')
    } catch (error: any) {
      console.error('Profile update error:', error)
      toast.error(error.response?.data?.detail || 'Profile update failed.')
      throw error
    }
  }

  const contextValue: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    updateUser,
  }

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext 