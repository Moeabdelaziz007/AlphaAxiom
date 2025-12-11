
import pytest
import asyncio
import json
import sys
import os

# Import mock environment first to set up sys.modules
from tests.mock_env import MockEnv, mock_js

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from routes import api, cron, telegram

@pytest.fixture
def env():
    return MockEnv()

@pytest.fixture
def headers():
    return mock_js.Headers.new({})

@pytest.mark.asyncio
async def test_api_account(env, headers):
    response = await api.get_account(env, headers)
    data = json.loads(await response.text())

    assert "portfolio_value" in data
    assert "cash" in data
    assert data["portfolio_value"] == "100000"

@pytest.mark.asyncio
async def test_api_positions(env, headers):
    response = await api.get_positions(env, headers)
    data = json.loads(await response.text())

    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_api_candles_default(env, headers):
    # Mock request
    class MockRequest:
        url = "http://localhost/api/candles"

    response = await api.get_candles(MockRequest(), env, headers)
    data = json.loads(await response.text())

    assert "symbol" in data
    assert "candles" in data
    assert data["symbol"] == "SPY"

@pytest.mark.asyncio
async def test_cron_panic_mode(env):
    # Set panic mode
    await env.BRAIN_MEMORY.put("panic_mode", "true")

    # Run scheduled task
    await cron.on_scheduled(None, env)

    # Check if maintenance ran (we can't easily spy on internal calls without more complex mocking,
    # but we can verify it didn't crash)

    # Verify panic mode is still true
    val = await env.BRAIN_MEMORY.get("panic_mode")
    assert val == "true"

@pytest.mark.asyncio
async def test_telegram_webhook_start(env, headers):
    # Mock request for /start
    body = {
        "message": {
            "chat": {"id": 123},
            "text": "/start",
            "from": {"first_name": "TestUser"}
        }
    }

    class MockRequest:
        async def json(self):
            return body

    response = await telegram.handle_telegram_webhook(MockRequest(), env, headers)
    data = json.loads(await response.text())
    assert data["ok"] is True

@pytest.mark.asyncio
async def test_telegram_panic_commands(env, headers):
    # Test /stoptrade
    stop_body = {
        "message": {
            "chat": {"id": 123},
            "text": "/stoptrade",
            "from": {"first_name": "TestUser"}
        }
    }

    class MockRequestStop:
        async def json(self):
            return stop_body

    await telegram.handle_telegram_webhook(MockRequestStop(), env, headers)
    assert await env.BRAIN_MEMORY.get("panic_mode") == "true"

    # Test /starttrade
    start_body = {
        "message": {
            "chat": {"id": 123},
            "text": "/starttrade",
            "from": {"first_name": "TestUser"}
        }
    }

    class MockRequestStart:
        async def json(self):
            return start_body

    await telegram.handle_telegram_webhook(MockRequestStart(), env, headers)
    assert await env.BRAIN_MEMORY.get("panic_mode") == "false"
