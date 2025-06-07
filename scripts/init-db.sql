-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS payments;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set search path
ALTER DATABASE payments_db SET search_path TO payments, analytics, audit, public;

-- Create read-only user for analytics
CREATE USER analytics_reader WITH PASSWORD 'analytics_read_pass';
GRANT CONNECT ON DATABASE payments_db TO analytics_reader;
GRANT USAGE ON SCHEMA payments, analytics TO analytics_reader;

-- Performance optimizations
-- Increase work_mem for better query performance
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';

-- Enable query statistics
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Create database configuration table
CREATE TABLE IF NOT EXISTS config (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert initial configuration
INSERT INTO config (key, value, description) VALUES
    ('db_version', '1.0.0', 'Database schema version'),
    ('initialized_at', NOW()::TEXT, 'Database initialization timestamp'),
    ('timezone', 'UTC', 'Default timezone for the application')
ON CONFLICT (key) DO NOTHING; 