import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from adapters.mt5_adapter import MT5Adapter
import asyncio

@pytest.fixture
def mt5_adapter():
    return MT5Adapter(bridge_url="http://mock-mt5", auth_token="token")

@pytest.mark.asyncio
async def test_reconnection_logic_success(mt5_adapter):
    """Verify _ensure_connection retries and eventually succeeds."""

    # Mock self.connect() to fail twice then succeed
    mt5_adapter.connect = AsyncMock(side_effect=[False, False, True])

    # Run _ensure_connection
    # We patch sleep to avoid waiting real time
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        result = await mt5_adapter._ensure_connection(max_retries=3)

        assert result is True
        assert mt5_adapter.connect.call_count == 3
        # Should have slept twice (after 1st and 2nd failure)
        assert mock_sleep.call_count == 2

@pytest.mark.asyncio
async def test_reconnection_logic_failure(mt5_adapter):
    """Verify _ensure_connection fails after max retries."""

    # Mock self.connect() to always fail
    mt5_adapter.connect = AsyncMock(return_value=False)

    with patch('asyncio.sleep', new_callable=AsyncMock):
        result = await mt5_adapter._ensure_connection(max_retries=3)

        assert result is False
        assert mt5_adapter.connect.call_count == 3

@pytest.mark.asyncio
async def test_ensure_connection_already_connected(mt5_adapter):
    mt5_adapter._connected = True
    mt5_adapter.connect = AsyncMock()

    result = await mt5_adapter._ensure_connection()
    assert result is True
    mt5_adapter.connect.assert_not_called()
