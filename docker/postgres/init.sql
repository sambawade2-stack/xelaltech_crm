-- FinTrack CRM — PostgreSQL init
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Optimize for full-text search
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET shared_buffers = '256MB';
