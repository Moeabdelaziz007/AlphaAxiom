
import json
import asyncio
from typing import Any, Dict, Optional

class MockHeaders:
    def __init__(self, items=None):
        self._items = items or {}

    @staticmethod
    def new(items):
        return MockHeaders(dict(items))

    def items(self):
        return self._items.items()

class MockResponse:
    def __init__(self, body, headers=None, status=200):
        self._body = body
        self._headers = headers or {}
        self.status = status
        self.ok = 200 <= status < 300

    @staticmethod
    def new(body, headers=None):
        return MockResponse(body, headers)

    async def text(self):
        return self._body

    async def json(self):
        return json.loads(self._body)

class MockJSON:
    @staticmethod
    def stringify(obj):
        return json.dumps(obj)

    @staticmethod
    def parse(s):
        return json.loads(s)

class MockKV:
    def __init__(self):
        self.store = {}

    async def get(self, key):
        return self.store.get(key)

    async def put(self, key, value, expiration_ttl=None):
        self.store[key] = value

class MockEnv:
    def __init__(self):
        self.ALPACA_KEY = "test_key"
        self.ALPACA_SECRET = "test_secret"
        self.BRAIN_MEMORY = MockKV()
        self.TRADING_MODE = "SIMULATION"
        self.TELEGRAM_BOT_TOKEN = "test_token"
        self.TELEGRAM_CHAT_ID = "test_chat_id"

# Global mock fetch function
async def mock_fetch(url, method="GET", headers=None, body=None):
    if "alpaca" in url and "account" in url:
        return MockResponse(json.dumps({
            "portfolio_value": "100000",
            "buying_power": "200000",
            "cash": "100000",
            "equity": "100000",
            "daytrade_count": 0
        }))
    if "alpaca" in url and "positions" in url:
        return MockResponse(json.dumps([]))
    if "alpaca" in url and "bars" in url:
        return MockResponse(json.dumps({"bars": []}))
    if "alpaca" in url and "snapshot" in url:
        return MockResponse(json.dumps({
            "dailyBar": {"c": 150.0, "v": 1000},
            "prevDailyBar": {"c": 149.0}
        }))
    if "telegram" in url:
        return MockResponse(json.dumps({"ok": True}))

    return MockResponse(json.dumps({}))

# Install mocks into sys.modules
import sys
from unittest.mock import MagicMock

# Create a mock js module
mock_js = MagicMock()
mock_js.Response = MockResponse
mock_js.Headers = MockHeaders
mock_js.JSON = MockJSON
mock_js.fetch = mock_fetch

sys.modules["js"] = mock_js
