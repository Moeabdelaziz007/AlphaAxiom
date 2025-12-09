# ========================================
# 📰 AXIOM NEWS SERVER - Sentiment Analysis MCP
# ========================================
# Aggregates news from multiple sources:
#   - NewsData.io (Free tier: 200 req/day)
#   - Finnhub News (Rate Limited)
# ========================================
# Features:
#   - Keyword-based sentiment scoring
#   - Crypto/Forex/Stock news filtering
#   - KV caching (5 minute TTL for news)
# ========================================

import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from js import fetch


class NewsServer:
    """
    News & Sentiment Analysis Server - "The Ears of Axiom".
    
    Fetches market news and calculates sentiment scores.
    """
    
    CACHE_TTL_SECONDS = 300  # 5 minute cache for news
    
    # Sentiment keywords (weighted)
    BULLISH_KEYWORDS = {
        "surge": 3, "soar": 3, "rally": 3, "breakout": 2, "bullish": 2,
        "buy": 1, "upgrade": 2, "growth": 1, "profit": 1, "gain": 1,
        "rise": 1, "jump": 2, "record": 2, "high": 1, "strong": 1,
        "positive": 1, "optimistic": 2, "boom": 3, "moon": 3, "pump": 2
    }
    
    BEARISH_KEYWORDS = {
        "crash": 3, "plunge": 3, "collapse": 3, "bearish": 2, "sell": 1,
        "downgrade": 2, "loss": 1, "drop": 1, "fall": 1, "decline": 1,
        "low": 1, "weak": 1, "dump": 2, "fear": 2, "panic": 3,
        "negative": 1, "warning": 2, "risk": 1, "concern": 1, "recession": 3
    }
    
    def __init__(self, env):
        """
        Initialize NewsServer.
        
        Args:
            env: Cloudflare Worker environment
        """
        self.env = env
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
        self.newsdata_key = str(getattr(env, 'NEWSDATA_API_KEY', ''))
        self.finnhub_key = str(getattr(env, 'FINNHUB_API_KEY', ''))
    
    async def get_sentiment(
        self,
        symbol: str,
        asset_type: str = "crypto"
    ) -> Dict[str, Any]:
        """
        Get aggregated sentiment score for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., BTC, AAPL)
            asset_type: 'crypto', 'forex', or 'stock'
        
        Returns:
            Sentiment analysis with score (-100 to +100)
        """
        # Check cache
        cache_key = f"sentiment:{symbol}"
        cached = await self._get_cached(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached
        
        # Fetch news and analyze
        news = await self.get_news(symbol, asset_type)
        
        if news.get("status") != "success" or not news.get("articles"):
            return {
                "status": "no_data",
                "symbol": symbol,
                "score": 0,
                "signal": "NEUTRAL",
                "message": "No news available for sentiment analysis"
            }
        
        # Calculate sentiment
        result = self._analyze_sentiment(news["articles"], symbol)
        result["article_count"] = len(news["articles"])
        result["source"] = news.get("source", "unknown")
        
        # Cache result
        await self._set_cached(cache_key, result)
        
        return result
    
    async def get_news(
        self,
        symbol: str,
        asset_type: str = "crypto",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Fetch news articles for a symbol.
        
        Args:
            symbol: Trading symbol
            asset_type: Asset type
            limit: Max articles
        
        Returns:
            News articles
        """
        # Try NewsData.io first
        if self.newsdata_key:
            result = await self._fetch_newsdata(symbol, asset_type, limit)
            if result.get("status") == "success":
                return result
        
        # Fallback to Finnhub
        if self.finnhub_key and asset_type != "crypto":
            result = await self._fetch_finnhub(symbol, limit)
            if result.get("status") == "success":
                return result
        
        return {
            "status": "error",
            "message": "No news sources configured or available"
        }
    
    async def _fetch_newsdata(
        self,
        symbol: str,
        asset_type: str,
        limit: int
    ) -> Dict[str, Any]:
        """Fetch from NewsData.io."""
        try:
            # Map symbol to search query
            query = self._symbol_to_query(symbol, asset_type)
            category = "business" if asset_type != "crypto" else "business"
            
            url = f"https://newsdata.io/api/1/news?apikey={self.newsdata_key}&q={query}&language=en&size={limit}"
            
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if data.get("status") == "success" and data.get("results"):
                articles = []
                for item in data["results"][:limit]:
                    articles.append({
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "source": item.get("source_id", ""),
                        "published": item.get("pubDate", ""),
                        "url": item.get("link", "")
                    })
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "articles": articles,
                    "source": "newsdata.io",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {"status": "error", "message": "NewsData.io returned no results"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _fetch_finnhub(
        self,
        symbol: str,
        limit: int
    ) -> Dict[str, Any]:
        """Fetch from Finnhub (stocks only)."""
        try:
            # Get date range (last 7 days)
            from datetime import timedelta
            to_date = datetime.utcnow()
            from_date = to_date - timedelta(days=7)
            
            url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date.strftime('%Y-%m-%d')}&to={to_date.strftime('%Y-%m-%d')}&token={self.finnhub_key}"
            
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if isinstance(data, list) and len(data) > 0:
                articles = []
                for item in data[:limit]:
                    articles.append({
                        "title": item.get("headline", ""),
                        "description": item.get("summary", ""),
                        "source": item.get("source", ""),
                        "published": datetime.fromtimestamp(item.get("datetime", 0)).isoformat(),
                        "url": item.get("url", "")
                    })
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "articles": articles,
                    "source": "finnhub",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {"status": "error", "message": "Finnhub returned no results"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _analyze_sentiment(
        self,
        articles: List[Dict],
        symbol: str
    ) -> Dict[str, Any]:
        """
        Analyze sentiment from article titles and descriptions.
        
        Returns score from -100 (bearish) to +100 (bullish).
        """
        total_bullish = 0
        total_bearish = 0
        analyzed_count = 0
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            
            # Count bullish keywords
            for word, weight in self.BULLISH_KEYWORDS.items():
                count = len(re.findall(r'\b' + word + r'\b', text))
                total_bullish += count * weight
            
            # Count bearish keywords
            for word, weight in self.BEARISH_KEYWORDS.items():
                count = len(re.findall(r'\b' + word + r'\b', text))
                total_bearish += count * weight
            
            analyzed_count += 1
        
        # Calculate score (-100 to +100)
        total = total_bullish + total_bearish
        if total == 0:
            score = 0
        else:
            score = ((total_bullish - total_bearish) / total) * 100
        
        # Determine signal
        if score >= 50:
            signal = "STRONG_BUY"
            strength = 90
        elif score >= 20:
            signal = "BUY"
            strength = 70
        elif score <= -50:
            signal = "STRONG_SELL"
            strength = 90
        elif score <= -20:
            signal = "SELL"
            strength = 70
        else:
            signal = "NEUTRAL"
            strength = 50
        
        return {
            "status": "success",
            "symbol": symbol,
            "score": round(score, 2),
            "signal": signal,
            "strength": strength,
            "bullish_score": total_bullish,
            "bearish_score": total_bearish,
            "analyzed_articles": analyzed_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _symbol_to_query(self, symbol: str, asset_type: str) -> str:
        """Convert symbol to search query."""
        crypto_names = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum",
            "SOL": "Solana",
            "XRP": "Ripple XRP",
            "DOGE": "Dogecoin",
            "ADA": "Cardano",
            "BNB": "Binance BNB"
        }
        
        # Extract base symbol
        base = symbol.replace("USDT", "").replace("USD", "").replace("PERP", "")
        
        if asset_type == "crypto" and base in crypto_names:
            return crypto_names[base]
        
        return symbol
    
    # ========================================
    # 🗄️ KV Caching
    # ========================================
    
    async def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached value."""
        if not self.kv:
            return None
        try:
            cached = await self.kv.get(key)
            if cached:
                data = json.loads(cached)
                cached_time = datetime.fromisoformat(data.get("timestamp", "2000-01-01"))
                age = (datetime.utcnow() - cached_time).total_seconds()
                if age < self.CACHE_TTL_SECONDS:
                    return data
        except Exception:
            pass
        return None
    
    async def _set_cached(self, key: str, value: Dict) -> None:
        """Store in cache."""
        if not self.kv:
            return
        try:
            await self.kv.put(key, json.dumps(value), {"expirationTtl": self.CACHE_TTL_SECONDS * 2})
        except Exception:
            pass


# ========================================
# 🏭 Factory
# ========================================

def get_news_server(env) -> NewsServer:
    """Get NewsServer instance."""
    return NewsServer(env)
