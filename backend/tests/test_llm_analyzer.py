import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Set environment variables
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["OLLAMA_MODEL"] = "phi3:mini"
os.environ["OLLAMA_TEMPERATURE"] = "0.2"
os.environ["OLLAMA_MAX_TOKENS"] = "400"

from app.services.llm_analyzer import LLMAnalyzer
from app.models import TweetRaw

async def test_llm_analyzer():
    """Test LLMAnalyzer with Ollama provider"""
    print("=" * 80)
    print("TEST: LLMAnalyzer with Ollama Provider")
    print("=" * 80)
    
    # Create test tweet
    tweet = TweetRaw(
        tweet_id="test_001",
        author="TestUser",
        text="Service client excellent! Merci Free Mobile.",
        date="2024-10-18 12:00:00",
        url="https://twitter.com/test/status/123"
    )
    
    print(f"\n Test Tweet:")
    print(f"   ID: {tweet.tweet_id}")
    print(f"   Author: {tweet.author}")
    print(f"   Text: {tweet.text}")
    
    # Initialize LLMAnalyzer with Ollama
    print(f"\n Initializing LLMAnalyzer with provider='ollama'...")
    try:
        analyzer = LLMAnalyzer(provider="ollama", batch_size=1)
        print(f" LLMAnalyzer initialized successfully")
        print(f"   Provider: {analyzer.provider}")
        print(f"   Clients: {list(analyzer.clients.keys())}")
    except Exception as e:
        print(f" Failed to initialize LLMAnalyzer: {e}")
        return
    
    # Analyze tweet
    print(f"\n🤖 Analyzing tweet...")
    try:
        result = await analyzer.analyze_tweet(tweet)
        
        if result:
            print(f" Analysis successful!")
            print(f"\n Results:")
            print(f"   Sentiment: {result.sentiment}")
            print(f"   Sentiment Score: {result.sentiment_score}")
            print(f"   Category: {result.category}")
            print(f"   Priority: {result.priority}")
            print(f"   Keywords: {result.keywords}")
            print(f"   Is Urgent: {result.is_urgent}")
            print(f"   Needs Response: {result.needs_response}")
            print(f"   Summary: {result.summary}")
        else:
            print(f" Analysis failed - returned None")
            
    except Exception as e:
        print(f" Analysis failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Get stats
    print(f"\n📈 Analysis Stats:")
    stats = analyzer.get_analysis_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(test_llm_analyzer())

