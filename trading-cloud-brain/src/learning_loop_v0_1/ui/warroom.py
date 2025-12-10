"""
Dialectic War Room - Real-time visualization and SSE streaming.
Provides the "Consciousness" streaming for the frontend UI.
"""

import asyncio
import json
import random
from typing import Dict, Any, AsyncGenerator, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class DialecticEvent:
    """Event structure for SSE streaming"""
    event_type: str  # "CORE_TOKEN", "SHADOW_TOKEN", "SYNTHESIS", "DECISION"
    payload: str
    timestamp: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_sse(self) -> str:
        """Format as Server-Sent Event"""
        data = json.dumps(asdict(self), ensure_ascii=False)
        return f"data: {data}\n\n"


class DialecticWarRoom:
    """
    Main orchestrator for the War Room visualization.
    Handles real-time streaming of dialectic reasoning.
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.event_listeners: List[Callable] = []
        
        # Simulated market scenarios for demo
        self._scenarios = [
            {
                "condition": "bullish_breakout",
                "core_thesis": "RSI oversold bounce detected at 28.5. Volume 150% above average. Breaking resistance at $95,000. High conviction LONG setup.",
                "shadow_critique": "Thin orderbook above $95,000. Only 5 BTC liquidity. High funding rates suggest long liquidation cascade risk. Recent false breakouts at this level.",
                "synthesis": "CAUTIOUS_LONG with tight stop-loss at $94,000 and reduced position size (50%)."
            },
            {
                "condition": "bearish_divergence",
                "core_thesis": "Price making higher highs but RSI making lower highs. Classic bearish divergence. SHORT opportunity with 2:1 RR.",
                "shadow_critique": "Strong spot buying on Coinbase. Institutional accumulation detected. Divergences can extend for weeks in trending markets.",
                "synthesis": "WAIT for confirmation. Set alert at $93,500 support break."
            },
            {
                "condition": "ranging_chop",
                "core_thesis": "Price in compression pattern. Bollinger Bands squeezing. Breakout imminent. Prepare for volatility expansion.",
                "shadow_critique": "Low volume environment. False breakouts common in compression. Whipsaws likely to stop out both sides.",
                "synthesis": "NO_TRADE. Capital preservation mode. Wait for clear direction."
            },
            {
                "condition": "macro_event",
                "core_thesis": "CPI data release in 2 hours. Historical tendency for BTC pump post-CPI. Pre-position for move.",
                "shadow_critique": "Macro events are unpredictable. 50/50 outcome. Position sizing should reflect uncertainty.",
                "synthesis": "REDUCE_EXPOSURE to 25% of normal. Wait for post-announcement direction."
            }
        ]
    
    def start_dialectic_session(
        self, 
        session_id: str, 
        market_data: Dict[str, Any]
    ) -> None:
        """Start a new dialectic session"""
        self.active_sessions[session_id] = {
            "started_at": datetime.now().isoformat(),
            "market_data": market_data,
            "status": "in_progress"
        }
        logger.info(f"Dialectic session started: {session_id}")
    
    def complete_dialectic_cycle(
        self, 
        session_id: str, 
        result: Dict[str, Any]
    ) -> None:
        """Complete a dialectic cycle with result"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = "completed"
            self.active_sessions[session_id]["result"] = result
            logger.info(f"Dialectic session completed: {session_id}")
    
    async def stream_dialectic_reasoning(
        self,
        market_data: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream the dialectic reasoning process token-by-token.
        This creates the "Consciousness" effect in the UI.
        """
        # Select a scenario based on market conditions or random for demo
        scenario = random.choice(self._scenarios)
        
        session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_dialectic_session(session_id, market_data or {})
        
        # Stream: Session Start
        yield DialecticEvent(
            event_type="SESSION_START",
            payload=session_id,
            timestamp=datetime.now().isoformat(),
            metadata={"condition": scenario["condition"]}
        ).to_sse()
        
        await asyncio.sleep(0.5)
        
        # Stream: Core Thesis (Token by Token)
        yield DialecticEvent(
            event_type="PHASE_START",
            payload="CORE",
            timestamp=datetime.now().isoformat()
        ).to_sse()
        
        core_confidence = random.uniform(0.7, 0.95)
        for word in scenario["core_thesis"].split():
            yield DialecticEvent(
                event_type="CORE_TOKEN",
                payload=word + " ",
                timestamp=datetime.now().isoformat(),
                confidence=core_confidence
            ).to_sse()
            await asyncio.sleep(random.uniform(0.03, 0.08))
        
        yield DialecticEvent(
            event_type="PHASE_END",
            payload="CORE",
            timestamp=datetime.now().isoformat(),
            confidence=core_confidence
        ).to_sse()
        
        await asyncio.sleep(0.3)
        
        # Stream: Shadow Critique (Token by Token)
        yield DialecticEvent(
            event_type="PHASE_START",
            payload="SHADOW",
            timestamp=datetime.now().isoformat()
        ).to_sse()
        
        shadow_regret = random.uniform(0.3, 0.8)
        for word in scenario["shadow_critique"].split():
            yield DialecticEvent(
                event_type="SHADOW_TOKEN",
                payload=word + " ",
                timestamp=datetime.now().isoformat(),
                confidence=shadow_regret
            ).to_sse()
            await asyncio.sleep(random.uniform(0.03, 0.08))
        
        yield DialecticEvent(
            event_type="PHASE_END",
            payload="SHADOW",
            timestamp=datetime.now().isoformat(),
            confidence=shadow_regret
        ).to_sse()
        
        await asyncio.sleep(0.5)
        
        # Stream: Synthesis
        yield DialecticEvent(
            event_type="PHASE_START",
            payload="SYNTHESIS",
            timestamp=datetime.now().isoformat()
        ).to_sse()
        
        # Calculate E_score
        e_score = core_confidence - (shadow_regret * 1.2)
        
        for word in scenario["synthesis"].split():
            yield DialecticEvent(
                event_type="SYNTHESIS_TOKEN",
                payload=word + " ",
                timestamp=datetime.now().isoformat()
            ).to_sse()
            await asyncio.sleep(random.uniform(0.05, 0.1))
        
        # Stream: Final Decision
        decision = self._determine_decision(e_score)
        
        yield DialecticEvent(
            event_type="DECISION",
            payload=decision,
            timestamp=datetime.now().isoformat(),
            confidence=max(0, min(1, e_score)),
            metadata={
                "core_confidence": round(core_confidence, 3),
                "shadow_regret": round(shadow_regret, 3),
                "e_score": round(e_score, 3),
                "condition": scenario["condition"]
            }
        ).to_sse()
        
        self.complete_dialectic_cycle(session_id, {
            "decision": decision,
            "e_score": e_score
        })
        
        # Stream: Session End
        yield DialecticEvent(
            event_type="SESSION_END",
            payload=session_id,
            timestamp=datetime.now().isoformat()
        ).to_sse()
    
    def _determine_decision(self, e_score: float) -> str:
        """Determine trading decision based on E_score"""
        if e_score > 0.5:
            return "EXECUTE_FULL"
        elif e_score > 0.3:
            return "EXECUTE_REDUCED"
        elif e_score > 0.1:
            return "HOLD_WAIT"
        else:
            return "BLOCK_TRADE"
    
    async def get_live_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics for UI"""
        return {
            "active_sessions": len(self.active_sessions),
            "system_status": "OPERATIONAL",
            "last_decision": self._get_last_decision(),
            "metrics": {
                "generation": random.randint(25, 35),
                "population_size": 128,
                "mutation_rate": round(random.uniform(0.05, 0.1), 3),
                "best_fitness": round(random.uniform(0.92, 0.98), 3)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_last_decision(self) -> Optional[Dict[str, Any]]:
        """Get the most recent decision"""
        if not self.active_sessions:
            return None
        
        latest = max(
            self.active_sessions.items(),
            key=lambda x: x[1].get("started_at", "")
        )
        return latest[1].get("result")


# Standalone async generator for testing
async def demo_stream():
    """Demo streaming for testing"""
    war_room = DialecticWarRoom()
    async for event in war_room.stream_dialectic_reasoning():
        print(event, end="")


if __name__ == "__main__":
    asyncio.run(demo_stream())