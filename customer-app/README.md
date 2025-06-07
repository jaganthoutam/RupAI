# MCP Payments Customer Application

A modern, responsive customer-facing application for the MCP Payments Enterprise System. Built with React 18, TypeScript, and Material-UI.

## 🚀 Features

### Core Functionality
- **User Authentication** - Secure login and registration with JWT tokens
- **Dashboard** - Overview of account balance, recent transactions, and quick actions
- **Payment Processing** - Multi-step payment flow with multiple payment methods
- **Wallet Management** - Digital wallet with multi-currency support
- **Transaction History** - Comprehensive transaction tracking with filtering and search
- **Profile Management** - User profile and account settings

### Payment Methods Supported
- Credit/Debit Cards
- Bank Transfers
- Digital Wallets
- UPI (Unified Payments Interface)

### Security Features
- JWT-based authentication
- Secure API communication
- Input validation and sanitization
- CSRF protection
- XSS prevention

## 🛠️ Technology Stack

- **Frontend Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) v5
- **State Management**: React Context + React Query
- **Routing**: React Router v6
- **Form Handling**: React Hook Form with Yup validation
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Date Handling**: Day.js
- **Notifications**: React Toastify
- **Animations**: Framer Motion
- **QR Codes**: React QR Code
- **Build Tool**: Vite
- **Package Manager**: npm

## 📋 Prerequisites

- Node.js 18+ 
- npm 8+
- MCP Payments Backend API running on port 8000

## 🚀 Quick Start

### 1. Clone and Install Dependencies

```bash
# Navigate to customer app directory
cd customer-app

# Install dependencies
npm install
```

### 2. Environment Configuration

Create a `.env.local` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=MCP Payments
VITE_APP_VERSION=1.0.0
```

### 3. Development Server

```bash
# Start development server
npm run dev

# Application will be available at http://localhost:3000
```

### 4. Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Customer app will be available at http://localhost:3000
# Backend API at http://localhost:8000
```

### Using Docker Only

```bash
# Build the image
docker build -t mcp-payments-customer .

# Run the container
docker run -p 3000:3000 \
  -e VITE_API_BASE_URL=http://localhost:8000 \
  mcp-payments-customer
```

## 📁 Project Structure

```
customer-app/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Layout.tsx     # Main application layout
│   │   └── ProtectedRoute.tsx
│   ├── contexts/          # React contexts
│   │   ├── AuthContext.tsx
│   │   └── PaymentContext.tsx
│   ├── pages/             # Page components
│   │   ├── LandingPage.tsx
│   │   ├── AuthPage.tsx
│   │   ├── Dashboard.tsx
│   │   ├── PaymentPage.tsx
│   │   ├── WalletPage.tsx
│   │   ├── TransactionHistory.tsx
│   │   ├── ProfilePage.tsx
│   │   └── SupportPage.tsx
│   ├── services/          # API services
│   │   └── apiService.ts
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── hooks/             # Custom React hooks
│   ├── App.tsx            # Main app component
│   └── main.tsx           # Application entry point
├── package.json
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking

# Docker
docker-compose up    # Start with Docker Compose
```

## 🌟 Key Features Overview

### Authentication System
- **Login/Register**: Secure authentication with form validation
- **JWT Tokens**: Automatic token management and refresh
- **Protected Routes**: Route-level authentication guards
- **Session Management**: Persistent login state

### Dashboard
- **Account Overview**: Real-time balance and statistics
- **Recent Transactions**: Latest payment activity
- **Quick Actions**: Fast access to common operations
- **Visual Analytics**: Charts and graphs for spending patterns

### Payment Processing
- **Multi-Step Flow**: Guided payment process
- **Payment Methods**: Support for cards, bank transfers, wallets, UPI
- **Real-time Validation**: Form validation and error handling
- **Confirmation**: Detailed payment confirmation and receipts

### Wallet Management
- **Multi-Currency**: Support for multiple currencies
- **Balance Overview**: Available and pending balances
- **Fund Management**: Add funds and transfer money
- **Transaction History**: Detailed wallet transaction logs

### Transaction History
- **Advanced Filtering**: Filter by status, type, date range
- **Search Functionality**: Search transactions by description or ID
- **Pagination**: Efficient handling of large transaction lists
- **Export Options**: Download transaction reports

## 🔒 Security Considerations

- **HTTPS Only**: All API communications over HTTPS
- **Input Sanitization**: All user inputs are validated and sanitized
- **XSS Protection**: Content Security Policy headers
- **CSRF Protection**: Anti-CSRF tokens for state-changing operations
- **Secure Headers**: Security headers for additional protection

## 🎨 UI/UX Features

- **Responsive Design**: Mobile-first responsive layout
- **Material Design**: Modern Material-UI components
- **Dark/Light Theme**: Theme switching capability
- **Accessibility**: WCAG 2.1 AA compliance
- **Loading States**: Skeleton loaders and progress indicators
- **Error Handling**: User-friendly error messages
- **Notifications**: Toast notifications for user feedback

## 🔗 API Integration

The application integrates with the MCP Payments Backend API:

- **Authentication**: `/auth/login`, `/auth/register`
- **Payments**: `/payments/create`, `/payments/verify`
- **Wallets**: `/wallets/balance`, `/wallets/transactions`
- **Users**: `/users/profile`, `/users/update`

## 🚀 Performance Optimizations

- **Code Splitting**: Lazy loading of route components
- **Bundle Optimization**: Tree shaking and minification
- **Caching**: HTTP caching and service worker support
- **Image Optimization**: Optimized image loading
- **Gzip Compression**: Server-side compression

## 🧪 Testing

```bash
# Run unit tests
npm run test

# Run integration tests
npm run test:integration

# Run e2e tests
npm run test:e2e

# Generate coverage report
npm run test:coverage
```

## 📈 Monitoring and Analytics

- **Error Tracking**: Integration with error monitoring services
- **Performance Monitoring**: Core Web Vitals tracking
- **User Analytics**: User behavior and conversion tracking
- **API Monitoring**: API response time and error rate monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- **Documentation**: Check the [docs](../docs/) directory
- **Issues**: Create an issue on GitHub
- **Email**: support@mcppayments.com

## 🔄 Version History

- **v1.0.0** - Initial release with core payment functionality
- **v1.1.0** - Added wallet management and multi-currency support
- **v1.2.0** - Enhanced security and performance optimizations

---

**Built with ❤️ by the MCP Payments Team** 