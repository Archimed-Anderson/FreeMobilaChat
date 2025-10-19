-- PostgreSQL Database Initialization Script for FreeMobilaChat
-- This script creates the database schema and initial data

-- Create database (if running manually, uncomment the next line)
-- CREATE DATABASE freemobilachat_prod;

-- Connect to the database
\c freemobilachat_prod;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types for enums
CREATE TYPE sentiment_type AS ENUM ('positive', 'neutral', 'negative', 'unknown');
CREATE TYPE category_type AS ENUM ('facturation', 'réseau', 'technique', 'abonnement', 'réclamation', 'compliment', 'question', 'autre');
CREATE TYPE priority_type AS ENUM ('critique', 'haute', 'moyenne', 'basse');
CREATE TYPE user_role_type AS ENUM ('agent_sav', 'manager', 'analyste', 'admin');

-- Main tweets table with analysis results
CREATE TABLE IF NOT EXISTS tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(50) UNIQUE NOT NULL,
    author VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    retweet_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    
    -- Extracted metadata
    mentions JSONB DEFAULT '[]'::jsonb,
    hashtags JSONB DEFAULT '[]'::jsonb,
    urls JSONB DEFAULT '[]'::jsonb,
    
    -- LLM Analysis results
    sentiment sentiment_type,
    sentiment_score REAL CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0),
    category category_type,
    priority priority_type,
    keywords JSONB DEFAULT '[]'::jsonb,
    
    -- Enrichment data
    is_urgent BOOLEAN DEFAULT FALSE,
    needs_response BOOLEAN DEFAULT TRUE,
    estimated_resolution_time INTEGER CHECK (estimated_resolution_time >= 0),
    
    -- Timestamps
    analyzed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analysis logs for tracking batch processing and costs
CREATE TABLE IF NOT EXISTS analysis_logs (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(50) UNIQUE NOT NULL,
    total_tweets INTEGER NOT NULL CHECK (total_tweets >= 0),
    successful_analysis INTEGER NOT NULL CHECK (successful_analysis >= 0),
    failed_analysis INTEGER NOT NULL CHECK (failed_analysis >= 0),
    llm_provider VARCHAR(50) NOT NULL,
    total_cost REAL DEFAULT 0.0 CHECK (total_cost >= 0.0),
    processing_time REAL DEFAULT 0.0 CHECK (processing_time >= 0.0),
    error_details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (successful_analysis + failed_analysis <= total_tweets)
);

-- Users table for role-based access control
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    role user_role_type NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System configuration for application settings
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Training metadata table
CREATE TABLE IF NOT EXISTS training_metadata (
    id SERIAL PRIMARY KEY,
    preparation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    total_samples INTEGER NOT NULL,
    train_samples INTEGER NOT NULL,
    val_samples INTEGER NOT NULL,
    test_samples INTEGER NOT NULL,
    file_paths JSONB NOT NULL,
    statistics JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Evaluation results table
CREATE TABLE IF NOT EXISTS evaluation_results (
    id SERIAL PRIMARY KEY,
    evaluation_date TIMESTAMP WITH TIME ZONE NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    test_samples INTEGER NOT NULL,
    metrics JSONB NOT NULL,
    files JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    analysis_date TIMESTAMP WITH TIME ZONE NOT NULL,
    provider VARCHAR(50) NOT NULL,
    total_tweets INTEGER NOT NULL,
    analysis_summary JSONB NOT NULL,
    kpi_metrics JSONB NOT NULL,
    insights_and_recommendations JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tweets_tweet_id ON tweets (tweet_id);
CREATE INDEX IF NOT EXISTS idx_tweets_date ON tweets (date);
CREATE INDEX IF NOT EXISTS idx_tweets_sentiment ON tweets (sentiment);
CREATE INDEX IF NOT EXISTS idx_tweets_priority ON tweets (priority);
CREATE INDEX IF NOT EXISTS idx_tweets_category ON tweets (category);
CREATE INDEX IF NOT EXISTS idx_tweets_urgent ON tweets (is_urgent);
CREATE INDEX IF NOT EXISTS idx_tweets_needs_response ON tweets (needs_response);
CREATE INDEX IF NOT EXISTS idx_tweets_analyzed_at ON tweets (analyzed_at);
CREATE INDEX IF NOT EXISTS idx_tweets_author ON tweets (author);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_tweets_text_search ON tweets USING gin(to_tsvector('french', text));
CREATE INDEX IF NOT EXISTS idx_tweets_keywords_search ON tweets USING gin(keywords);

-- Analysis logs indexes
CREATE INDEX IF NOT EXISTS idx_analysis_logs_batch_id ON analysis_logs (batch_id);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_provider ON analysis_logs (llm_provider);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_created_at ON analysis_logs (created_at);

-- Users indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users (is_active);

-- System config indexes
CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config (config_key);

-- Create update trigger for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_tweets_updated_at BEFORE UPDATE ON tweets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, description) VALUES
    ('app_version', '1.0.0', 'Application version'),
    ('maintenance_mode', 'false', 'Enable/disable maintenance mode'),
    ('max_file_size_mb', '200', 'Maximum file upload size in MB'),
    ('default_batch_size', '10', 'Default batch size for analysis'),
    ('rate_limit_per_minute', '30', 'Rate limit for API calls per minute')
ON CONFLICT (config_key) DO NOTHING;

-- Insert default admin user (password should be changed in production)
INSERT INTO users (username, role, is_active) VALUES
    ('admin', 'admin', true),
    ('manager', 'manager', true),
    ('agent', 'agent_sav', true)
ON CONFLICT (username) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mobilachat_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mobilachat_user;

-- Create backup user (optional)
-- CREATE USER backup_user WITH PASSWORD 'backup_password';
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;

COMMIT;
