"""
daily_brief.py
AQT Intelligence Hub - Phase 6
Fetches daily news from D1 (via Worker Proxy) and generates an AI briefing using Perplexity API.
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
WORKER_URL = os.getenv("WORKER_URL", "https://trading-brain-v1.amrikyy1.workers.dev")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "")  # Set via environment
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")


# Perplexity Settings (Price Optimization: sonar)
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
MODEL = "sonar"

def get_latest_headlines():
    """Step 1: Get raw data from D1 via Worker."""
    print("📡 Fetching latest news from D1 Vault...")
    try:
        resp = requests.get(f"{WORKER_URL}/api/news/latest?limit=50", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Fetched {data.get('count', 0)} headlines")
            return data.get("news", [])
        else:
            print(f"⚠️ Failed to fetch news: {resp.status_code}")
            return []
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return []

def analyze_with_perplexity(headlines):
    """Step 2: The $0.002 AI Brain"""
    if not headlines:
        print("⚠️ No headlines to analyze.")
        return None
    
    print(f"🤖 Analyzing {len(headlines)} headlines with Perplexity AI ({MODEL})...")
    
    # Format headlines for the prompt
    headlines_text = "\n".join([f"- {h['title']} ({h.get('source', 'Unknown')})" for h in headlines])
    
    # Arabic Prompt (As per user's specification)
    prompt = f"""
    بصفتك محللاً مالياً خبيراً، اقرأ عناوين العملات الرقمية التالية:
    ---
    {headlines_text}
    ---
    المطلوب رد بصيغة JSON فقط:
    1. "summary": ملخص تنفيذي للمستثمرين (100 كلمة).
    2. "sentiment": كلمة واحدة (Bullish, Bearish, Neutral).
    """

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a crypto financial analyst. Output JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(PERPLEXITY_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content']
            # Clean markdown blocks
            clean_json = content.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        else:
            print(f"❌ Perplexity Error: {resp.status_code} - {resp.text}")
            return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Analysis Error: {e}")
        return None

def save_briefing(data):
    """Step 3: Save back to D1 via Worker."""
    print("💾 Saving briefing to D1...")
    try:
        resp = requests.post(
            f"{WORKER_URL}/api/briefing/save",
            json=data,
            headers={
                "X-Internal-Secret": INTERNAL_SECRET,
                "Content-Type": "application/json"
            },
            timeout=15
        )
        if resp.status_code == 200:
            print(f"✅ Daily Briefing Saved: Sentiment = {data.get('sentiment', 'N/A')}")
            return True
        else:
            print(f"⚠️ Save Failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Save Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print(f"🤖 AQT Daily Brief | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # Step 1: Fetch
    headlines = get_latest_headlines()
    
    if headlines:
        # Step 2: Analyze
        analysis = analyze_with_perplexity(headlines)
        
        if analysis:
            # Step 3: Save
            save_briefing(analysis)
            
            # Step 4: Print Summary
            print("\n📝 Briefing Content:")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        else:
            print("⚠️ Analysis failed. Check API key.")
    else:
        print("⚠️ No headlines found to analyze.")
    
    print("\n💤 Cycle Complete.")
