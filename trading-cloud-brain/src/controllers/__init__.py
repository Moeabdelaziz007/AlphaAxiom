"""
Controllers __init__.py
Exposes all controller handlers.
"""

from controllers.news import (
    handle_news_push,
    handle_news_latest
)

from controllers.briefing import (
    handle_briefing_save,
    handle_briefing_latest
)

from controllers.health import (
    handle_healthz,
    handle_status
)

__all__ = [
    # News
    "handle_news_push",
    "handle_news_latest",
    # Briefing
    "handle_briefing_save",
    "handle_briefing_latest",
    # Health
    "handle_healthz",
    "handle_status",
]
