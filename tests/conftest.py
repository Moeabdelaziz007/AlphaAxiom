import sys
from unittest.mock import MagicMock, AsyncMock
import pytest
import os

# Mock the 'js' module for Cloudflare Workers
class MockJs:
    fetch = AsyncMock()

sys.modules['js'] = MockJs()

# Mock the 'pyodide' module if needed (often used with js in Workers)
sys.modules['pyodide'] = MagicMock()

# --- PATH SETUP ---
# We need to support two types of imports found in the codebase:
# 1. `from engine.cipher` (Relative to src/)
# 2. `from src.brokers` (Absolute from project root)

# Add 'trading-cloud-brain/src' to allow `from engine import ...`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../trading-cloud-brain/src')))

# Add 'trading-cloud-brain' to allow `from src.brokers import ...`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../trading-cloud-brain')))

# Define a fixture for the mock exchange
@pytest.fixture
def mock_exchange():
    exchange = MagicMock()
    exchange.get_price = AsyncMock(return_value=100.0)
    exchange.get_balance = AsyncMock(return_value=10000.0)
    exchange.buy = AsyncMock(return_value={'id': '123', 'status': 'filled'})
    exchange.sell = AsyncMock(return_value={'id': '124', 'status': 'filled'})
    return exchange

# Define a fixture for the mock database
@pytest.fixture
def mock_db():
    db = MagicMock()
    db.get_user = AsyncMock(return_value={'id': 'user1', 'risk_score': 0.5})
    db.save_trade = AsyncMock()
    return db

# Fixture for JS fetch
@pytest.fixture
def mock_fetch(mocker):
    # Reset the mock before each test
    MockJs.fetch.reset_mock()
    return MockJs.fetch
