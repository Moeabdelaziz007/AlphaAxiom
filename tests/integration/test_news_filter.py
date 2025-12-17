import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from engine.news_filter import NewsFilter, NewsSentinel

@pytest.fixture
def news_filter():
    return NewsFilter(api_key="test_key")

@pytest.mark.asyncio
async def test_news_filter_red_folder(news_filter):
    """
    Scenario: Mock Perplexity API response with Red Folder = True.
    Verify engine detects high risk.
    """

    mock_response_data = {
        "choices": [{
            "message": {
                "content": """
                ```json
                {
                    "fomc_event": true,
                    "cpi_event": false,
                    "major_hack": false,
                    "sec_action": false,
                    "stablecoin_risk": false,
                    "war_escalation": false,
                    "red_folder_warning": true,
                    "sentiment_score": -0.8,
                    "risk_level": "EXTREME",
                    "summary": "FOMC meeting today creates high volatility risk."
                }
                ```
                """
            }
        }]
    }

    # Mock the httpx client post method
    with patch.object(news_filter.client, 'post', new_callable=AsyncMock) as mock_post:
        # Create a mock response object
        mock_response = MagicMock()
        # json() is a sync method on httpx.Response
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        # post() returns the mock_response (awaitable because mock_post is AsyncMock)
        mock_post.return_value = mock_response

        sentinel = await news_filter.analyze_sentiment("BTCUSD")

        assert sentinel.red_folder_warning is True
        assert sentinel.risk_level == "EXTREME"
        assert sentinel.sentiment_score == -0.8
        assert "FOMC" in sentinel.summary

@pytest.mark.asyncio
async def test_news_filter_safe_conditions(news_filter):
    """Scenario: Safe market conditions."""

    mock_response_data = {
        "choices": [{
            "message": {
                "content": """
                ```json
                {
                    "red_folder_warning": false,
                    "sentiment_score": 0.5,
                    "risk_level": "LOW",
                    "summary": "Market is stable."
                }
                ```
                """
            }
        }]
    }

    with patch.object(news_filter.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        sentinel = await news_filter.analyze_sentiment("BTCUSD")

        assert sentinel.red_folder_warning is False
        assert sentinel.risk_level == "LOW"

@pytest.mark.asyncio
async def test_news_filter_api_failure(news_filter):
    """Scenario: API failure should fallback to safe/unknown."""

    with patch.object(news_filter.client, 'post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("API Timeout")

        sentinel = await news_filter.analyze_sentiment("BTCUSD")

        assert sentinel.risk_level == "UNKNOWN"
        assert "API Error" in sentinel.summary
