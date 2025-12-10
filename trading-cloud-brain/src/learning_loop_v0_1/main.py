"""
Main Orchestration Module for AlphaAxiom v0.1 Beta Self-Play Learning Loop
Integrates all components of the dialectic intelligence system.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import all components (v0.1 Beta)
from learning_loop_v0_1.dialectic.unified_model import UnifiedDialecticModel, DialecticSynthesis
from learning_loop_v0_1.memory.hybrid_memory import HybridMemory, MarketSnapshot, DialecticSession
from learning_loop_v0_1.protection.circuit_breaker import CircuitBreakerSystem
from learning_loop_v0_1.evolution.genetic_engine import DifferentialEvolutionEngine
from learning_loop_v0_1.ui.warroom import DialecticWarRoom

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlphaAxiomOrchestrator:
    """
    Main orchestrator for the AlphaAxiom v0.1 Beta Self-Play Learning Loop.
    Coordinates all components of the dialectic intelligence system.
    """
    
    def __init__(self, d1_db=None, r2_bucket=None):
        """Initialize all system components"""
        self.dialectic_model = UnifiedDialecticModel()
        self.circuit_breakers = CircuitBreakerSystem()
        self.hybrid_memory = HybridMemory(d1_db, r2_bucket)
        self.evolution_engine = DifferentialEvolutionEngine()
        self.war_room = DialecticWarRoom()
        
        # Initialize population for evolution
        self.evolution_engine.initialize_population()
        
        logger.info("AlphaAxiom v0.1 Beta Self-Play Learning Loop initialized")
    
    async def process_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming market data through the complete dialectic pipeline.
        
        Args:
            market_data: Current market conditions and context
            
        Returns:
            Trading decision with execution weight and metadata
        """
        # Generate unique session ID
        session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Start visualization in War Room
            self.war_room.start_dialectic_session(session_id, market_data)
            
            # Check circuit breakers before proceeding
            # In a real implementation, we would pass actual portfolio values
            portfolio_value = 100000  # Placeholder
            initial_value = 100000    # Placeholder
            
            # For now, we'll simulate a simple execution function
            async def dummy_execution_func(signal):
                return {"status": "success", "executed": True}
            
            # Check if trading is allowed
            trade_status = await self.circuit_breakers.execute_trade(
                {"type": "dialectic_decision"}, 
                portfolio_value, 
                initial_value, 
                dummy_execution_func
            )
            
            if trade_status == "BLOCKED":
                logger.warning("Trade blocked by circuit breakers")
                return {
                    "status": "blocked",
                    "reason": "Circuit breakers tripped",
                    "session_id": session_id
                }
            
            # Step 1: Generate dialectic synthesis using GLM-4.6
            logger.info("Generating dialectic synthesis...")
            dialectic_synthesis = await self.dialectic_model.generate_dialectic(market_data)
            
            # Step 2: Store market snapshot in hybrid memory
            logger.info("Storing market snapshot...")
            market_snapshot = MarketSnapshot(
                snapshot_id=session_id,
                timestamp=datetime.now(),
                price_data=market_data.get("price_data", {}),
                orderbook_data=market_data.get("orderbook", {}),
                news_sentiment=market_data.get("news", {}),
                technical_indicators=market_data.get("indicators", {}),
                macro_data=market_data.get("macro", {}),
                metadata={
                    "source": "live_trading",
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            await self.hybrid_memory.store_market_snapshot(market_snapshot)
            
            # Step 3: Create dialectic session record
            logger.info("Creating dialectic session record...")
            dialectic_session = DialecticSession(
                session_id=session_id,
                snapshot_uuid=session_id,
                timestamp=datetime.now(),
                market_condition=market_data.get("market_condition", "normal"),
                debate_intensity=0.75,  # Placeholder value
                outcome_confidence=dialectic_synthesis.execution_weight,
                core_reasoning_chain=[dialectic_synthesis.core_thesis.argument],
                shadow_counterpoints=[dialectic_synthesis.shadow_antithesis.argument],
                synthesis_process={"synthesis": dialectic_synthesis.final_synthesis},
                embeddings={
                    "core": [],  # In a real implementation, we would generate embeddings
                    "shadow": [],
                    "combined": []
                },
                metadata={
                    "model_version": self.dialectic_model.model_name,
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            await self.hybrid_memory.store_dialectic_session(dialectic_session)
            
            # Step 4: Complete dialectic cycle in War Room
            self.war_room.complete_dialectic_cycle(session_id, {
                "core_confidence": dialectic_synthesis.core_thesis.confidence,
                "shadow_regret": dialectic_synthesis.shadow_antithesis.confidence,
                "decision": dialectic_synthesis.final_synthesis,
                "execution_weight": dialectic_synthesis.execution_weight
            })
            
            # Step 5: Prepare result
            result = {
                "status": "success",
                "session_id": session_id,
                "decision": {
                    "core_thesis": {
                        "argument": dialectic_synthesis.core_thesis.argument,
                        "confidence": dialectic_synthesis.core_thesis.confidence
                    },
                    "shadow_antithesis": {
                        "argument": dialectic_synthesis.shadow_antithesis.argument,
                        "confidence": dialectic_synthesis.shadow_antithesis.confidence
                    },
                    "synthesis": dialectic_synthesis.final_synthesis,
                    "execution_weight": dialectic_synthesis.execution_weight,
                    "tool_calls": dialectic_synthesis.tool_calls
                },
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "model_used": self.dialectic_model.model_name
                }
            }
            
            logger.info(f"Dialectic process completed for session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing market data: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id
            }
    
    async def run_evolution_cycle(self, crime_scenes: Optional[list] = None):
        """
        Run one cycle of the evolutionary optimization process.
        
        Args:
            crime_scenes: Historical market snapshots for evaluation (optional)
            
        Returns:
            Evolution cycle results
        """
        try:
            logger.info("Starting evolution cycle...")
            
            # If no crime scenes provided, use recent snapshots from memory
            if crime_scenes is None:
                # In a real implementation, we would fetch recent snapshots
                crime_scenes = [{"id": f"SIM_{i}", "data": f"simulated_crime_scene_{i}"} 
                              for i in range(10)]
            
            # Evolve the population for one generation
            self.evolution_engine.evolve_generation(crime_scenes)
            
            # Check for shadow deployment candidate
            candidate = self.evolution_engine.get_shadow_deployment_candidate()
            
            result = {
                "status": "success",
                "generation": self.evolution_engine.generation,
                "population_size": len(self.evolution_engine.population),
                "best_fitness": self.evolution_engine.best_strategy.fitness_score if self.evolution_engine.best_strategy else 0,
                "shadow_deployment_candidate": candidate is not None,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Evolution cycle completed - Generation {self.evolution_engine.generation}")
            return result
            
        except Exception as e:
            logger.error(f"Error in evolution cycle: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current status of all system components.
        
        Returns:
            System status information
        """
        try:
            # Get memory statistics
            memory_stats = await self.hybrid_memory.get_memory_statistics()
            
            # Get circuit breaker statuses
            breaker_statuses = {}
            for name, breaker in self.circuit_breakers.breakers.items():
                breaker_statuses[name] = {
                    "state": breaker.state.value if hasattr(breaker.state, 'value') else str(breaker.state),
                    "failure_count": getattr(breaker, 'failure_count', 0),
                    "last_failure": getattr(breaker, 'last_failure_time', 0)
                }
            
            # Get evolution engine status
            evolution_status = {
                "generation": self.evolution_engine.generation,
                "population_size": len(self.evolution_engine.population),
                "best_fitness": self.evolution_engine.best_strategy.fitness_score if self.evolution_engine.best_strategy else 0
            }
            
            return {
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "dialectic_model": {
                        "model_name": self.dialectic_model.model_name,
                        "status": "ready"
                    },
                    "hybrid_memory": memory_stats,
                    "circuit_breakers": breaker_statuses,
                    "evolution_engine": evolution_status,
                    "war_room": {
                        "active_sessions": len(self.war_room.active_sessions),
                        "event_listeners": len(self.war_room.event_listeners)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Example usage and testing
async def main():
    """Example usage of the AlphaAxiomOrchestrator"""
    # Initialize the orchestrator
    orchestrator = AlphaAxiomOrchestrator()
    
    # Example market data
    market_data = {
        "symbol": "BTCUSDT",
        "price": 95000,
        "volume": 1250000000,
        "market_condition": "bullish",
        "price_data": {
            "open": 94500,
            "high": 95500,
            "low": 94200,
            "close": 95000,
            "volume": 1250000000
        },
        "orderbook": {
            "bids": [[94990, 2.5], [94980, 3.1], [94970, 1.8]],
            "asks": [[95010, 1.2], [95020, 2.3], [95030, 1.5]]
        },
        "news": {
            "sentiment_score": 0.65,
            "recent_articles": [
                "Bitcoin ETF approval rumors boost investor confidence",
                "Institutional adoption of crypto continues to rise"
            ]
        },
        "indicators": {
            "rsi": 62.3,
            "macd": 1250.75,
            "atr": 850.25
        },
        "macro": {
            "fed_rate_expectation": "neutral",
            "inflation_data": "decreasing"
        }
    }
    
    print("=== AlphaAxiom v1.0 Self-Play Learning Loop ===")
    print("Processing market data...")
    
    # Process market data through the dialectic pipeline
    result = await orchestrator.process_market_data(market_data)
    print(f"Processing result: {json.dumps(result, indent=2)}")
    
    print("\nRunning evolution cycle...")
    # Run evolution cycle
    evolution_result = await orchestrator.run_evolution_cycle()
    print(f"Evolution result: {json.dumps(evolution_result, indent=2)}")
    
    print("\nGetting system status...")
    # Get system status
    status = await orchestrator.get_system_status()
    print(f"System status: {json.dumps(status, indent=2)}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())