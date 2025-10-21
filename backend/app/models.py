"""
Pydantic models for tweet analysis platform
Robust data structures with validation and typing
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, UTC
from typing import Optional, List, Literal, Dict, Tuple, Union, Any
from enum import Enum

class SentimentType(str, Enum):
    """Sentiment classification for tweets"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"

class PriorityLevel(str, Enum):
    """Priority levels for customer service response"""
    CRITICAL = "critique"      # Panne majeure, service down
    HIGH = "haute"             # Problème urgent
    MEDIUM = "moyenne"         # Demande standard
    LOW = "basse"              # Question simple

class CategoryType(str, Enum):
    """Tweet categorization for customer service"""
    BILLING = "facturation"
    NETWORK = "réseau"
    TECHNICAL = "technique"
    SUBSCRIPTION = "abonnement"
    COMPLAINT = "réclamation"
    PRAISE = "compliment"
    QUESTION = "question"
    OTHER = "autre"

class UserRole(str, Enum):
    """User roles for dashboard access control"""
    AGENT = "agent_sav"
    MANAGER = "manager"
    ANALYST = "analyste"
    ADMIN = "admin"

class TweetRaw(BaseModel):
    """Tweet brut depuis CSV - Raw tweet data from CSV import"""
    tweet_id: str
    author: str
    text: str
    date: datetime
    retweet_count: int = 0
    favorite_count: int = 0
    
    @field_validator('text')
    @classmethod
    def clean_text(cls, v: str) -> str:
        """Basic text cleaning and validation"""
        if not v or not v.strip():
            raise ValueError("Tweet text cannot be empty")
        return v.strip()
    
    @field_validator('tweet_id')
    @classmethod
    def validate_tweet_id(cls, v: str) -> str:
        """Validate tweet ID format"""
        if not v or not v.strip():
            raise ValueError("Tweet ID cannot be empty")
        return v.strip()

class TweetAnalyzed(BaseModel):
    """Tweet après analyse LLM - Tweet after LLM analysis"""
    # Données originales - Original data
    tweet_id: str
    author: str
    text: str
    date: datetime
    
    # Métadonnées extraites - Extracted metadata
    mentions: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    urls: List[str] = Field(default_factory=list)
    
    # Analyse LLM - LLM Analysis results
    sentiment: SentimentType
    sentiment_score: float = Field(ge=-1.0, le=1.0, description="Sentiment score from -1 to +1")
    category: CategoryType
    priority: PriorityLevel
    keywords: List[str] = Field(default_factory=list)
    
    # Enrichissement - Enrichment data
    is_urgent: bool = False
    needs_response: bool = True
    estimated_resolution_time: Optional[int] = Field(None, description="Estimated resolution time in minutes")
    
    # Timestamps
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    @field_validator('sentiment_score')
    @classmethod
    def validate_sentiment_score(cls, v: float) -> float:
        """Ensure sentiment score is within valid range"""
        if not -1.0 <= v <= 1.0:
            raise ValueError("Sentiment score must be between -1.0 and 1.0")
        return v
    
    @field_validator('estimated_resolution_time')
    @classmethod
    def validate_resolution_time(cls, v: Optional[int]) -> Optional[int]:
        """Validate resolution time is positive"""
        if v is not None and v < 0:
            raise ValueError("Resolution time must be positive")
        return v

class KPIMetrics(BaseModel):
    """Métriques agrégées pour dashboard - Aggregated metrics for dashboard"""
    total_tweets: int = Field(ge=0, description="Total number of tweets analyzed")
    date_range: Tuple[datetime, datetime] = Field(description="Date range of analyzed tweets")

    # Sentiment distribution
    sentiment_distribution: Dict[SentimentType, int] = Field(default_factory=dict)
    sentiment_percentages: Dict[SentimentType, float] = Field(default_factory=dict)

    # Category distribution
    category_distribution: Dict[CategoryType, int] = Field(default_factory=dict)
    
    # Priority metrics
    critical_count: int = Field(ge=0, description="Number of critical priority tweets")
    high_priority_count: int = Field(ge=0, description="Number of high priority tweets")
    avg_priority_score: float = Field(ge=0.0, description="Average priority score")
    
    # Response metrics
    tweets_needing_response: int = Field(ge=0, description="Tweets requiring response")
    avg_estimated_resolution: float = Field(ge=0.0, description="Average resolution time in minutes")
    
    # Temporal analysis
    tweets_per_hour: Dict[int, int] = Field(default_factory=dict)
    peak_hour: int = Field(ge=0, le=23, description="Hour with most tweet activity")

    @field_validator('date_range')
    @classmethod
    def validate_date_range(cls, v: Tuple[datetime, datetime]) -> Tuple[datetime, datetime]:
        """Ensure date range is valid"""
        start_date, end_date = v
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
        return v
    
    @field_validator('sentiment_percentages')
    @classmethod
    def validate_percentages(cls, v: Dict[SentimentType, float]) -> Dict[SentimentType, float]:
        """Ensure percentages are valid"""
        for sentiment, percentage in v.items():
            if not 0.0 <= percentage <= 100.0:
                raise ValueError(f"Percentage for {sentiment} must be between 0 and 100")
        return v

class DashboardView(BaseModel):
    """Configuration vue par rôle utilisateur - Dashboard view configuration by user role"""
    role: UserRole
    visible_metrics: List[str] = Field(default_factory=list)
    can_export: bool = False
    can_filter_all: bool = False
    
    @field_validator('visible_metrics')
    @classmethod
    def validate_metrics(cls, v: List[str]) -> List[str]:
        """Validate metric names"""
        valid_metrics = [
            'total_tweets', 'sentiment_distribution', 'category_distribution',
            'priority_metrics', 'response_metrics', 'temporal_analysis'
        ]
        for metric in v:
            if metric not in valid_metrics:
                raise ValueError(f"Invalid metric: {metric}")
        return v

# Configuration par défaut pour chaque rôle - Default configuration for each role
DEFAULT_DASHBOARD_CONFIGS = {
    UserRole.AGENT: DashboardView(
        role=UserRole.AGENT,
        visible_metrics=['total_tweets', 'priority_metrics', 'response_metrics'],
        can_export=False,
        can_filter_all=False
    ),
    UserRole.MANAGER: DashboardView(
        role=UserRole.MANAGER,
        visible_metrics=['total_tweets', 'sentiment_distribution', 'category_distribution', 'priority_metrics'],
        can_export=True,
        can_filter_all=True
    ),
    UserRole.ANALYST: DashboardView(
        role=UserRole.ANALYST,
        visible_metrics=['total_tweets', 'sentiment_distribution', 'category_distribution', 
                        'priority_metrics', 'response_metrics', 'temporal_analysis'],
        can_export=True,
        can_filter_all=True
    ),
    UserRole.ADMIN: DashboardView(
        role=UserRole.ADMIN,
        visible_metrics=['total_tweets', 'sentiment_distribution', 'category_distribution', 
                        'priority_metrics', 'response_metrics', 'temporal_analysis'],
        can_export=True,
        can_filter_all=True
    )
}

class AnalysisLog(BaseModel):
    """Log d'analyse pour traçabilité - Analysis log for traceability"""
    batch_id: str
    total_tweets: int = Field(ge=0)
    successful_analysis: int = Field(ge=0)
    failed_analysis: int = Field(ge=0)
    llm_provider: str
    total_cost: float = Field(ge=0.0, description="Total cost in USD")
    processing_time: float = Field(ge=0.0, description="Processing time in seconds")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    @field_validator('batch_id')
    @classmethod
    def validate_batch_id(cls, v: str) -> str:
        """Validate batch ID format"""
        if not v or not v.strip():
            raise ValueError("Batch ID cannot be empty")
        return v.strip()

class User(BaseModel):
    """Utilisateur système - System user"""
    id: Optional[int] = None
    username: str = Field(min_length=3, max_length=50)
    role: UserRole
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        # Basic alphanumeric validation
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        return v.strip().lower()

# CHATBOT SAV MODELS - Modèles pour le chatbot SAV intelligent

class MessageRole(str, Enum):
    """Rôles des messages dans une conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """Message individuel dans une conversation chatbot"""
    id: Optional[str] = None
    conversation_id: str
    role: MessageRole
    content: str = Field(min_length=1, max_length=4000, description="Contenu du message")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Métadonnées pour les réponses de l'assistant
    sources: List[str] = Field(default_factory=list, description="Sources utilisées pour générer la réponse")
    llm_provider: Optional[str] = Field(None, description="Fournisseur LLM utilisé")
    processing_time: Optional[float] = Field(None, ge=0.0, description="Temps de traitement en secondes")

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Valider et nettoyer le contenu du message"""
        if not v or not v.strip():
            raise ValueError("Le contenu du message ne peut pas être vide")
        return v.strip()

class ConversationStatus(str, Enum):
    """Statut d'une conversation"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class Conversation(BaseModel):
    """Conversation complète avec un utilisateur"""
    id: Optional[str] = None
    user_id: Optional[str] = Field(None, description="ID utilisateur (optionnel pour sessions anonymes)")
    session_id: str = Field(description="ID de session unique")
    title: Optional[str] = Field(None, max_length=200, description="Titre de la conversation")
    status: ConversationStatus = ConversationStatus.ACTIVE

    # Métadonnées
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_message_at: Optional[datetime] = None

    # Configuration LLM utilisée
    llm_provider: str = Field(default="mistral", description="Fournisseur LLM par défaut")

    # Statistiques
    message_count: int = Field(default=0, ge=0, description="Nombre total de messages")
    user_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="Note de satisfaction (1-5)")

    @field_validator('session_id')
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Valider l'ID de session"""
        if not v or not v.strip():
            raise ValueError("L'ID de session ne peut pas être vide")
        return v.strip()

class DocumentType(str, Enum):
    """Types de documents dans la base de connaissances"""
    FAQ = "faq"
    GUIDE = "guide"
    PROCEDURE = "procedure"
    TROUBLESHOOTING = "troubleshooting"
    GENERAL = "general"
    GRAPHRAG = "graphrag"  # Documents provenant de Fast-GraphRAG

class KnowledgeDocument(BaseModel):
    """Document dans la base de connaissances SAV"""
    id: Optional[str] = None
    title: str = Field(min_length=1, max_length=500, description="Titre du document")
    content: str = Field(min_length=10, description="Contenu textuel du document")
    document_type: DocumentType = DocumentType.GENERAL

    # Métadonnées source
    source_url: str = Field(description="URL source du document")
    source_domain: str = Field(description="Domaine source (ex: assistance.free.fr)")

    # Métadonnées de traitement
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    content_hash: str = Field(description="Hash du contenu pour détecter les changements")

    # Embeddings pour recherche sémantique
    embedding_model: Optional[str] = Field(None, description="Modèle utilisé pour les embeddings")
    embedding_dimension: Optional[int] = Field(None, ge=1, description="Dimension du vecteur d'embedding")

    # Métadonnées d'utilisation
    usage_count: int = Field(default=0, ge=0, description="Nombre de fois utilisé dans les réponses")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score de pertinence moyen")

    @field_validator('content_hash')
    @classmethod
    def validate_content_hash(cls, v: str) -> str:
        """Valider le hash du contenu"""
        if not v or len(v) != 64:  # SHA-256 hash length
            raise ValueError("Hash du contenu invalide (doit être SHA-256)")
        return v.lower()

class FeedbackType(str, Enum):
    """Types de feedback utilisateur"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    REPORT_ISSUE = "report_issue"
    SUGGESTION = "suggestion"

class ChatFeedback(BaseModel):
    """Feedback utilisateur sur les réponses du chatbot"""
    id: Optional[str] = None
    conversation_id: str
    message_id: str = Field(description="ID du message évalué")
    feedback_type: FeedbackType

    # Détails du feedback
    rating: Optional[int] = Field(None, ge=1, le=5, description="Note de 1 à 5")
    comment: Optional[str] = Field(None, max_length=1000, description="Commentaire optionnel")

    # Métadonnées
    user_id: Optional[str] = Field(None, description="ID utilisateur (optionnel)")
    session_id: str = Field(description="ID de session")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Informations techniques pour amélioration
    llm_provider_used: Optional[str] = Field(None, description="Fournisseur LLM utilisé")
    sources_used: List[str] = Field(default_factory=list, description="Sources utilisées")
    response_time: Optional[float] = Field(None, ge=0.0, description="Temps de réponse")

    @field_validator('comment')
    @classmethod
    def validate_comment(cls, v: Optional[str]) -> Optional[str]:
        """Valider et nettoyer le commentaire"""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v
