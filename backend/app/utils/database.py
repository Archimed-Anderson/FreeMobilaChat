"""
Database utilities for tweet analysis platform
Handles database connections, initialization, and operations
"""

import sqlite3
import asyncio
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from contextlib import asynccontextmanager
import os
from urllib.parse import quote_plus

try:
    import aiosqlite
except ImportError:
    aiosqlite = None

try:
    import asyncpg
    import psycopg2
except ImportError:
    asyncpg = None
    psycopg2 = None

from ..models import TweetAnalyzed, AnalysisLog, User
from ..schemas import get_database_schema, get_postgresql_optimizations

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Database manager for tweet analysis platform
    Supports both SQLite and PostgreSQL
    """
    
    def __init__(self, database_type: str = "sqlite", connection_string: str = None):
        """
        Initialize database manager
        
        Args:
            database_type: Type of database ('sqlite' or 'postgresql')
            connection_string: Database connection string
        """
        self.database_type = database_type.lower()
        self.connection_string = connection_string or self._get_default_connection_string()
        self.connection_pool = None
        
        logger.info(f"Database manager initialized: {self.database_type}")
    
    def _get_default_connection_string(self) -> str:
        """Get default connection string based on environment"""
        if self.database_type == "sqlite":
            db_path = os.getenv("SQLITE_DATABASE_PATH", "./data/tweets_analysis.db")
            # Ensure directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            return db_path
        elif self.database_type == "postgresql":
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            db = os.getenv("POSTGRES_DB", "tweets_analysis")
            user = os.getenv("POSTGRES_USER", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "")
            # URL encode the password to handle special characters
            try:
                from urllib.parse import quote_plus
                encoded_password = quote_plus(password)
                return f"postgresql://{user}:{encoded_password}@{host}:{port}/{db}"
            except Exception:
                # Fallback if URL encoding fails
                return f"postgresql://{user}:{password}@{host}:{port}/{db}"
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")
    
    async def initialize_database(self):
        """Initialize database with schema"""
        try:
            logger.info("Initializing database schema")
            
            if self.database_type == "sqlite":
                await self._initialize_sqlite()
            elif self.database_type == "postgresql":
                await self._initialize_postgresql()
            
            logger.info("Database initialization completed")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _initialize_sqlite(self):
        """Initialize SQLite database"""
        if not aiosqlite:
            raise ImportError("aiosqlite is required for SQLite support")
        
        async with aiosqlite.connect(self.connection_string) as db:
            # Execute schema
            schema = get_database_schema()
            await db.executescript(schema)
            await db.commit()
            
            logger.info(f"SQLite database initialized: {self.connection_string}")
    
    async def _initialize_postgresql(self):
        """Initialize PostgreSQL database"""
        if not asyncpg:
            raise ImportError("asyncpg is required for PostgreSQL support")

        conn = await asyncpg.connect(self.connection_string)
        try:
            # Check if tables already exist (init-db.sql should have created them)
            result = await conn.fetchval(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'tweets'"
            )

            if result == 0:
                logger.warning("Tables not found. init-db.sql may not have run properly.")
                # Fallback: create basic tables only
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS tweets (
                        id SERIAL PRIMARY KEY,
                        tweet_id VARCHAR(50) UNIQUE NOT NULL,
                        author VARCHAR(100) NOT NULL,
                        text TEXT NOT NULL,
                        date TIMESTAMP NOT NULL,
                        sentiment VARCHAR(20),
                        category VARCHAR(50),
                        priority VARCHAR(20),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_logs (
                        id SERIAL PRIMARY KEY,
                        batch_id VARCHAR(50) UNIQUE NOT NULL,
                        total_tweets INTEGER NOT NULL,
                        successful_analysis INTEGER NOT NULL,
                        failed_analysis INTEGER NOT NULL,
                        llm_provider VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            else:
                logger.info("Database tables already exist (created by init-db.sql)")

            # Apply PostgreSQL optimizations if available
            try:
                optimizations = get_postgresql_optimizations()
                opt_statements = [stmt.strip() for stmt in optimizations.split(';') if stmt.strip()]

                for statement in opt_statements:
                    if statement:
                        await conn.execute(statement)
            except Exception as e:
                logger.warning(f"Could not apply optimizations: {e}")
            
            logger.info("PostgreSQL database initialized")
            
        finally:
            await conn.close()
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection context manager"""
        if self.database_type == "sqlite":
            async with aiosqlite.connect(self.connection_string) as conn:
                # Enable foreign keys for SQLite
                await conn.execute("PRAGMA foreign_keys = ON")
                yield conn
        elif self.database_type == "postgresql":
            conn = await asyncpg.connect(self.connection_string)
            try:
                yield conn
            finally:
                await conn.close()
    
    async def save_analyzed_tweets(self, tweets: List[TweetAnalyzed], batch_id: str) -> int:
        """
        Save analyzed tweets to database
        
        Args:
            tweets: List of analyzed tweets
            batch_id: Batch identifier
            
        Returns:
            Number of tweets saved
        """
        if not tweets:
            return 0
        
        try:
            async with self.get_connection() as conn:
                saved_count = 0
                
                for tweet in tweets:
                    # Prepare tweet data
                    tweet_data = {
                        'tweet_id': tweet.tweet_id,
                        'author': tweet.author,
                        'text': tweet.text,
                        'date': tweet.date,
                        'mentions': tweet.mentions,
                        'hashtags': tweet.hashtags,
                        'urls': tweet.urls,
                        'sentiment': tweet.sentiment.value,
                        'sentiment_score': tweet.sentiment_score,
                        'category': tweet.category.value,
                        'priority': tweet.priority.value,
                        'keywords': tweet.keywords,
                        'is_urgent': tweet.is_urgent,
                        'needs_response': tweet.needs_response,
                        'estimated_resolution_time': tweet.estimated_resolution_time,
                        'analyzed_at': tweet.analyzed_at
                    }
                    
                    # Insert tweet
                    if self.database_type == "sqlite":
                        await self._insert_tweet_sqlite(conn, tweet_data)
                    elif self.database_type == "postgresql":
                        await self._insert_tweet_postgresql(conn, tweet_data)
                    
                    saved_count += 1
                
                logger.info(f"Saved {saved_count} tweets to database")
                return saved_count
                
        except Exception as e:
            logger.error(f"Error saving tweets: {e}")
            raise
    
    async def _insert_tweet_sqlite(self, conn, tweet_data: Dict[str, Any]):
        """Insert tweet into SQLite database"""
        import json
        
        query = """
        INSERT OR REPLACE INTO tweets (
            tweet_id, author, text, date, mentions, hashtags, urls,
            sentiment, sentiment_score, category, priority, keywords,
            is_urgent, needs_response, estimated_resolution_time, analyzed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            tweet_data['tweet_id'],
            tweet_data['author'],
            tweet_data['text'],
            tweet_data['date'],
            json.dumps(tweet_data['mentions']),
            json.dumps(tweet_data['hashtags']),
            json.dumps(tweet_data['urls']),
            tweet_data['sentiment'],
            tweet_data['sentiment_score'],
            tweet_data['category'],
            tweet_data['priority'],
            json.dumps(tweet_data['keywords']),
            tweet_data['is_urgent'],
            tweet_data['needs_response'],
            tweet_data['estimated_resolution_time'],
            tweet_data['analyzed_at']
        )
        
        await conn.execute(query, values)
        await conn.commit()
    
    async def _insert_tweet_postgresql(self, conn, tweet_data: Dict[str, Any]):
        """Insert tweet into PostgreSQL database"""
        query = """
        INSERT INTO tweets (
            tweet_id, author, text, date, mentions, hashtags, urls,
            sentiment, sentiment_score, category, priority, keywords,
            is_urgent, needs_response, estimated_resolution_time, analyzed_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
        ON CONFLICT (tweet_id) DO UPDATE SET
            sentiment = EXCLUDED.sentiment,
            sentiment_score = EXCLUDED.sentiment_score,
            category = EXCLUDED.category,
            priority = EXCLUDED.priority,
            keywords = EXCLUDED.keywords,
            is_urgent = EXCLUDED.is_urgent,
            needs_response = EXCLUDED.needs_response,
            estimated_resolution_time = EXCLUDED.estimated_resolution_time,
            analyzed_at = EXCLUDED.analyzed_at
        """
        
        await conn.execute(
            query,
            tweet_data['tweet_id'],
            tweet_data['author'],
            tweet_data['text'],
            tweet_data['date'],
            tweet_data['mentions'],
            tweet_data['hashtags'],
            tweet_data['urls'],
            tweet_data['sentiment'],
            tweet_data['sentiment_score'],
            tweet_data['category'],
            tweet_data['priority'],
            tweet_data['keywords'],
            tweet_data['is_urgent'],
            tweet_data['needs_response'],
            tweet_data['estimated_resolution_time'],
            tweet_data['analyzed_at']
        )
    
    async def get_tweets_by_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        """
        Get tweets for a specific batch

        Args:
            batch_id: Batch identifier

        Returns:
            List of tweet dictionaries for the batch
        """
        try:
            async with self.get_connection() as conn:
                # We need to join with analysis_logs to get batch_id
                # For now, we'll use a workaround by storing batch_id in tweet metadata
                # In a proper implementation, we'd have a batch_tweets table

                # Get analysis log first to verify batch exists
                logs = await self.get_analysis_logs(limit=100)
                batch_log = next((log for log in logs if log.get('batch_id') == batch_id), None)

                if not batch_log:
                    return []

                # For now, return tweets analyzed around the same time as the batch
                # This is a temporary solution - in production, you'd have proper batch tracking
                query = """
                SELECT * FROM tweets
                WHERE analyzed_at >= ? AND analyzed_at <= ?
                ORDER BY analyzed_at DESC
                """

                # Get tweets within a time window around the batch creation
                from datetime import datetime, timedelta
                batch_time = batch_log.get('created_at')
                if isinstance(batch_time, str):
                    batch_time = datetime.fromisoformat(batch_time.replace('Z', '+00:00'))

                start_time = batch_time - timedelta(minutes=5)
                end_time = batch_time + timedelta(hours=1)

                if self.database_type == "sqlite":
                    cursor = await conn.execute(query, (start_time.isoformat(), end_time.isoformat()))
                    rows = await cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]

                elif self.database_type == "postgresql":
                    rows = await conn.fetch(query.replace('?', '$1').replace('?', '$2'), start_time, end_time)
                    return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting tweets by batch: {e}")
            return []

    async def get_tweets(self,
                        limit: int = 100,
                        offset: int = 0,
                        filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get tweets from database with filtering
        
        Args:
            limit: Maximum number of tweets
            offset: Number of tweets to skip
            filters: Filter criteria
            
        Returns:
            List of tweet dictionaries
        """
        try:
            async with self.get_connection() as conn:
                # Build query
                query = "SELECT * FROM tweets WHERE 1=1"
                params = []
                
                if filters:
                    if 'sentiment' in filters:
                        query += " AND sentiment = ?"
                        params.append(filters['sentiment'])
                    
                    if 'category' in filters:
                        query += " AND category = ?"
                        params.append(filters['category'])
                    
                    if 'priority' in filters:
                        query += " AND priority = ?"
                        params.append(filters['priority'])
                    
                    if 'urgent_only' in filters and filters['urgent_only']:
                        query += " AND is_urgent = 1"
                
                query += " ORDER BY date DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                if self.database_type == "sqlite":
                    cursor = await conn.execute(query, params)
                    rows = await cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
                
                elif self.database_type == "postgresql":
                    # Convert ? to $1, $2, etc. for PostgreSQL
                    pg_query = query
                    for i, _ in enumerate(params, 1):
                        pg_query = pg_query.replace('?', f'${i}', 1)
                    
                    rows = await conn.fetch(pg_query, *params)
                    return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting tweets: {e}")
            raise
    
    async def save_analysis_log(self, log: AnalysisLog) -> bool:
        """
        Save analysis log to database
        
        Args:
            log: Analysis log to save
            
        Returns:
            True if successful
        """
        try:
            async with self.get_connection() as conn:
                query = """
                INSERT INTO analysis_logs (
                    batch_id, total_tweets, successful_analysis, failed_analysis,
                    llm_provider, total_cost, processing_time, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    log.batch_id,
                    log.total_tweets,
                    log.successful_analysis,
                    log.failed_analysis,
                    log.llm_provider,
                    log.total_cost,
                    log.processing_time,
                    log.created_at
                )
                
                if self.database_type == "sqlite":
                    await conn.execute(query, values)
                    await conn.commit()
                elif self.database_type == "postgresql":
                    pg_query = query.replace('?', '${}')
                    pg_query = pg_query.format(*range(1, len(values) + 1))
                    await conn.execute(pg_query, *values)
                
                return True
                
        except Exception as e:
            logger.error(f"Error saving analysis log: {e}")
            return False
    
    async def get_analysis_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get analysis logs from database"""
        try:
            async with self.get_connection() as conn:
                query = "SELECT * FROM analysis_logs ORDER BY created_at DESC LIMIT ?"
                
                if self.database_type == "sqlite":
                    cursor = await conn.execute(query, (limit,))
                    rows = await cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
                
                elif self.database_type == "postgresql":
                    rows = await conn.fetch(query.replace('?', '$1'), limit)
                    return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting analysis logs: {e}")
            return []
    
    async def delete_analysis(self, batch_id: str) -> int:
        """
        Delete analysis results for a specific batch

        Args:
            batch_id: Batch identifier

        Returns:
            Number of records deleted
        """
        try:
            async with self.get_connection() as conn:
                deleted_count = 0

                # Get analysis log to find the time range for tweets
                logs = await self.get_analysis_logs(limit=100)
                batch_log = next((log for log in logs if log.get('batch_id') == batch_id), None)

                if batch_log:
                    # Delete tweets within the batch time range
                    from datetime import datetime, timedelta
                    batch_time = batch_log.get('created_at')
                    if isinstance(batch_time, str):
                        batch_time = datetime.fromisoformat(batch_time.replace('Z', '+00:00'))

                    start_time = batch_time - timedelta(minutes=5)
                    end_time = batch_time + timedelta(hours=1)

                    if self.database_type == "sqlite":
                        # Delete tweets
                        cursor = await conn.execute(
                            "DELETE FROM tweets WHERE analyzed_at >= ? AND analyzed_at <= ?",
                            (start_time.isoformat(), end_time.isoformat())
                        )
                        deleted_count = cursor.rowcount

                        # Delete analysis log
                        await conn.execute("DELETE FROM analysis_logs WHERE batch_id = ?", (batch_id,))
                        await conn.commit()

                    elif self.database_type == "postgresql":
                        # Delete tweets
                        result = await conn.execute(
                            "DELETE FROM tweets WHERE analyzed_at >= $1 AND analyzed_at <= $2",
                            start_time, end_time
                        )
                        deleted_count = int(result.split()[-1]) if result else 0

                        # Delete analysis log
                        await conn.execute("DELETE FROM analysis_logs WHERE batch_id = $1", batch_id)

                logger.info(f"Deleted analysis {batch_id}: {deleted_count} tweets")
                return deleted_count

        except Exception as e:
            logger.error(f"Error deleting analysis {batch_id}: {e}")
            return 0

    async def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """
        Clean up old data from database

        Args:
            days_to_keep: Number of days to keep

        Returns:
            Number of records deleted
        """
        try:
            async with self.get_connection() as conn:
                # Delete old tweets
                query = "DELETE FROM tweets WHERE created_at < datetime('now', '-{} days')".format(days_to_keep)

                if self.database_type == "sqlite":
                    cursor = await conn.execute(query)
                    deleted_count = cursor.rowcount
                    await conn.commit()
                elif self.database_type == "postgresql":
                    result = await conn.execute(query)
                    deleted_count = int(result.split()[-1])

                logger.info(f"Cleaned up {deleted_count} old records")
                return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0

    async def store_training_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Store training metadata in database

        Args:
            metadata: Training metadata dictionary

        Returns:
            Success status
        """
        try:
            if self.database_type == "postgresql":
                async with self.connection_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO training_metadata
                        (preparation_date, source_file, total_samples, train_samples,
                         val_samples, test_samples, file_paths, statistics)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    metadata['preparation_date'],
                    metadata['source_file'],
                    metadata['total_samples'],
                    metadata['train_samples'],
                    metadata['val_samples'],
                    metadata['test_samples'],
                    json.dumps(metadata['file_paths']),
                    json.dumps(metadata['statistics'])
                    )
            else:
                async with aiosqlite.connect(self.connection_string) as conn:
                    await conn.execute("""
                        INSERT INTO training_metadata
                        (preparation_date, source_file, total_samples, train_samples,
                         val_samples, test_samples, file_paths, statistics)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metadata['preparation_date'].isoformat(),
                        metadata['source_file'],
                        metadata['total_samples'],
                        metadata['train_samples'],
                        metadata['val_samples'],
                        metadata['test_samples'],
                        json.dumps(metadata['file_paths']),
                        json.dumps(metadata['statistics'])
                    ))
                    await conn.commit()

            logger.info("Training metadata stored successfully")
            return True

        except Exception as e:
            logger.error(f"Error storing training metadata: {e}")
            return False

    async def store_evaluation_results(self, results: Dict[str, Any]) -> bool:
        """
        Store evaluation results in database

        Args:
            results: Evaluation results dictionary

        Returns:
            Success status
        """
        try:
            if self.database_type == "postgresql":
                async with self.connection_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO evaluation_results
                        (evaluation_date, model_name, test_samples, metrics, files)
                        VALUES ($1, $2, $3, $4, $5)
                    """,
                    results['evaluation_date'],
                    results['model_name'],
                    results['test_samples'],
                    json.dumps(results['metrics']),
                    json.dumps(results['files'])
                    )
            else:
                async with aiosqlite.connect(self.connection_string) as conn:
                    await conn.execute("""
                        INSERT INTO evaluation_results
                        (evaluation_date, model_name, test_samples, metrics, files)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        results['evaluation_date'].isoformat(),
                        results['model_name'],
                        results['test_samples'],
                        json.dumps(results['metrics']),
                        json.dumps(results['files'])
                    ))
                    await conn.commit()

            logger.info("Evaluation results stored successfully")
            return True

        except Exception as e:
            logger.error(f"Error storing evaluation results: {e}")
            return False

    async def store_analysis_results(self, results: Dict[str, Any]) -> bool:
        """
        Store comprehensive analysis results in database

        Args:
            results: Analysis results dictionary

        Returns:
            Success status
        """
        try:
            if self.database_type == "postgresql":
                async with self.connection_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO analysis_results
                        (analysis_date, provider, total_tweets, analysis_summary,
                         kpi_metrics, insights_and_recommendations)
                        VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    results['analysis_date'],
                    results['provider'],
                    results['total_tweets'],
                    json.dumps(results['analysis_summary']),
                    json.dumps(results['kpi_metrics']),
                    json.dumps(results['insights_and_recommendations'])
                    )
            else:
                async with aiosqlite.connect(self.connection_string) as conn:
                    await conn.execute("""
                        INSERT INTO analysis_results
                        (analysis_date, provider, total_tweets, analysis_summary,
                         kpi_metrics, insights_and_recommendations)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        results['analysis_date'],
                        results['provider'],
                        results['total_tweets'],
                        json.dumps(results['analysis_summary']),
                        json.dumps(results['kpi_metrics']),
                        json.dumps(results['insights_and_recommendations'])
                    ))
                    await conn.commit()

            logger.info("Analysis results stored successfully")
            return True

        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
            return False

    
    # CHATBOT SAV METHODS - Méthodes pour le chatbot SAV intelligent
    

    async def store_knowledge_document(self, document: Dict[str, Any]) -> Optional[str]:
        """
        Store a knowledge document in the database

        Args:
            document: Document data dictionary

        Returns:
            Document ID if successful, None otherwise
        """
        try:
            if self.database_type == "postgresql":
                async with self.get_connection() as conn:
                    # Insert document and return the generated ID
                    result = await conn.fetchrow("""
                        INSERT INTO knowledge_documents
                        (title, content, document_type, source_url, source_domain,
                         content_hash, embedding_model, embedding_dimension,
                         embedding_vector, usage_count, relevance_score)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        RETURNING id
                    """,
                    document['title'],
                    document['content'],
                    document.get('document_type', 'general'),
                    document['source_url'],
                    document['source_domain'],
                    document['content_hash'],
                    document.get('embedding_model'),
                    document.get('embedding_dimension'),
                    document.get('embedding_vector'),  # JSON string
                    document.get('usage_count', 0),
                    document.get('relevance_score', 0.0)
                    )

                    document_id = str(result['id'])
                    logger.info(f"Knowledge document stored: {document_id}")
                    return document_id

            else:
                logger.warning("Knowledge document storage not implemented for SQLite")
                return None

        except Exception as e:
            logger.error(f"Error storing knowledge document: {e}")
            return None

    async def search_documents_by_embedding(self, query_embedding: List[float],
                                          limit: int = 5,
                                          similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Search documents by embedding similarity

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score

        Returns:
            List of matching documents with similarity scores
        """
        try:
            if self.database_type == "postgresql":
                async with self.get_connection() as conn:
                    # For now, return documents without similarity calculation
                    # since we don't have pgvector. We'll use full-text search instead
                    rows = await conn.fetch("""
                        SELECT id, title, content, document_type, source_url, source_domain,
                               content_hash, usage_count, relevance_score, embedding_vector
                        FROM knowledge_documents
                        ORDER BY relevance_score DESC, usage_count DESC
                        LIMIT $1
                    """, limit)

                    documents = []
                    for row in rows:
                        doc = dict(row)
                        # For now, assign a default similarity score
                        doc['similarity_score'] = 0.8  # Placeholder
                        documents.append(doc)

                    logger.info(f"Found {len(documents)} documents")
                    return documents

            else:
                logger.warning("Document search not implemented for SQLite")
                return []

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    async def store_conversation(self, conversation: Dict[str, Any]) -> Optional[str]:
        """
        Store a conversation in the database

        Args:
            conversation: Conversation data dictionary

        Returns:
            Conversation ID if successful, None otherwise
        """
        try:
            if self.database_type == "postgresql":
                async with self.get_connection() as conn:
                    result = await conn.fetchrow("""
                        INSERT INTO conversations
                        (user_id, session_id, title, status, llm_provider, message_count)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        RETURNING id
                    """,
                    conversation.get('user_id'),
                    conversation['session_id'],
                    conversation.get('title'),
                    conversation.get('status', 'active'),
                    conversation.get('llm_provider', 'mistral'),
                    conversation.get('message_count', 0)
                    )

                    conversation_id = str(result['id'])
                    logger.info(f"Conversation stored: {conversation_id}")
                    return conversation_id

            else:
                logger.warning("Conversation storage not implemented for SQLite")
                return None

        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            return None

    async def store_conversation_with_id(self, conversation: Dict[str, Any]) -> Optional[str]:
        """
        Store a conversation with a specific ID (for custom conversation IDs)

        Args:
            conversation: Conversation data dictionary with 'id' field

        Returns:
            Conversation ID if successful, None otherwise
        """
        try:
            if self.database_type == "postgresql":
                async with self.get_connection() as conn:
                    # Use INSERT ... ON CONFLICT DO NOTHING to avoid duplicates
                    result = await conn.fetchrow("""
                        INSERT INTO conversations
                        (id, user_id, session_id, title, status, llm_provider, message_count)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (id) DO NOTHING
                        RETURNING id
                    """,
                    conversation['id'],
                    conversation.get('user_id'),
                    conversation['session_id'],
                    conversation.get('title'),
                    conversation.get('status', 'active'),
                    conversation.get('llm_provider', 'mistral'),
                    conversation.get('message_count', 0)
                    )

                    if result:
                        conversation_id = str(result['id'])
                        logger.info(f"Conversation stored with custom ID: {conversation_id}")
                        return conversation_id
                    else:
                        # Conversation already exists
                        logger.info(f"Conversation already exists: {conversation['id']}")
                        return conversation['id']

            else:
                logger.warning("Conversation storage not implemented for SQLite")
                return None

        except Exception as e:
            logger.error(f"Error storing conversation with ID: {e}")
            return None

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation data if found, None otherwise
        """
        try:
            if self.database_type == "postgresql":
                async with self.get_connection() as conn:
                    row = await conn.fetchrow("""
                        SELECT id, user_id, session_id, title, status, created_at,
                               updated_at, last_message_at, llm_provider, message_count,
                               user_satisfaction
                        FROM conversations
                        WHERE id = $1
                    """, conversation_id)

                    if row:
                        conversation = dict(row)
                        logger.info(f"Conversation retrieved: {conversation_id}")
                        return conversation
                    else:
                        logger.warning(f"Conversation not found: {conversation_id}")
                        return None

            else:
                logger.warning("Conversation retrieval not implemented for SQLite")
                return None

        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None

    async def store_message(self, message: Dict[str, Any]) -> Optional[str]:
        """
        Store a chat message in the database

        Args:
            message: Message data dictionary

        Returns:
            Message ID if successful, None otherwise
        """
        try:
            if self.database_type == "postgresql":
                async with self.get_connection() as conn:
                    result = await conn.fetchrow("""
                        INSERT INTO chat_messages
                        (conversation_id, role, content, sources, llm_provider, processing_time)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        RETURNING id
                    """,
                    message['conversation_id'],
                    message['role'],
                    message['content'],
                    json.dumps(message.get('sources', [])),
                    message.get('llm_provider'),
                    message.get('processing_time')
                    )

                    message_id = str(result['id'])

                    # Update conversation message count and last_message_at
                    await conn.execute("""
                        UPDATE conversations
                        SET message_count = message_count + 1,
                            last_message_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = $1
                    """, message['conversation_id'])

                    logger.info(f"Message stored: {message_id}")
                    return message_id

            else:
                logger.warning("Message storage not implemented for SQLite")
                return None

        except Exception as e:
            logger.error(f"Error storing message: {e}")
            return None

    async def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages ordered by timestamp
        """
        try:
            if self.database_type == "postgresql":
                async with self.get_connection() as conn:
                    rows = await conn.fetch("""
                        SELECT id, conversation_id, role, content, timestamp,
                               sources, llm_provider, processing_time
                        FROM chat_messages
                        WHERE conversation_id = $1
                        ORDER BY timestamp ASC
                        LIMIT $2
                    """, conversation_id, limit)

                    messages = []
                    for row in rows:
                        message = dict(row)
                        # Parse JSON sources
                        if message['sources']:
                            try:
                                message['sources'] = json.loads(message['sources'])
                            except:
                                message['sources'] = []
                        else:
                            message['sources'] = []
                        messages.append(message)

                    logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
                    return messages

            else:
                logger.warning("Message retrieval not implemented for SQLite")
                return []

        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []

    async def store_feedback(self, feedback: Dict[str, Any]) -> Optional[str]:
        """
        Store user feedback in the database

        Args:
            feedback: Feedback data dictionary

        Returns:
            Feedback ID if successful, None otherwise
        """
        try:
            if self.database_type == "postgresql":
                async with self.get_connection() as conn:
                    result = await conn.fetchrow("""
                        INSERT INTO chat_feedback
                        (conversation_id, message_id, feedback_type, rating, comment,
                         user_id, session_id, llm_provider_used, sources_used, response_time)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        RETURNING id
                    """,
                    feedback['conversation_id'],
                    feedback['message_id'],
                    feedback['feedback_type'],
                    feedback.get('rating'),
                    feedback.get('comment'),
                    feedback.get('user_id'),
                    feedback['session_id'],
                    feedback.get('llm_provider_used'),
                    json.dumps(feedback.get('sources_used', [])),
                    feedback.get('response_time')
                    )

                    feedback_id = str(result['id'])
                    logger.info(f"Feedback stored: {feedback_id}")
                    return feedback_id

            else:
                logger.warning("Feedback storage not implemented for SQLite")
                return None

        except Exception as e:
            logger.error(f"Error storing feedback: {e}")
            return None

    async def get_conversations_by_user(self, user_id: str = None, session_id: str = None,
                                      limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get conversations for a user or session

        Args:
            user_id: User ID (optional)
            session_id: Session ID (optional)
            limit: Maximum number of conversations

        Returns:
            List of conversations
        """
        try:
            if self.database_type == "postgresql":
                async with self.get_connection() as conn:
                    if user_id:
                        rows = await conn.fetch("""
                            SELECT id, user_id, session_id, title, status, created_at,
                                   last_message_at, llm_provider, message_count
                            FROM conversations
                            WHERE user_id = $1
                            ORDER BY last_message_at DESC NULLS LAST, created_at DESC
                            LIMIT $2
                        """, user_id, limit)
                    elif session_id:
                        rows = await conn.fetch("""
                            SELECT id, user_id, session_id, title, status, created_at,
                                   last_message_at, llm_provider, message_count
                            FROM conversations
                            WHERE session_id = $1
                            ORDER BY last_message_at DESC NULLS LAST, created_at DESC
                            LIMIT $2
                        """, session_id, limit)
                    else:
                        logger.warning("Either user_id or session_id must be provided")
                        return []

                    conversations = [dict(row) for row in rows]
                    logger.info(f"Retrieved {len(conversations)} conversations")
                    return conversations

            else:
                logger.warning("Conversation retrieval not implemented for SQLite")
                return []

        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return []

# Global database manager instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    
    if _db_manager is None:
        db_type = os.getenv("DATABASE_TYPE", "sqlite")
        connection_string = os.getenv("DATABASE_URL")
        _db_manager = DatabaseManager(db_type, connection_string)
    
    return _db_manager
