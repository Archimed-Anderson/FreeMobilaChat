-- Script pour recréer les tables du chatbot avec les bons types
-- Supprimer les tables existantes (dans l'ordre inverse des dépendances)
DROP TABLE IF EXISTS chat_feedback CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;

-- Recréer la table conversations avec id TEXT
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    user_id VARCHAR(100),
    session_id VARCHAR(100) NOT NULL,
    title VARCHAR(200),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,

    -- Configuration LLM utilisée
    llm_provider VARCHAR(50) NOT NULL DEFAULT 'mistral',

    -- Statistiques
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    user_satisfaction INTEGER CHECK (user_satisfaction >= 1 AND user_satisfaction <= 5)
);

-- Recréer la table chat_messages avec conversation_id TEXT
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL CHECK (length(content) > 0 AND length(content) <= 4000),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Métadonnées pour les réponses de l'assistant
    sources JSON DEFAULT '[]',
    llm_provider VARCHAR(50),
    processing_time REAL CHECK (processing_time >= 0.0)
);

-- Recréer la table chat_feedback avec conversation_id TEXT
CREATE TABLE chat_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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

-- Recréer les index
CREATE INDEX idx_conversations_session_id ON conversations (session_id);
CREATE INDEX idx_conversations_user_id ON conversations (user_id);
CREATE INDEX idx_conversations_status ON conversations (status);
CREATE INDEX idx_conversations_created_at ON conversations (created_at);
CREATE INDEX idx_conversations_last_message_at ON conversations (last_message_at);

CREATE INDEX idx_chat_messages_conversation_id ON chat_messages (conversation_id);
CREATE INDEX idx_chat_messages_role ON chat_messages (role);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages (timestamp);

CREATE INDEX idx_chat_feedback_conversation_id ON chat_feedback (conversation_id);
CREATE INDEX idx_chat_feedback_message_id ON chat_feedback (message_id);
CREATE INDEX idx_chat_feedback_feedback_type ON chat_feedback (feedback_type);
CREATE INDEX idx_chat_feedback_created_at ON chat_feedback (created_at);

