"""
AQT Custom Runner - Orchestrates MCP Server + Intelligence Spiders
Run with: python run_aqt.py
"""

import asyncio
import uvicorn
from connector.mcp_server import mcp
from connector.spiders.news_spider import NewsSpider

# Initialize Spider with callback
def news_callback(source: str, title: str, link: str):
    """Callback when news is found - logs to stdout (captured by MCP)."""
    print(f"[NEWS] {source}: {title}")

spider = NewsSpider(on_news=news_callback, interval=60)


async def main():
    """Main entry point - runs MCP Server + Spiders concurrently."""
    
    print("=" * 50)
    print("🚀 AQT Engine Starting...")
    print("   - MCP Server: http://0.0.0.0:8766/sse")
    print("   - News Spider: Active (60s interval)")
    print("=" * 50)
    
    # Spider Task
    spider_task = asyncio.create_task(spider.start())
    
    # MCP Server Task (using uvicorn on the FastMCP ASGI app)
    # FastMCP exposes .sse_app() method for Starlette ASGI app
    app = mcp.sse_app()
    
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=8766, 
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    # Run both concurrently
    await asyncio.gather(
        spider_task,
        server.serve()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        spider.stop()
        print("\n🛑 AQT System Shutdown")
