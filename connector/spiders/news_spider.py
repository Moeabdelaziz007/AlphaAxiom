"""
News Spider - AQT Intelligence Layer
Fetches crypto news from RSS feeds and emits events for the dashboard.
Zero external dependencies (uses stdlib xml.etree + aiohttp)
"""

import asyncio
import aiohttp
from xml.etree import ElementTree as ET
from datetime import datetime
from typing import Callable, Set, List, Tuple
import os

# RSS Feed Sources (Free, Real-time)
RSS_FEEDS = [
    ("Coindesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
]

# Cloudflare Worker Configuration
WORKER_URL = os.getenv("WORKER_URL", "https://trading-brain-v1.amrikyy1.workers.dev/api/news/push")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "")  # Set via environment

class NewsSpider:
    """Async spider that fetches crypto news from RSS feeds."""
    
    def __init__(self, on_news: Callable[[str, str, str], None] = None, interval: int = 60):
        """
        Initialize the news spider.
        
        Args:
            on_news: Callback function(source, title, link) when new article found.
            interval: Seconds between fetch cycles.
        """
        self.on_news = on_news or self._default_handler
        self.interval = interval
        self.seen_links: Set[str] = set()
        self._running = False
    
    def _default_handler(self, source: str, title: str, link: str):
        """Default handler logs to console."""
        print(f"[SPIDER-01] {source}: {title}")
        
    async def push_to_cloud(self, session: aiohttp.ClientSession, title: str, link: str, source: str):
        """Sending data to the Edge (D1)"""
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Secret": INTERNAL_SECRET
        }
        payload = {
            "source": source,
            "title": title,
            "link": link,
            "sentiment": "neutral" 
        }
        
        try:
            async with session.post(WORKER_URL, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    print(f"✅ [D1 SYNC] Saved: {title[:30]}...")
                elif resp.status == 401:
                    print("⛔ [D1 AUTH] Unauthorized! Check INTERNAL_SECRET.")
                else:
                    print(f"⚠️ [D1 FAIL] Status {resp.status} for {title[:30]}...")
        except Exception as e:
            print(f"❌ [D1 ERROR] Connection failed: {str(e)}")

    async def fetch_feed(self, session: aiohttp.ClientSession, name: str, url: str) -> List[Tuple[str, str, str]]:
        """Fetch and parse a single RSS feed."""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return []
                
                text = await resp.text()
                root = ET.fromstring(text)
                
                # Handle both RSS 2.0 and Atom formats
                items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                
                news_items = []
                for item in items[:5]:  # Limit to 5 most recent
                    # RSS 2.0
                    title_el = item.find('title')
                    link_el = item.find('link')
                    
                    # Atom fallback
                    if link_el is None:
                        link_el = item.find('{http://www.w3.org/2005/Atom}link')
                        if link_el is not None:
                            link = link_el.get('href', '')
                        else:
                            link = ''
                    else:
                        link = link_el.text or ''
                    
                    title = title_el.text if title_el is not None else 'No title'
                    
                    if link and link not in self.seen_links:
                        self.seen_links.add(link)
                        news_items.append((name, title.strip(), link.strip()))
                
                return news_items
                
        except Exception as e:
            print(f"[SPIDER-01] Error fetching {name}: {e}")
            return []
    
    async def run_once(self):
        """Run a single fetch cycle across all feeds."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_feed(session, name, url) for name, url in RSS_FEEDS]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_news = []
            for result in results:
                if isinstance(result, list):
                    all_news.extend(result)
            
            # Emit events & Push to D1
            for source, title, link in all_news:
                # 1. Local Callback
                self.on_news(source, title, link)
                
                # 2. Persist to D1 (Await to ensure session stays open)
                await self.push_to_cloud(session, title, link, source)
            
            return len(all_news)
    
    async def start(self):
        """Start the continuous spider loop."""
        self._running = True
        print(f"[SPIDER-01] Starting news spider (interval: {self.interval}s)")
        print(f"[SPIDER-01] Target Worker: {WORKER_URL}")
        
        # Initial wait to let connections settle
        await asyncio.sleep(1)
        
        # Background loop
        while self._running:
            try:
                count = await self.run_once()
                if count > 0:
                    print(f"[SPIDER-01] Processed {count} new articles")
            except Exception as e:
                print(f"[SPIDER-01] Critical Loop Error: {e}")
                
            await asyncio.sleep(self.interval)
    
    def stop(self):
        """Stop the spider loop."""
        self._running = False
        print("[SPIDER-01] Spider stopped")


# For testing
if __name__ == "__main__":
    spider = NewsSpider(interval=30)
    asyncio.run(spider.start())
