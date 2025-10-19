"""
Test direct analysis without HTTP server
"""
import sys
import asyncio
import logging
sys.path.insert(0, "backend")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.services.llm_analyzer import LLMAnalyzer
from app.models import TweetRaw
from datetime import datetime

async def test_analysis():
    """Test analyzing a single tweet with Ollama"""
    print("🧪 Testing direct tweet analysis with Ollama...")
    
    # Create test tweet
    test_tweet = TweetRaw(
        tweet_id="test_001",
        author="test_user",
        text="Merci Free pour votre excellent service!",
        date=datetime.utcnow(),
        url="https://twitter.com/test/status/123"
    )
    
    print(f"📝 Tweet: {test_tweet.text}")
    
    # Initialize analyzer with Ollama
    print("🔧 Initializing LLMAnalyzer with Ollama...")
    analyzer = LLMAnalyzer(provider="ollama", batch_size=1)
    print(f"   Provider: {analyzer.provider}")
    print(f"   Clients: {list(analyzer.clients.keys())}")
    
    # Analyze
    print("⏳ Analyzing tweet...")
    try:
        result = await analyzer.analyze_tweet(test_tweet)
        
        if result:
            print("\n✅ Analysis successful!")
            print(f"   Sentiment: {result.sentiment.value}")
            print(f"   Category: {result.category.value}")
            print(f"   Priority: {result.priority.value}")
            print(f"   Keywords: {result.keywords}")
            print(f"   Is urgent: {result.is_urgent}")
            print(f"   Needs response: {result.needs_response}")
            return True
        else:
            print("\n❌ Analysis returned None")
            return False
    except Exception as e:
        print(f"\n❌ Analysis failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_analysis())
    sys.exit(0 if success else 1)

