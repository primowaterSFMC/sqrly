-- Sqrly ADHD Planner Database Initialization Script
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database user for the application (if not using default postgres user)
-- DO $$ 
-- BEGIN
--     IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'sqrly_user') THEN
--         CREATE ROLE sqrly_user WITH LOGIN PASSWORD 'sqrly_password';
--     END IF;
-- END
-- $$;

-- Grant necessary permissions
-- GRANT ALL PRIVILEGES ON DATABASE sqrly_adhd_planner TO sqrly_user;

-- Set timezone
SET timezone = 'UTC';

-- Log initialization
SELECT 'Sqrly ADHD Planner database initialized successfully' AS status;
