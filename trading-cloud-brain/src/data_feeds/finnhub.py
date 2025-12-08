"""
📰 Finnhub Data Connector for AXIOM Trading System
Market Data, News, and Company Fundamentals

FREE TIER: 60 API calls/minute
FEATURES: Real-time quotes, company news, earnings, forex rates

Based on User Capability List (Dec 2025):
✅ FREE/HIGH USAGE:
- Quote, Company News, Basic Financials
- Market Status, Market Holiday
- Insider Transactions, Insider Sentiment (New)
- Recommendation Trends, Earnings Calendar
- WebSocket (Trades)

⛔ PREMIUM:
- News Sentiment, SEC Sentiment
- Candles (OHLCV) for Stocks/Forex/Crypto
- Technical Indicators (All)
- Company Profile 2

API Documentation: https://finnhub.io/docs/api
"""

import json
from typing import Optional, Dict, List


class FinnhubConnector:
    """
    Finnhub Market Data Integration.
    
    Free Tier Features:
    - Real-time quotes (US stocks, Forex)
    - Company news
    - Earnings calendar
    - Basic fundamentals
    """
    
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self, api_key: str):
        """
        Initialize with Finnhub API key.
        Get free key at: https://finnhub.io/register
        """
        self.api_key = api_key
    
    async def _fetch(self, endpoint: str, params: dict = None) -> dict:
        """Make API request to Finnhub."""
        from js import fetch
        
        params = params or {}
        params["token"] = self.api_key
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.BASE_URL}{endpoint}?{query_string}"
        
        response = await fetch(url)
        
        if response.status == 429:
            return {"error": "Rate limit exceeded (60 calls/min)"}
        if response.status == 403:
            return {"error": "Premium feature - Access Denied"}
        
        data = await response.json()
        return data
    
    # ==========================================
    # 📈 MARKET DATA
    # ==========================================
    
    async def get_quote(self, symbol: str) -> dict:
        """
        Get real-time quote for a symbol.
        High Usage Endpoint.
        """
        data = await self._fetch("/quote", {"symbol": symbol})
        
        if "error" in data or "c" not in data:
            return {"error": "Failed to fetch quote"}
        
        current = data.get("c", 0)
        prev = data.get("pc", current)
        change = current - prev
        change_pct = (change / prev * 100) if prev else 0
        
        return {
            "symbol": symbol,
            "current": current,
            "high": data.get("h", 0),
            "low": data.get("l", 0),
            "open": data.get("o", 0),
            "prev_close": prev,
            "change": round(change, 4),
            "change_pct": round(change_pct, 2),
            "timestamp": data.get("t", 0)
        }
    
    async def get_market_status(self, exchange: str = "US") -> dict:
        """Get market status (Open/Closed/Holiday). (New/Free)"""
        return await self._fetch("/stock/market-status", {"exchange": exchange})
    
    # ==========================================
    # 📰 NEWS & FUNDAMENTALS
    # ==========================================
    
    async def get_company_news(
        self,
        symbol: str,
        from_date: str = None,
        to_date: str = None
    ) -> list:
        """
        Get company news headlines.
        High Usage Endpoint.
        """
        from datetime import datetime, timedelta
        
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        data = await self._fetch("/company-news", {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        })
        
        if isinstance(data, dict) and "error" in data:
            return []
        
        news = []
        for article in data[:20]:  # Limit to 20 articles
            news.append({
                "headline": article.get("headline", ""),
                "summary": article.get("summary", "")[:200],
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "datetime": article.get("datetime", 0),
                "related": article.get("related", "")
            })
        
        return news
    
    async def get_basic_financials(self, symbol: str, metric: str = "all") -> dict:
        """
        Get basic financial data. 
        High Usage Endpoint.
        """
        data = await self._fetch("/stock/metric", {
            "symbol": symbol,
            "metric": metric
        })
        
        if "error" in data:
            return data
            
        return {
            "symbol": symbol,
            "metric_type": data.get("metricType"),
            "metrics": data.get("metric", {})
        }

    async def get_recommendation_trends(self, symbol: str) -> list:
        """Get analyst recommendation trends (Buy/Sell/Hold)."""
        data = await self._fetch("/stock/recommendation", {"symbol": symbol})
        if isinstance(data, list):
            return data[:5] # Last 5 periods
        return []

    # ==========================================
    # 🧠 SENTIMENT (New/Free & Custom)
    # ==========================================

    async def get_insider_sentiment(self, symbol: str) -> dict:
        """
        Get insider sentiment data.
        Marked as 'New' in docs - might be free or trial.
        """
        from datetime import datetime, timedelta
        
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d") # Last 90 days
        
        data = await self._fetch("/stock/insider-sentiment", {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        })
        
        return data  # Return raw data for analysis if available

    async def get_news_sentiment_basic(self, symbol: str) -> dict:
        """
        Basic sentiment analysis using news headlines.
        FREE alternative to premium sentiment API.
        
        Uses keyword matching for basic sentiment scoring.
        """
        news = await self.get_company_news(symbol)
        
        if not news:
            return {"sentiment": "NEUTRAL", "score": 0, "articles": 0}
        
        # Keyword-based sentiment (basic)
        positive_words = [
            "surge", "rally", "gain", "profit", "growth", "beat", "upgrade",
            "bullish", "record", "high", "strong", "optimistic", "buy",
            "outperform", "soar", "jump", "boost", "successful"
        ]
        negative_words = [
            "drop", "fall", "loss", "decline", "crash", "miss", "downgrade",
            "bearish", "low", "weak", "concern", "sell", "underperform",
            "plunge", "slump", "cut", "warning", "fear", "risk"
        ]
        
        total_score = 0
        
        for article in news:
            text = (article["headline"] + " " + article["summary"]).lower()
            
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            total_score += (pos_count - neg_count)
        
        # Normalize score
        avg_score = total_score / len(news) if news else 0
        
        if avg_score > 0.5:
            sentiment = "BULLISH"
        elif avg_score < -0.5:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"
        
        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "score": round(avg_score, 2),
            "articles_analyzed": len(news),
            "method": "keyword_matching",
            "note": "Basic analysis. For AI sentiment, use Groq/DeepSeek."
        }
    
    # ==========================================
    # 📊 EARNINGS & FUNDAMENTALS
    # ==========================================
    
    async def get_earnings_calendar(
        self,
        from_date: str = None,
        to_date: str = None
    ) -> list:
        """Get upcoming earnings announcements."""
        from datetime import datetime, timedelta
        
        if not to_date:
            to_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        
        data = await self._fetch("/calendar/earnings", {
            "from": from_date,
            "to": to_date
        })
        
        earnings = data.get("earningsCalendar", [])
        
        return [{
            "symbol": e.get("symbol"),
            "date": e.get("date"),
            "eps_estimate": e.get("epsEstimate"),
            "eps_actual": e.get("epsActual"),
            "revenue_estimate": e.get("revenueEstimate"),
            "hour": e.get("hour", "unknown")
        } for e in earnings[:50]]


class FinnhubStreamHandler:
    """
    WebSocket Handler for Real-time Trades.
    Docs: https://finnhub.io/docs/api/websocket-trades
    """
    
    WEBSOCKET_URL = "wss://ws.finnhub.io"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.url = f"{self.WEBSOCKET_URL}?token={api_key}"
    
    def get_subscription_message(self, symbol: str) -> dict:
        """Get message to subscribe to a symbol."""
        return {"type": "subscribe", "symbol": symbol}
        
    def get_unsubscription_message(self, symbol: str) -> dict:
        """Get message to unsubscribe from a symbol."""
        return {"type": "unsubscribe", "symbol": symbol}
    
    def parse_message(self, message: str) -> dict:
        """Parse incoming WebSocket message."""
        try:
            data = json.loads(message)
            if data.get("type") == "trade":
                # Finnhub sends batched trades
                trades = data.get("data", [])
                return {
                    "type": "trade",
                    "trades": [{
                        "symbol": t.get("s"),
                        "price": t.get("p"),
                        "volume": t.get("v"),
                        "timestamp": t.get("t")
                    } for t in trades]
                }
            elif data.get("type") == "ping":
                return {"type": "ping"}
            
            return {"type": "unknown", "raw": data}
            
        except json.JSONDecodeError:
            return {"type": "error", "message": "Invalid JSON"}

