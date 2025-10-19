-- Script de création des tables pour le Chatbot SAV FreeMobilaChat
-- Modifié pour fonctionner sans l'extension pgvector

-- Table conversations - Conversations du chatbot
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
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
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

    -- Embeddings pour recherche sémantique (stockés en JSON sans pgvector)
    embedding_model VARCHAR(100),
    embedding_dimension INTEGER CHECK (embedding_dimension >= 1),
    embedding_vector TEXT, -- JSON array des embeddings

    -- Métadonnées d'utilisation
    usage_count INTEGER DEFAULT 0 CHECK (usage_count >= 0),
    relevance_score REAL DEFAULT 0.0 CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),

    -- Contraintes d'unicité
    UNIQUE(content_hash),
    UNIQUE(source_url)
);

-- Table feedback - Feedback utilisateur sur les réponses
CREATE TABLE IF NOT EXISTS chat_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_chat_feedback_conversation_id ON chat_feedback (conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_message_id ON chat_feedback (message_id);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_feedback_type ON chat_feedback (feedback_type);
CREATE INDEX IF NOT EXISTS idx_chat_feedback_created_at ON chat_feedback (created_at);
