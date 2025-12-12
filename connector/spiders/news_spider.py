"""
News Spider - AQT Intelligence Layer
Fetches crypto news from RSS feeds and emits events for the dashboard.
Zero external dependencies (uses stdlib xml.etree + aiohttp)
"""

import asyncio
import aiohttp
from xml.etree import ElementTree as ET
from datetime import datetime
from typing import Callable, Set

# RSS Feed Sources (Free, Real-time)
RSS_FEEDS = [
    ("Coindesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
]

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
    
    async def fetch_feed(self, session: aiohttp.ClientSession, name: str, url: str):
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
            
            # Emit news events
            for source, title, link in all_news:
                self.on_news(source, title, link)
            
            return len(all_news)
    
    async def start(self):
        """Start the continuous spider loop."""
        self._running = True
        print(f"[SPIDER-01] Starting news spider (interval: {self.interval}s)")
        
        # Initial fetch
        count = await self.run_once()
        print(f"[SPIDER-01] Initial fetch: {count} new articles")
        
        # Background loop
        while self._running:
            await asyncio.sleep(self.interval)
            count = await self.run_once()
            if count > 0:
                print(f"[SPIDER-01] Found {count} new articles")
    
    def stop(self):
        """Stop the spider loop."""
        self._running = False
        print("[SPIDER-01] Spider stopped")


# For testing
if __name__ == "__main__":
    spider = NewsSpider(interval=30)
    asyncio.run(spider.start())
