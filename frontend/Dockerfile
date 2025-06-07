# Multi-stage Dockerfile for React frontend with development and production targets
FROM node:18-alpine as base

WORKDIR /app

# Copy package files
COPY package*.json ./

# Development Stage
FROM base as development

# Install all dependencies (including dev dependencies)
RUN npm install

# Create non-root user for development
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copy source code (will be overridden by volume mount in dev)
COPY --chown=nextjs:nodejs . .

USER nextjs

EXPOSE 3000

# Start development server with hot reload
CMD ["npm", "start"]

# Builder Stage  
FROM base as builder

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production Stage
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Add health check script
RUN echo '#!/bin/sh' > /usr/local/bin/health-check.sh && \
    echo 'curl -f http://localhost:80/ || exit 1' >> /usr/local/bin/health-check.sh && \
    chmod +x /usr/local/bin/health-check.sh

# Create health endpoint
RUN echo 'OK' > /usr/share/nginx/html/health

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD /usr/local/bin/health-check.sh

CMD ["nginx", "-g", "daemon off;"] 