"""
Simple test script to upload CSV and check analysis status
"""
import requests
import time
import json

# Upload CSV
print(" Uploading CSV...")
with open("data/samples/sample_tweets.csv", "rb") as f:
    files = {"file": ("sample_tweets.csv", f, "text/csv")}
    data = {
        "llm_provider": "ollama",  # Explicitly specify Ollama provider
        "max_tweets": "3",
        "batch_size": "1"
    }
    response = requests.post("http://localhost:8000/upload-csv", files=files, data=data)
    
if response.status_code == 200:
    result = response.json()
    batch_id = result["batch_id"]
    print(f" Upload successful! Batch ID: {batch_id}")
    
    # Wait for analysis
    print("⏳ Waiting 20 seconds for analysis...")
    time.sleep(20)
    
    # Check status
    print(" Checking status...")
    status_response = requests.get(f"http://localhost:8000/analysis-status/{batch_id}")
    if status_response.status_code == 200:
        status = status_response.json()
        print(f"Status: {status['status']}")
        print(f"Total: {status['total_tweets']}")
        print(f"Analyzed: {status['analyzed_tweets']}")
        print(f"Failed: {status['failed_tweets']}")
        print(f"Processing time: {status['processing_time']}s")
        
        if status['analyzed_tweets'] == status['total_tweets'] and status['failed_tweets'] == 0:
            print("\n SUCCESS! All tweets analyzed")
            
            # Get KPIs
            kpis_response = requests.get(f"http://localhost:8000/kpis/{batch_id}")
            if kpis_response.status_code == 200:
                kpis = kpis_response.json()
                print("\n KPIs:")
                print(f"  Total: {kpis['total_tweets']}")
                print(f"  Sentiment - Pos: {kpis['sentiment_distribution']['positive']} | Neu: {kpis['sentiment_distribution']['neutral']} | Neg: {kpis['sentiment_distribution']['negative']}")
                print(f"  Urgent: {kpis['urgent_tweets']}")
                print(f"  Needs response: {kpis['needs_response_tweets']}")
        else:
            print(f"\n FAILED - {status['failed_tweets']} tweets failed")
    else:
        print(f" Error getting status: {status_response.status_code} - {status_response.text}")
else:
    print(f" Upload failed: {response.status_code} - {response.text}")

