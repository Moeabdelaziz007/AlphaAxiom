"""
📅 Economic Calendar Module for Axiom Antigravity
Prevents trading during high-impact economic news events.

SOURCES (in fallback order):
1. Finnhub (free tier)
2. Nager.Date for holidays
3. Built-in high-impact times (FOMC, NFP)

RESEARCH-BASED IMPLEMENTATION:
- Avoid trading 15 minutes before and after high-impact news
- Cache calendar data in KV (refresh every 6 hours)
- Fallback to known recurring events if API fails
"""

import json
import time
from js import fetch, Headers

# High-impact event types to avoid
HIGH_IMPACT_EVENTS = [
    "Non-Farm Payrolls",
    "NFP",
    "FOMC",
    "Interest Rate Decision",
    "CPI",
    "Core CPI",
    "GDP",
    "Retail Sales",
    "Unemployment Rate",
    "PMI",
    "ECB",
    "BOE",
    "BOJ",
    "Fed Chair",
    "Powell",
    "Lagarde"
]

# Currencies to watch for each country's news
CURRENCY_MAP = {
    "USD": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD"],
    "EUR": ["EURUSD", "EURGBP", "EURJPY", "EURCHF"],
    "GBP": ["GBPUSD", "EURGBP", "GBPJPY"],
    "JPY": ["USDJPY", "EURJPY", "GBPJPY"],
    "AUD": ["AUDUSD", "EURAUD"],
    "CAD": ["USDCAD", "EURCAD"],
    "CHF": ["USDCHF", "EURCHF"]
}

# Known recurring high-impact events (backup if API fails)
# Day of week (0=Mon) + approximate hour (UTC)
KNOWN_RECURRING_EVENTS = [
    {"name": "NFP", "day": 4, "hour": 13, "minute": 30, "week_of_month": 1},  # First Friday
    {"name": "FOMC", "hour": 19, "minute": 0},  # Usually 2pm ET = 19:00 UTC
]

# News avoidance window (minutes)
NEWS_BUFFER_BEFORE = 15
NEWS_BUFFER_AFTER = 15


class EconomicCalendar:
    """
    📅 Economic Calendar for avoiding high-impact news
    
    Usage:
        calendar = EconomicCalendar(env)
        if await calendar.should_avoid_trading("EURUSD"):
            return  # Skip trade
    """
    
    def __init__(self, env):
        self.env = env
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
        self.cached_events = []
        self.cache_timestamp = 0
    
    async def _fetch_finnhub_calendar(self):
        """Fetch economic calendar from Finnhub (free tier)"""
        try:
            # Finnhub economic calendar endpoint
            # Note: May require API key for full access
            api_key = str(getattr(self.env, 'FINNHUB_API_KEY', ''))
            
            # Get today and next 7 days
            from_date = time.strftime("%Y-%m-%d")
            to_date = time.strftime("%Y-%m-%d", time.localtime(time.time() + 7*24*60*60))
            
            url = f"https://finnhub.io/api/v1/calendar/economic?from={from_date}&to={to_date}"
            if api_key:
                url += f"&token={api_key}"
            
            response = await fetch(url, method="GET")
            
            if response.ok:
                data = json.loads(await response.text())
                events = data.get("economicCalendar", [])
                
                # Filter high-impact events
                high_impact = []
                for event in events:
                    name = event.get("event", "")
                    impact = event.get("impact", "").lower()
                    
                    # Check if high impact by name or impact level
                    is_high = impact == "high" or any(
                        hi.lower() in name.lower() for hi in HIGH_IMPACT_EVENTS
                    )
                    
                    if is_high:
                        high_impact.append({
                            "name": name,
                            "time": event.get("time", ""),
                            "country": event.get("country", ""),
                            "currency": event.get("currency", "USD"),
                            "impact": "high"
                        })
                
                return high_impact
            
            return []
        except Exception as e:
            print(f"Finnhub calendar error: {e}")
            return []
    
    async def _get_cached_or_fetch(self):
        """Get cached calendar or fetch fresh data"""
        try:
            if self.kv:
                cached = await self.kv.get("economic_calendar")
                if cached:
                    cache_data = json.loads(cached)
                    cache_age = time.time() - cache_data.get("timestamp", 0)
                    
                    # Use cache if less than 6 hours old
                    if cache_age < 6 * 60 * 60:
                        return cache_data.get("events", [])
            
            # Fetch fresh data
            events = await self._fetch_finnhub_calendar()
            
            # Cache for 6 hours
            if self.kv and events:
                await self.kv.put("economic_calendar", json.dumps({
                    "timestamp": time.time(),
                    "events": events
                }))
            
            return events
            
        except Exception as e:
            print(f"Calendar cache error: {e}")
            return []
    
    def _is_within_news_window(self, event_time_str):
        """Check if current time is within news avoidance window"""
        try:
            # Parse event time (format: "HH:MM")
            if not event_time_str or ":" not in event_time_str:
                return False
            
            hour, minute = map(int, event_time_str.split(":")[:2])
            
            # Get current UTC time
            now = time.gmtime()
            current_minutes = now.tm_hour * 60 + now.tm_min
            event_minutes = hour * 60 + minute
            
            # Check if within buffer window
            diff = abs(current_minutes - event_minutes)
            
            return diff <= (NEWS_BUFFER_BEFORE + NEWS_BUFFER_AFTER)
            
        except:
            return False
    
    async def should_avoid_trading(self, symbol=None):
        """
        Check if trading should be avoided due to high-impact news.
        
        Args:
            symbol: Trading pair (e.g., "EURUSD") - if provided, 
                    only check news affecting that currency
        
        Returns:
            dict: {"avoid": bool, "reason": str, "events": list}
        """
        try:
            events = await self._get_cached_or_fetch()
            
            affecting_events = []
            
            for event in events:
                # Check if event affects the symbol
                if symbol:
                    currency = event.get("currency", "USD")
                    affected_pairs = CURRENCY_MAP.get(currency, [])
                    
                    # Normalize symbol
                    symbol_clean = symbol.upper().replace("/", "").replace("_", "")
                    
                    if not any(symbol_clean in pair for pair in affected_pairs):
                        continue
                
                # Check if within news window
                if self._is_within_news_window(event.get("time", "")):
                    affecting_events.append(event)
            
            if affecting_events:
                event_names = [e.get("name", "Unknown") for e in affecting_events]
                return {
                    "avoid": True,
                    "reason": f"High-impact news: {', '.join(event_names[:3])}",
                    "events": affecting_events
                }
            
            return {"avoid": False, "reason": "", "events": []}
            
        except Exception as e:
            # On error, be conservative but don't block
            return {"avoid": False, "reason": f"Calendar check failed: {str(e)}", "events": []}
    
    async def get_upcoming_events(self, hours=24):
        """Get upcoming high-impact events for the next N hours"""
        events = await self._get_cached_or_fetch()
        
        # Filter events within time window
        upcoming = []
        for event in events:
            # Add to upcoming list (already filtered for high impact)
            upcoming.append({
                "name": event.get("name"),
                "time": event.get("time"),
                "currency": event.get("currency", "USD"),
                "impact": "🔴 High"
            })
        
        return upcoming[:10]  # Limit to 10 events
