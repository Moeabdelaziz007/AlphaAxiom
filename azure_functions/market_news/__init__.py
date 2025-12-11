import datetime
import logging
import json
import os
import requests
import azure.functions as func

# Configuration
CLOUDFLARE_WORKER_URL = os.getenv("CLOUDFLARE_WORKER_URL", "https://your-worker.workers.dev")
CLOUDFLARE_KV_KEY = "news_cache"
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
# If writing directly to KV via Cloudflare API (Preferred if worker doesn't have a specific PUT endpoint)
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_KV_NAMESPACE_ID = os.getenv("CLOUDFLARE_KV_NAMESPACE_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

def fetch_google_news_rss(symbol):
    """Fetch news from Google News RSS"""
    try:
        rss_url = f"https://news.google.com/rss/search?q={symbol}+stock+news&hl=en-US&gl=US&ceid=US:en"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; AlphaAxiombot/1.0)"}
        response = requests.get(rss_url, headers=headers, timeout=10)
        return response.text[:10000] # Limit size
    except Exception as e:
        logging.error(f"Error fetching Google RSS for {symbol}: {e}")
        return None

def fetch_finnhub_news():
    """Fetch general market news from Finnhub"""
    if not FINNHUB_API_KEY:
        return []
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_API_KEY}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()[:5] # Top 5 news
        return []
    except Exception as e:
        logging.error(f"Error fetching Finnhub news: {e}")
        return []

def save_to_cloudflare_kv(key, value):
    """Save data to Cloudflare KV via API"""
    if not (CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_KV_NAMESPACE_ID and CLOUDFLARE_API_TOKEN):
        logging.warning("Cloudflare KV credentials missing. Skipping upload.")
        return False

    url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/storage/kv/namespaces/{CLOUDFLARE_KV_NAMESPACE_ID}/values/{key}"

    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "text/plain" # or application/json depending on need, KV stores value as string/bytes
    }

    # Value must be string
    if not isinstance(value, str):
        value = json.dumps(value)

    try:
        response = requests.put(url, headers=headers, data=value, timeout=10)
        if response.status_code == 200:
            logging.info(f"Successfully wrote key '{key}' to Cloudflare KV.")
            return True
        else:
            logging.error(f"Failed to write to KV: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Exception writing to KV: {e}")
        return False

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    logging.info(f"Python timer trigger function ran at {utc_timestamp}")

    # 1. Fetch News
    logging.info("Fetching Market News...")

    # General Market News (Finnhub)
    general_news = fetch_finnhub_news()

    # Specific Symbols (Google RSS)
    symbols = ["SPY", "BTC", "ETH", "AAPL", "TSLA"]
    specific_news = {}
    for sym in symbols:
        rss_content = fetch_google_news_rss(sym)
        if rss_content:
            specific_news[sym] = "RSS Content Fetched" # Storing full XML might be too large, or we parse it. keeping raw for now or simplified.
            # In a real app, we'd parse XML to JSON here to save space.

    # 2. Aggregated Payload
    payload = {
        "timestamp": utc_timestamp,
        "general": general_news,
        "specific_summary": specific_news # Just a summary for now
    }

    # 3. Push to Cloudflare KV
    # Logic: The worker reads from 'news_cache' key
    save_to_cloudflare_kv(CLOUDFLARE_KV_KEY, payload)

    logging.info("Market News Cycle Complete.")
