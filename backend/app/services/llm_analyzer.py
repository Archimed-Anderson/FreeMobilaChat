"""
LLM Analyzer for tweet sentiment and classification
Supports OpenAI, Mistral, and Anthropic APIs with rate limiting
"""

import asyncio
import json
import os
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
import logging
from enum import Enum
import httpx

# LLM Client imports
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    from mistralai import Mistral
    MistralAsyncClient = Mistral
except ImportError:
    MistralAsyncClient = None

from ..models import TweetRaw, TweetAnalyzed, SentimentType, CategoryType, PriorityLevel
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    MISTRAL = "mistral"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"

class LLMAnalyzer:
    """
    Analyseur LLM avec rate limiting
    LLM analyzer with rate limiting and multi-provider support
    """
    
    def __init__(self, 
                 provider: str = "openai", 
                 batch_size: int = 10,
                 max_concurrent: int = 5,
                 rate_limit_per_minute: int = 30):
        """
        Initialize LLM analyzer
        
        Args:
            provider: LLM provider to use
            batch_size: Number of tweets per batch
            max_concurrent: Maximum concurrent requests
            rate_limit_per_minute: Rate limit for API calls
        """
        self.provider = LLMProvider(provider)
        logger.info(f" LLMAnalyzer initialized with provider: {self.provider} (type: {type(self.provider)})")
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_calls=rate_limit_per_minute,
            time_window=60  # 1 minute
        )

        # Initialize clients
        self.clients = {}
        self._initialize_clients()

        # Simple in-memory cache for tweet analysis results
        self.analysis_cache = {}
        self.cache_enabled = True

        # Analysis statistics
        self.stats = {
            'total_analyzed': 0,
            'successful': 0,
            'failed': 0,
            'total_cost': 0.0,
            'start_time': None
        }
    
    def _initialize_clients(self):
        """Initialize LLM API clients"""
        logger.info(f" Initializing clients for provider: {self.provider}")
        try:
            # OpenAI client
            if self.provider == LLMProvider.OPENAI and AsyncOpenAI:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.clients['openai'] = AsyncOpenAI(api_key=api_key)
                    logger.info("OpenAI client initialized")
                else:
                    logger.warning("OpenAI API key not found")
            
            # Mistral client
            if self.provider == LLMProvider.MISTRAL and MistralAsyncClient:
                api_key = os.getenv("MISTRAL_API_KEY")
                if api_key:
                    self.clients['mistral'] = MistralAsyncClient(api_key=api_key)
                    logger.info("Mistral client initialized")
                else:
                    logger.warning("Mistral API key not found")
            
            # Anthropic client
            if self.provider == LLMProvider.ANTHROPIC and anthropic:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self.clients['anthropic'] = anthropic.AsyncAnthropic(api_key=api_key)
                    logger.info("Anthropic client initialized")
                else:
                    logger.warning("Anthropic API key not found")

            # Ollama client (using httpx for API calls)
            logger.info(f" Checking Ollama condition: {self.provider} == {LLMProvider.OLLAMA} = {self.provider == LLMProvider.OLLAMA}")
            if self.provider == LLMProvider.OLLAMA:
                logger.info(" Initializing Ollama client...")
                import httpx
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                api_key = os.getenv("OLLAMA_API_KEY")  # Optional for local Ollama

                # Initialize client with or without API key
                headers = {}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"

                self.clients['ollama'] = httpx.AsyncClient(
                    base_url=base_url,
                    headers=headers,
                    timeout=60.0  # Increase timeout for local LLM
                )
                logger.info(f" Ollama client initialized with base_url: {base_url}")

        except Exception as e:
            logger.error(f"Error initializing LLM clients: {e}")
    
    def _get_analysis_prompt(self, tweet: TweetRaw) -> str:
        """
        Generate analysis prompt for LLM
        
        Args:
            tweet: Tweet to analyze
            
        Returns:
            Formatted prompt for LLM
        """
        return f"""Analyse ce tweet adressé au SAV de Free (opérateur télécom français).

Tweet: "{tweet.text}"

IMPORTANT: Réponds UNIQUEMENT avec un JSON valide. Utilise EXACTEMENT les valeurs indiquées.

Format JSON requis:
{{
  "sentiment": "positive" OU "neutral" OU "negative",
  "sentiment_score": <nombre entre -1.0 et 1.0>,
  "category": "facturation" OU "réseau" OU "technique" OU "abonnement" OU "réclamation" OU "compliment" OU "question" OU "autre",
  "priority": "critique" OU "haute" OU "moyenne" OU "basse",
  "keywords": ["mot1", "mot2", "mot3"],
  "is_urgent": true OU false,
  "needs_response": true OU false,
  "estimated_resolution_time": <nombre de minutes OU null>
}}

Exemple:
{{
  "sentiment": "positive",
  "sentiment_score": 0.8,
  "category": "compliment",
  "priority": "basse",
  "keywords": ["service", "excellent"],
  "is_urgent": false,
  "needs_response": false,
  "estimated_resolution_time": null
}}

RÈGLES:
- sentiment: UNIQUEMENT "positive", "neutral" ou "negative"
- category: UNIQUEMENT UNE des 8 valeurs (pas de combinaisons)
- priority: UNIQUEMENT "critique", "haute", "moyenne" ou "basse"
- Pas de markdown, pas de texte supplémentaire"""
    
    async def _call_openai(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call OpenAI API"""
        try:
            client = self.clients.get('openai')
            if not client:
                raise ValueError("OpenAI client not initialized")
            
            response = await client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "Tu es un assistant d'analyse de satisfaction client pour Free. Réponds UNIQUEMENT en JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
                max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "300"))
            )
            
            content = response.choices[0].message.content.strip()
            # Clean markdown if present
            content = content.replace("```json", "").replace("```", "").strip()
            
            # Estimate cost (approximate for gpt-4o-mini)
            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            cost = (prompt_tokens * 0.00015 + completion_tokens * 0.0006) / 1000
            self.stats['total_cost'] += cost
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    async def _call_mistral(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Mistral API"""
        try:
            client = self.clients.get('mistral')
            if not client:
                raise ValueError("Mistral client not initialized")
            
            response = await client.chat.complete_async(
                model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
                messages=[
                    {"role": "system", "content": "Tu es un expert en analyse de satisfaction client pour Free (opérateur télécom français). Tu analyses les tweets du service client avec précision. Réponds UNIQUEMENT en JSON valide, sans markdown ni commentaires."},
                    {"role": "user", "content": prompt}
                ],
                temperature=float(os.getenv("MISTRAL_TEMPERATURE", "0.2")),
                max_tokens=int(os.getenv("MISTRAL_MAX_TOKENS", "400"))
            )
            
            content = response.choices[0].message.content.strip()
            content = content.replace("```json", "").replace("```", "").strip()
            
            # Mistral pricing is typically lower
            self.stats['total_cost'] += 0.001  # Approximate cost
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            return None
    
    async def _call_anthropic(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Anthropic Claude API"""
        try:
            client = self.clients.get('anthropic')
            if not client:
                raise ValueError("Anthropic client not initialized")
            
            response = await client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
                max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "300")),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text.strip()
            content = content.replace("```json", "").replace("```", "").strip()
            
            # Anthropic pricing
            self.stats['total_cost'] += 0.002  # Approximate cost
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return None

    async def _call_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Ollama API with detailed logging for debugging"""
        logger.info("=" * 80)
        logger.info("OLLAMA API CALL - START")
        logger.info("=" * 80)

        try:
            # Step 1: Verify client initialization
            client = self.clients.get('ollama')
            if not client:
                logger.error(" Ollama client not initialized")
                raise ValueError("Ollama client not initialized")

            logger.info(f" Ollama client found")
            logger.info(f"   - Base URL: {client.base_url}")
            logger.info(f"   - Client type: {type(client)}")

            # Step 2: Build payload
            model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
            max_tokens = int(os.getenv("OLLAMA_MAX_TOKENS", "400"))

            logger.info(f"Configuration:")
            logger.info(f"   - Model: {model}")
            logger.info(f"   - Temperature: {temperature}")
            logger.info(f"   - Max tokens: {max_tokens}")

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Tu es un expert en analyse de satisfaction client pour Free (opérateur télécom français). Tu analyses les tweets du service client avec précision. Réponds UNIQUEMENT en JSON valide, sans markdown ni commentaires."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            logger.info(f"📤 Request payload:")
            logger.info(f"   - Endpoint: /v1/chat/completions")
            logger.info(f"   - Method: POST")
            logger.info(f"   - Payload keys: {list(payload.keys())}")
            logger.info(f"   - Messages count: {len(payload['messages'])}")
            logger.info(f"   - Prompt length: {len(prompt)} characters")
            logger.info(f"   - Prompt preview: {prompt[:200]}...")

            # Step 3: Make the API call
            logger.info(f" Sending request to Ollama...")
            full_url = f"{client.base_url}/v1/chat/completions"
            logger.info(f"   - Full URL: {full_url}")

            response = await client.post("/v1/chat/completions", json=payload)

            # Step 4: Log response details
            logger.info(f"📥 Response received:")
            logger.info(f"   - Status code: {response.status_code}")
            logger.info(f"   - Headers: {dict(response.headers)}")

            response.raise_for_status()
            logger.info(f" Status check passed (2xx)")

            # Step 5: Parse response
            logger.info(f"Parsing response JSON...")
            data = response.json()
            logger.info(f"   - Response keys: {list(data.keys())}")

            if 'choices' in data:
                logger.info(f"   - Choices count: {len(data['choices'])}")
                if len(data['choices']) > 0:
                    choice = data['choices'][0]
                    logger.info(f"   - Choice[0] keys: {list(choice.keys())}")

                    if 'message' in choice:
                        message = choice['message']
                        logger.info(f"   - Message keys: {list(message.keys())}")

                        if 'content' in message:
                            raw_content = message['content']
                            logger.info(f"   - Raw content length: {len(raw_content)} characters")
                            logger.info(f"   - Raw content preview: {raw_content[:300]}...")

                            # Step 6: Clean content
                            content = raw_content.strip()
                            content = content.replace("```json", "").replace("```", "").strip()
                            logger.info(f"   - Cleaned content length: {len(content)} characters")
                            logger.info(f"   - Cleaned content: {content[:500]}...")

                            # Step 7: Parse JSON
                            logger.info(f"Parsing JSON content...")
                            try:
                                parsed_json = json.loads(content)
                                logger.info(f" JSON parsed successfully")
                                logger.info(f"   - Parsed keys: {list(parsed_json.keys())}")
                                logger.info(f"   - Parsed data: {json.dumps(parsed_json, indent=2, ensure_ascii=False)}")

                                # Ollama is typically free or very low cost
                                self.stats['total_cost'] += 0.0001  # Minimal cost

                                logger.info("=" * 80)
                                logger.info(" OLLAMA API CALL - SUCCESS")
                                logger.info("=" * 80)

                                return parsed_json

                            except json.JSONDecodeError as json_err:
                                logger.error(f" JSON parsing failed: {json_err}")
                                logger.error(f"   - Content that failed to parse: {content}")
                                return None
                        else:
                            logger.error(f" No 'content' in message")
                            return None
                    else:
                        logger.error(f" No 'message' in choice[0]")
                        return None
                else:
                    logger.error(f" Empty choices array")
                    return None
            else:
                logger.error(f" No 'choices' in response")
                logger.error(f"   - Full response: {json.dumps(data, indent=2)}")
                return None

        except httpx.HTTPStatusError as http_err:
            logger.error("=" * 80)
            logger.error(f" HTTP Error: {http_err}")
            logger.error(f"   - Status code: {http_err.response.status_code}")
            logger.error(f"   - Response text: {http_err.response.text}")
            logger.error("=" * 80)
            return None

        except Exception as e:
            logger.error("=" * 80)
            logger.error(f" Ollama API error: {e}")
            logger.error(f"   - Exception type: {type(e).__name__}")
            logger.error(f"   - Exception details:", exc_info=True)
            logger.error("=" * 80)
            return None
    
    async def analyze_tweet(self, tweet: TweetRaw) -> Optional[TweetAnalyzed]:
        """
        Analyse individuelle d'un tweet
        Analyze individual tweet with LLM

        Args:
            tweet: Tweet to analyze

        Returns:
            Analyzed tweet or None if failed
        """
        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key(tweet.text)
            if cache_key in self.analysis_cache:
                logger.debug(f"Cache hit for tweet {tweet.tweet_id}")
                cached_result = self.analysis_cache[cache_key]
                # Create new TweetAnalyzed with current tweet_id but cached analysis
                return TweetAnalyzed(
                    tweet_id=tweet.tweet_id,
                    author=tweet.author,
                    text=tweet.text,
                    date=tweet.date,
                    sentiment=cached_result['sentiment'],
                    category=cached_result['category'],
                    priority=cached_result['priority'],
                    confidence=cached_result['confidence'],
                    reasoning=cached_result['reasoning']
                )

        # Wait for rate limiter
        await self.rate_limiter.acquire()

        try:
            self.stats['total_analyzed'] += 1

            # Generate prompt
            prompt = self._get_analysis_prompt(tweet)

            # Call appropriate LLM
            analysis = None
            if self.provider == LLMProvider.OPENAI:
                analysis = await self._call_openai(prompt)
            elif self.provider == LLMProvider.MISTRAL:
                analysis = await self._call_mistral(prompt)
            elif self.provider == LLMProvider.ANTHROPIC:
                analysis = await self._call_anthropic(prompt)
            elif self.provider == LLMProvider.OLLAMA:
                analysis = await self._call_ollama(prompt)
            
            if not analysis:
                self.stats['failed'] += 1
                return None
            
            # Extract metadata from original text
            from ..utils.cleaning import TextCleaner
            cleaner = TextCleaner()
            mentions = cleaner.extract_mentions(tweet.text)
            hashtags = cleaner.extract_hashtags(tweet.text)
            urls = cleaner.extract_urls(tweet.text)
            
            # Create TweetAnalyzed object
            analyzed_tweet = TweetAnalyzed(
                tweet_id=tweet.tweet_id,
                author=tweet.author,
                text=tweet.text,
                date=tweet.date,
                mentions=mentions,
                hashtags=hashtags,
                urls=urls,
                sentiment=SentimentType(analysis['sentiment']),
                sentiment_score=float(analysis['sentiment_score']),
                category=CategoryType(analysis['category']),
                priority=PriorityLevel(analysis['priority']),
                keywords=analysis.get('keywords', []),
                is_urgent=bool(analysis.get('is_urgent', False)),
                needs_response=bool(analysis.get('needs_response', True)),
                estimated_resolution_time=analysis.get('estimated_resolution_time')
            )

            # Store in cache for future use
            if self.cache_enabled:
                cache_key = self._get_cache_key(tweet.text)
                self.analysis_cache[cache_key] = {
                    'sentiment': analyzed_tweet.sentiment,
                    'category': analyzed_tweet.category,
                    'priority': analyzed_tweet.priority,
                    'confidence': getattr(analyzed_tweet, 'confidence', 0.8),
                    'reasoning': getattr(analyzed_tweet, 'reasoning', '')
                }
            
            self.stats['successful'] += 1
            return analyzed_tweet
            
        except Exception as e:
            logger.error(f"Error analyzing tweet {tweet.tweet_id}: {e}", exc_info=True)
            self.stats['failed'] += 1
            return None
    
    async def analyze_batch(self, tweets: List[TweetRaw]) -> List[TweetAnalyzed]:
        """
        Analyse par batch avec rate limiting
        Analyze tweets in batches with rate limiting
        
        Args:
            tweets: List of tweets to analyze
            
        Returns:
            List of successfully analyzed tweets
        """
        if not tweets:
            return []
        
        logger.info(f"Starting batch analysis of {len(tweets)} tweets")
        self.stats['start_time'] = datetime.now(UTC)
        
        results = []
        
        # Process in batches to respect rate limits
        for i in range(0, len(tweets), self.max_concurrent):
            batch = tweets[i:i+self.max_concurrent]
            logger.info(f"Processing batch {i//self.max_concurrent + 1}: tweets {i+1}-{min(i+len(batch), len(tweets))}")
            
            # Create tasks for concurrent processing
            tasks = [self.analyze_tweet(tweet) for tweet in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            for result in batch_results:
                if isinstance(result, TweetAnalyzed):
                    results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
            
            # Rate limiting delay between batches
            if i + self.max_concurrent < len(tweets):
                delay = float(os.getenv("BATCH_PROCESSING_DELAY", "2"))
                logger.info(f"Waiting {delay}s before next batch...")
                await asyncio.sleep(delay)
        
        # Log final statistics
        end_time = datetime.now(UTC)
        duration = (end_time - self.stats['start_time']).total_seconds()
        
        logger.info(f"Batch analysis completed:")
        logger.info(f"  - Total processed: {self.stats['total_analyzed']}")
        logger.info(f"  - Successful: {self.stats['successful']}")
        logger.info(f"  - Failed: {self.stats['failed']}")
        logger.info(f"  - Success rate: {(self.stats['successful']/self.stats['total_analyzed']*100):.1f}%")
        logger.info(f"  - Duration: {duration:.1f}s")
        logger.info(f"  - Estimated cost: ${self.stats['total_cost']:.4f}")
        
        return results
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        stats = self.stats.copy()
        if stats['start_time']:
            duration = (datetime.now(UTC) - stats['start_time']).total_seconds()
            stats['duration_seconds'] = duration
            stats['tweets_per_second'] = stats['successful'] / duration if duration > 0 else 0
        
        return stats
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for tweet text"""
        # Normalize text and create hash for cache key
        normalized_text = text.lower().strip()
        return hashlib.md5(normalized_text.encode('utf-8')).hexdigest()

    def clear_cache(self):
        """Clear the analysis cache"""
        self.analysis_cache.clear()
        logger.info("Analysis cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.analysis_cache),
            'cache_enabled': self.cache_enabled
        }

    async def test_connection(self) -> bool:
        """Test LLM API connection"""
        try:
            test_tweet = TweetRaw(
                tweet_id="test_123",
                author="test_user",
                text="Test de connexion API",
                date=datetime.now(UTC)
            )
            
            result = await self.analyze_tweet(test_tweet)
            return result is not None
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
