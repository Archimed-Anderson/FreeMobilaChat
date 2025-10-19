"""
Database schema definitions for tweet analysis platform
SQL schema for SQLite/PostgreSQL with proper indexing and constraints
"""

# SQL Schema for SQLite/PostgreSQL
DATABASE_SCHEMA = """
-- Table principale tweets
-- Main tweets table with analysis results
CREATE TABLE IF NOT EXISTS tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(50) UNIQUE NOT NULL,
    author VARCHAR(100) NOT NULL,
    text TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    retweet_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    
    -- Métadonnées extraites - Extracted metadata
    mentions JSON DEFAULT '[]',
    hashtags JSON DEFAULT '[]',
    urls JSON DEFAULT '[]',
    
    -- Analyse LLM - LLM Analysis results
    sentiment VARCHAR(20) CHECK (sentiment IN ('positive', 'neutral', 'negative', 'unknown')),
    sentiment_score REAL CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0),
    category VARCHAR(50) CHECK (category IN ('facturation', 'réseau', 'technique', 'abonnement', 'réclamation', 'compliment', 'question', 'autre')),
    priority VARCHAR(20) CHECK (priority IN ('critique', 'haute', 'moyenne', 'basse')),
    keywords JSON DEFAULT '[]',
    
    -- Enrichissement - Enrichment data
    is_urgent BOOLEAN DEFAULT FALSE,
    needs_response BOOLEAN DEFAULT TRUE,
    estimated_resolution_time INTEGER CHECK (estimated_resolution_time >= 0),
    
    -- Timestamps
    analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table logs d'analyse
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (successful_analysis + failed_analysis <= total_tweets)
);

-- Table utilisateurs (simple auth)
-- Users table for role-based access control
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('agent_sav', 'manager', 'analyste', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table configuration système
-- System configuration for application settings
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

CREATE INDEX IF NOT EXISTS idx_analysis_logs_batch_id ON analysis_logs (batch_id);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_provider ON analysis_logs (llm_provider);
CREATE INDEX IF NOT EXISTS idx_analysis_logs_created_at ON analysis_logs (created_at);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users (is_active);

CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config (config_key);

-- Vues pour les requêtes fréquentes
-- Views for common queries

-- Vue tweets avec priorité critique
CREATE VIEW IF NOT EXISTS critical_tweets AS
SELECT 
    tweet_id,
    author,
    text,
    date,
    sentiment,
    category,
    priority,
    is_urgent,
    needs_response,
    estimated_resolution_time,
    analyzed_at
FROM tweets 
WHERE priority = 'critique' 
ORDER BY date DESC;

-- Vue métriques quotidiennes
CREATE VIEW IF NOT EXISTS daily_metrics AS
SELECT 
    DATE(date) as analysis_date,
    COUNT(*) as total_tweets,
    COUNT(CASE WHEN sentiment = 'positive' THEN 1 END) as positive_count,
    COUNT(CASE WHEN sentiment = 'neutral' THEN 1 END) as neutral_count,
    COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative_count,
    COUNT(CASE WHEN priority = 'critique' THEN 1 END) as critical_count,
    COUNT(CASE WHEN priority = 'haute' THEN 1 END) as high_priority_count,
    COUNT(CASE WHEN is_urgent = TRUE THEN 1 END) as urgent_count,
    COUNT(CASE WHEN needs_response = TRUE THEN 1 END) as needs_response_count,
    AVG(sentiment_score) as avg_sentiment_score,
    AVG(estimated_resolution_time) as avg_resolution_time
FROM tweets 
WHERE analyzed_at IS NOT NULL
GROUP BY DATE(date)
ORDER BY analysis_date DESC;

-- Vue distribution par catégorie
CREATE VIEW IF NOT EXISTS category_distribution AS
SELECT 
    category,
    COUNT(*) as tweet_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tweets WHERE analyzed_at IS NOT NULL), 2) as percentage,
    COUNT(CASE WHEN sentiment = 'negative' THEN 1 END) as negative_count,
    COUNT(CASE WHEN priority IN ('critique', 'haute') THEN 1 END) as high_priority_count
FROM tweets 
WHERE analyzed_at IS NOT NULL
GROUP BY category
ORDER BY tweet_count DESC;

-- Triggers pour mise à jour automatique des timestamps
-- Triggers for automatic timestamp updates

-- Trigger pour tweets
CREATE TRIGGER IF NOT EXISTS update_tweets_timestamp 
    AFTER UPDATE ON tweets
    FOR EACH ROW
BEGIN
    UPDATE tweets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger pour users
CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
    AFTER UPDATE ON users
    FOR EACH ROW
BEGIN
    UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger pour system_config
CREATE TRIGGER IF NOT EXISTS update_config_timestamp 
    AFTER UPDATE ON system_config
    FOR EACH ROW
BEGIN
    UPDATE system_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Insertion des données de configuration par défaut
-- Default configuration data insertion
INSERT OR IGNORE INTO system_config (config_key, config_value, description) VALUES
('max_tweets_per_batch', '500', 'Maximum number of tweets to process in a single batch'),
('default_llm_provider', 'openai', 'Default LLM provider for analysis'),
('rate_limit_requests_per_minute', '30', 'Rate limit for API requests per minute'),
('batch_processing_delay', '2', 'Delay in seconds between batch processing'),
('max_concurrent_requests', '5', 'Maximum concurrent API requests'),
('analysis_timeout_seconds', '30', 'Timeout for individual tweet analysis'),
('enable_fallback_analysis', 'true', 'Enable fallback analysis methods'),
('min_tweet_length', '10', 'Minimum tweet length for analysis');

-- Insertion d'un utilisateur admin par défaut
-- Default admin user insertion
INSERT OR IGNORE INTO users (username, role) VALUES ('admin', 'admin');
"""

# PostgreSQL specific optimizations (if using PostgreSQL instead of SQLite)
POSTGRESQL_OPTIMIZATIONS = """
-- PostgreSQL specific optimizations
-- Use JSONB instead of JSON for better performance
ALTER TABLE tweets ALTER COLUMN mentions TYPE JSONB USING mentions::JSONB;
ALTER TABLE tweets ALTER COLUMN hashtags TYPE JSONB USING hashtags::JSONB;
ALTER TABLE tweets ALTER COLUMN urls TYPE JSONB USING urls::JSONB;
ALTER TABLE tweets ALTER COLUMN keywords TYPE JSONB USING keywords::JSONB;

-- Additional indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_tweets_mentions_gin ON tweets USING GIN (mentions);
CREATE INDEX IF NOT EXISTS idx_tweets_hashtags_gin ON tweets USING GIN (hashtags);
CREATE INDEX IF NOT EXISTS idx_tweets_keywords_gin ON tweets USING GIN (keywords);

-- Partial indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tweets_urgent_true ON tweets (date, priority) WHERE is_urgent = TRUE;
CREATE INDEX IF NOT EXISTS idx_tweets_needs_response_true ON tweets (date, category) WHERE needs_response = TRUE;
CREATE INDEX IF NOT EXISTS idx_tweets_negative_sentiment ON tweets (date, priority) WHERE sentiment = 'negative';

-- Full-text search index for tweet content
CREATE INDEX IF NOT EXISTS idx_tweets_text_fts ON tweets USING GIN (to_tsvector('french', text));
"""

# Database initialization functions
def get_database_schema() -> str:
    """Return the complete database schema"""
    return DATABASE_SCHEMA

def get_postgresql_optimizations() -> str:
    """Return PostgreSQL specific optimizations"""
    return POSTGRESQL_OPTIMIZATIONS

# Table creation order (for proper foreign key handling)
TABLE_CREATION_ORDER = [
    'users',
    'system_config', 
    'tweets',
    'analysis_logs'
]

# Required indexes for performance
REQUIRED_INDEXES = [
    'idx_tweet_id',
    'idx_date',
    'idx_sentiment',
    'idx_priority',
    'idx_category',
    'idx_urgent',
    'idx_needs_response'
]

# Additional tables for training and evaluation
TRAINING_TABLES_SCHEMA = """
-- Table métadonnées d'entraînement - Training metadata
CREATE TABLE IF NOT EXISTS training_metadata (
    id SERIAL PRIMARY KEY,
    preparation_date TIMESTAMP NOT NULL,
    source_file VARCHAR(500) NOT NULL,
    total_samples INTEGER NOT NULL,
    train_samples INTEGER NOT NULL,
    val_samples INTEGER NOT NULL,
    test_samples INTEGER NOT NULL,
    file_paths JSON NOT NULL,
    statistics JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table résultats d'évaluation - Evaluation results
CREATE TABLE IF NOT EXISTS evaluation_results (
    id SERIAL PRIMARY KEY,
    evaluation_date TIMESTAMP NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    test_samples INTEGER NOT NULL,
    metrics JSON NOT NULL,
    files JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table résultats d'analyse complète - Complete analysis results
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    analysis_date TIMESTAMP NOT NULL,
    provider VARCHAR(50) NOT NULL,
    total_tweets INTEGER NOT NULL,
    analysis_summary JSON NOT NULL,
    kpi_metrics JSON NOT NULL,
    insights_and_recommendations JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for training tables
CREATE INDEX IF NOT EXISTS idx_training_preparation_date ON training_metadata (preparation_date);
CREATE INDEX IF NOT EXISTS idx_training_source_file ON training_metadata (source_file);

CREATE INDEX IF NOT EXISTS idx_evaluation_date ON evaluation_results (evaluation_date);
CREATE INDEX IF NOT EXISTS idx_evaluation_model_name ON evaluation_results (model_name);

CREATE INDEX IF NOT EXISTS idx_analysis_results_date ON analysis_results (analysis_date);
CREATE INDEX IF NOT EXISTS idx_analysis_results_provider ON analysis_results (provider);
CREATE INDEX IF NOT EXISTS idx_analysis_results_total_tweets ON analysis_results (total_tweets);
"""

# =============================================================================
# CHATBOT SAV SCHEMA - Schémas pour le chatbot SAV intelligent
# =============================================================================

CHATBOT_SCHEMA = """
-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table conversations - Conversations du chatbot
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_id VARCHAR(100),
    session_id VARCHAR(100) NOT NULL,
    title VARCHAR(200),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,

    -- Configuration LLM
    llm_provider VARCHAR(50) DEFAULT 'mistral',

    -- Statistiques
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    user_satisfaction INTEGER CHECK (user_satisfaction >= 1 AND user_satisfaction <= 5)
);

-- Table messages - Messages individuels dans les conversations
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL CHECK (length(content) > 0 AND length(content) <= 4000),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Métadonnées pour les réponses de l'assistant
    sources JSON DEFAULT '[]',
    llm_provider VARCHAR(50),
    processing_time REAL CHECK (processing_time >= 0.0)
);

-- Table base de connaissances - Documents SAV Free Mobile
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL CHECK (length(title) > 0),
    content TEXT NOT NULL CHECK (length(content) >= 10),
    document_type VARCHAR(50) NOT NULL DEFAULT 'general' CHECK (document_type IN ('faq', 'guide', 'procedure', 'troubleshooting', 'general')),

    -- Métadonnées source
    source_url TEXT NOT NULL,
    source_domain VARCHAR(200) NOT NULL,

    -- Métadonnées de traitement
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content_hash VARCHAR(64) NOT NULL CHECK (length(content_hash) = 64),

    -- Embeddings pour recherche sémantique
    embedding_model VARCHAR(100),
    embedding_dimension INTEGER CHECK (embedding_dimension >= 1),
    embedding_vector VECTOR, -- Nécessite l'extension pgvector pour PostgreSQL

    -- Métadonnées d'utilisation
    usage_count INTEGER DEFAULT 0 CHECK (usage_count >= 0),
    relevance_score REAL DEFAULT 0.0 CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),

    -- Contraintes d'unicité
    UNIQUE(content_hash),
    UNIQUE(source_url)
);

-- Table feedback - Feedback utilisateur sur les réponses
CREATE TABLE IF NOT EXISTS chat_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL CHECK (feedback_type IN ('thumbs_up', 'thumbs_down', 'report_issue', 'suggestion')),

    -- Détails du feedback
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT CHECK (length(comment) <= 1000),

    -- Métadonnées
    user_id VARCHAR(100),
    session_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Informations techniques pour amélioration
    llm_provider_used VARCHAR(50),
    sources_used JSON DEFAULT '[]',
    response_time REAL CHECK (response_time >= 0.0)
);

-- Index pour optimiser les performances du chatbot
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations (session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations (user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations (status);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations (created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_last_message_at ON conversations (last_message_at);

CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id ON chat_messages (conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_role ON chat_messages (role);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages (timestamp);

CREATE INDEX IF NOT EXISTS idx_knowledge_documents_document_type ON knowledge_documents (document_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_source_domain ON knowledge_documents (source_domain);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_scraped_at ON knowledge_documents (scraped_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_last_updated ON knowledge_documents (last_updated);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_usage_count ON knowledge_documents (usage_count);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_relevance_score ON knowledge_documents (relevance_score);

-- Index pour recherche full-text sur le contenu des documents
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_content_fts ON knowledge_documents USING GIN (to_tsvector('french', content));
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_title_fts ON knowledge_documents USING GIN (to_tsvector('french', title));

-- Index pour recherche vectorielle (nécessite pgvector)
-- CREATE INDEX IF NOT EXISTS idx_knowledge_documents_embedding_vector ON knowledge_documents USING ivfflat (embedding_vector vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_chat_feedback_conversation_id ON chat_feedback (conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_message_id ON chat_feedback (message_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_feedback_type ON chat_feedback (feedback_type);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_created_at ON chat_feedback (created_at);
"""
