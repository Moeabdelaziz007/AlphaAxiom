"""
Causal Learning Bridge v1.0
AlphaAxiom Learning Loop v2.0

The Integration Layer that connects:
- Telegram Bot Commands to AlphaMCP Tools
- Causal Inference Engine to Decision Analysis
- Learning Loop to Self-Improvement
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum
import json  # noqa: F401
import logging

# Add the new imports for ExecutionRouter
from .price_cache import PriceCache
from brokers import BinanceConnector

# Add import for ReferenceMemory
from ..memory.reference_memory import ReferenceMemory

# Add import for CounterfactualVisionEngine
from ..engines.counterfactual import CounterfactualVisionEngine


class ToolCategory(Enum):
    RISK = "risk"
    ANALYSIS = "analysis"
    STRATEGY = "strategy"
    INFO = "info"


class DecisionType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    ADJUST = "adjust"


@dataclass
class ToolCall:
    tool_name: str
    category: ToolCategory
    parameters: dict
    result: dict
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0


@dataclass
class CausalDecision:
    decision_id: str
    decision_type: DecisionType
    symbol: str
    confidence: float
    tool_calls: list
    causal_factors: dict
    counterfactual_analysis: dict
    expected_outcome: float
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DecisionOutcome:
    decision_id: str
    actual_outcome: float
    expected_outcome: float
    prediction_error: float
    was_correct: bool
    outcome_time: datetime = field(default_factory=datetime.now)


class CausalLearningBridge:
    """
    Main integration layer connecting:
    - Telegram commands to AlphaMCP tools
    - Decisions to Causal Inference analysis
    - Outcomes to Learning Loop for self-improvement
    """
    
    TOOL_CATEGORIES = {
        "calculate_kelly_criterion": ToolCategory.RISK,
        "advanced_rsi_analysis": ToolCategory.ANALYSIS,
        "alphaaxiom_market_analysis": ToolCategory.ANALYSIS,
        "intelligent_position_sizing": ToolCategory.RISK,
        "portfolio_risk_assessment": ToolCategory.RISK,
        "multi_timeframe_analysis": ToolCategory.ANALYSIS,
        "strategy_backtest_simulation": ToolCategory.STRATEGY,
        "get_server_info": ToolCategory.INFO,
        "market_calendar_today": ToolCategory.INFO,
    }
    
    def __init__(
        self,
        kv_store: Optional[Any] = None,
        d1_database: Optional[Any] = None,
        telegram_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ):
        self.kv = kv_store
        self.d1 = d1_database
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self._causal_engine = None
        self._mcp_tools = None
        self._pending_decisions: Dict[str, 'CausalDecision'] = {}
        self._decision_history: List['CausalDecision'] = []
        self._accuracy_by_tool: Dict[str, float] = {}
        self._tool_usage_count: Dict[str, int] = {}
        self._brokers: Dict[str, Any] = {}
        
        # Initialize ExecutionRouter 
        # components
        self._price_cache = PriceCache(default_ttl_seconds=30)
        self._brokers = {}
        self._initialize_brokers()
        
        # Initialize CounterfactualVisionEngine
        self._counterfactual_engine = CounterfactualVisionEngine(
            d1_db=d1_database, kv_store=kv_store
        )
    
    def _initialize_brokers(self):
        """Initialize broker connectors for smart routing."""
        # Placeholder API keys - these would be loaded from
        # environment in production
        self._brokers["Binance"] = BinanceConnector(
            api_key="PLACEHOLDER_BINANCE_API_KEY",
            api_secret="PLACEHOLDER_BINANCE_API_SECRET"
        )
        
        # Add other brokers as needed
        # self._brokers["Bybit"] = BybitConnector(...) etc.
    
    @property
    def causal_engine(self):
        if self._causal_engine is None:
            try:
                from learning_loop_v2.core.causal_inference import \
                    CausalInferenceEngine
            except ImportError:
                # Fallback for environments where 
                # causal_inference module is not available
                class CausalInferenceEngine:
                    pass
            self._causal_engine = CausalInferenceEngine(
                kv_store=self.kv, d1_database=self.d1
            )
        return self._causal_engine
    
    @property
    def mcp_tools(self):
        if self._mcp_tools is None:
            try:
                from alpha_mcp import moe_axiom_tools
                self._mcp_tools = moe_axiom_tools
            except ImportError:
                self._mcp_tools = None
        return self._mcp_tools
    
    async def execute_tool(self, tool_name: str, parameters: dict) -> ToolCall:
        """Execute an AlphaMCP tool and record the call."""
        start_time = datetime.now()
        
        if self.mcp_tools is None:
            return ToolCall(
                tool_name=tool_name, category=ToolCategory.INFO,
                parameters=parameters,
                result={"error": "MCP tools not available"},
                execution_time_ms=0
            )
        
        tool_func = getattr(self.mcp_tools, tool_name, None)
        if tool_func is None:
            return ToolCall(
                tool_name=tool_name, category=ToolCategory.INFO,
                parameters=parameters,
                result={"error": f"Tool {tool_name} not found"},
                execution_time_ms=0
            )
        
        try:
            result = tool_func(**parameters)
        except Exception as e:
            result = {"error": str(e)}
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        self._tool_usage_count[tool_name] = \
            self._tool_usage_count.get(tool_name, 0) + 1
        
        return ToolCall(
            tool_name=tool_name,
            category=self.TOOL_CATEGORIES.get(tool_name, ToolCategory.INFO),
            parameters=parameters, result=result,
            execution_time_ms=execution_time
        )

    async def make_causal_decision(
            self, symbol: str, context: dict) -> CausalDecision:
        """Make a trading decision using causal analysis."""
        import uuid
        decision_id = str(uuid.uuid4())[:8]
        tool_calls = []
        
        # Gather data from tools
        if "prices" in context:
            tool_calls.append(await self.execute_tool(
                "advanced_rsi_analysis", {"prices": context["prices"]}
            ))
        
        if all(k in context for k in [
                "current_price", "volume", "volatility"]):
            tool_calls.append(await self.execute_tool(
                "alphaaxiom_market_analysis", {
                    "symbol": symbol,
                    "current_price": context.get("current_price", 0),
                    "volume": context.get("volume", 1.0),
                    "volatility": context.get("volatility", 0.02),
                    "news_sentiment": context.get(
                        "news_sentiment", "neutral"),
                    "social_sentiment": context.get(
                        "social_sentiment", "neutral")
                }
            ))
        
        # Causal analysis
        observations = self._tools_to_observations(tool_calls, context)
        causal_analysis = await self.causal_engine.analyze_trading_causality(
            trading_data=observations,
            signal_variable="signal", 
            return_variable="return"
        )
        
        decision_type, confidence = self._synthesize_decision(
            tool_calls, causal_analysis)
        
        # Counterfactual
        counterfactual = {}
        if observations:
            cf = await self.causal_engine.compute_counterfactual(
                observation=observations[-1],
                intervention={
                    "signal": 1.0 
                    if decision_type == DecisionType.BUY
                    else 0.0
                },
                outcome_variable="return"
            )
            counterfactual = {
                "factual_outcome": cf.factual_outcome,
                "counterfactual_outcome": cf.counterfactual_outcome,
                "causal_effect": cf.causal_effect
            }
        
        expected = self._calculate_expected_outcome(
            tool_calls, causal_analysis, counterfactual)
        reasoning = self._generate_reasoning(
            symbol, tool_calls, causal_analysis, decision_type)
        
        # Counterfactual Vision Engine Analysis
        # Evaluate the decision using counterfactual analysis before finalizing
        current_price = context.get("current_price", 0)
        historical_prices = context.get("prices", [])
        
        if self._counterfactual_engine and current_price > 0 and len(historical_prices) > 10:
            # Run counterfactual analysis
            scenario = await self._counterfactual_engine.evaluate_decision(
                symbol=symbol,
                action=decision_type.value.upper(),
                current_price=current_price,
                context=context
            )
            
            # Check if decision should be rejected based on regret cost
            if self._counterfactual_engine.should_reject_decision(scenario):
                # Reject the decision - change to HOLD
                decision_type = DecisionType.HOLD
                confidence = min(confidence, 0.3)  # Reduce confidence
                reasoning = f"REJECTED: High regret cost ({scenario.regret_cost:.2%}) - {symbol}"
                
                # Update counterfactual analysis with rejection info
                counterfactual["regret_cost"] = scenario.regret_cost
                counterfactual["decision_rejected"] = True
        
        decision = CausalDecision(
            decision_id=decision_id, decision_type=decision_type,
            symbol=symbol, confidence=confidence, tool_calls=tool_calls,
            causal_factors={
                "causal_effect": causal_analysis.get("causal_effect"),
                "confounders": causal_analysis.get("confounders", []),
                "is_causal": causal_analysis.get("is_causal", False)
            },
            counterfactual_analysis=counterfactual,
            expected_outcome=expected, reasoning=reasoning
        )
        
        self._pending_decisions[decision_id] = decision
        self._decision_history.append(decision)
        return decision
    
    def _tools_to_observations(self, tool_calls, context):
        observations = []
        for tc in tool_calls:
            if tc.result.get("error"):
                continue
            obs = {"tool": tc.tool_name}
            if tc.tool_name == "advanced_rsi_analysis":
                rsi = tc.result.get("rsi_value", 50)
                obs["signal"] = 1.0 if rsi < 30 else (0.0 if rsi > 70 else 0.5)
            elif tc.tool_name == "alphaaxiom_market_analysis":
                obs["signal"] = tc.result.get("market_score", 0.5)
            obs["return"] = context.get("expected_return", 0.0)
            observations.append(obs)
        return observations
    
    def _synthesize_decision(self, tool_calls, causal_analysis):
        buy, sell = 0, 0
        for tc in tool_calls:
            if tc.result.get("error"):
                continue
            if tc.tool_name == "alphaaxiom_market_analysis":
                action = tc.result.get("action", "HOLD")
                if "BUY" in action:
                    buy += 1
                elif "SELL" in action:
                    sell += 1
        
        effect = causal_analysis.get("causal_effect")
        if effect and hasattr(effect, "ate") and effect.is_significant:
            if effect.ate > 0:
                buy += 1
            else:
                sell += 1
        
        total = buy + sell
        if total == 0:
            return DecisionType.HOLD, 0.5
        conf = max(buy, sell) / total
        if buy > sell:
            return DecisionType.BUY, conf
        if sell > buy:
            return DecisionType.SELL, conf
        return DecisionType.HOLD, 0.5
    
    def _calculate_expected_outcome(
            self, tool_calls, causal_analysis, counterfactual):
        effect = causal_analysis.get("causal_effect")
        if effect and hasattr(effect, "ate"):
            return effect.ate
        if counterfactual.get("causal_effect"):
            return counterfactual["causal_effect"]
        return 0.0
    
    def _generate_reasoning(
            self, symbol, tool_calls, causal_analysis, decision_type):
        emoji = {
            "buy": "BUY", "sell": "SELL", "hold": "HOLD", 
            "adjust": "ADJUST"}
        return f"{emoji.get(decision_type.value, '?')} {symbol}"

    async def record_outcome(
            self, decision_id: str, actual_outcome: float) -> DecisionOutcome:
        """Record outcome for learning."""
        decision = self._pending_decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        error = actual_outcome - decision.expected_outcome
        correct = (
            (decision.decision_type == DecisionType.BUY 
                and actual_outcome > 0) or
            (decision.decision_type == DecisionType.SELL 
                and actual_outcome < 0) or
            (decision.decision_type == DecisionType.HOLD 
                and abs(actual_outcome) < 0.01)
        )
        
        outcome = DecisionOutcome(
            decision_id=decision_id, actual_outcome=actual_outcome,
            expected_outcome=decision.expected_outcome,
            prediction_error=error, was_correct=correct
        )
        
        for tc in decision.tool_calls:
            self._update_tool_accuracy(tc.tool_name, correct)
        
        del self._pending_decisions[decision_id]
        return outcome
    
    def _update_tool_accuracy(self, tool_name, was_correct):
        current = self._accuracy_by_tool.get(tool_name, 0.5)
        count = self._tool_usage_count.get(tool_name, 1)
        alpha = 2 / (count + 1)
        self._accuracy_by_tool[tool_name] = (
            alpha * (1.0 if was_correct else 0.0) + 
            (1 - alpha) * current)
    
    async def get_learning_metrics(self):
        return {
            "total_decisions": len(self._decision_history),
            "pending_decisions": len(self._pending_decisions),
            "tool_accuracy": self._accuracy_by_tool,
            "tool_usage": self._tool_usage_count,
            "top_tools": sorted(
                self._accuracy_by_tool.items(), 
                key=lambda x: x[1], 
                reverse=True)[:3]
        }

    # Add ExecutionRouter methods here
    async def get_best_price(self, symbol: str, action: str) -> Dict[str, Any]:
        """
        Get the best price for a symbol across all available brokers.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            action: "buy" or "sell"
            
        Returns:
            Dictionary with best price info and broker name
        """
        best_price = None
        best_broker = None
        
        # Check cache first
        cache_key = f"best_price:{symbol}:{action}"
        cached = self._price_cache.get(cache_key)
        if cached:
            return cached
        
        # Get prices from all brokers
        for broker_name, broker in self._brokers.items():
            try:
                ticker = await broker.get_ticker(symbol)
                price = ticker.get(
                    "bid" if action.lower() == "sell" else "ask", 0
                )
                
                if price > 0:
                    if best_price is None:
                        best_price = price
                        best_broker = broker_name
                    elif (action.lower() == "buy" and price < best_price) or \
                         (action.lower() == "sell" and price > best_price):
                        best_price = price
                        best_broker = broker_name
            except Exception as e:
                logging.warning(
                    f"Failed to get price from {broker_name}: {str(e)}"
                )
                continue
        
        result = {
            "symbol": symbol,
            "action": action,
            "price": best_price,
            "broker": best_broker,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the result
        self._price_cache.put(cache_key, result)
        return result
    
    async def execute_arbitrage_opportunity(
        self, symbol: str, buy_broker: str, sell_broker: str, amount: float
    ) -> Dict[str, Any]:
        """
        Execute an arbitrage opportunity by buying on one broker and 
        selling on another.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            buy_broker: Name of broker to buy from
            sell_broker: Name of broker to sell to
            amount: Amount to trade
            
        Returns:
            Dictionary with execution results
        """
        if buy_broker not in self._brokers or sell_broker not in self._brokers:
            return {"error": "Invalid broker specified"}
        
        try:
            # Get current prices
            buy_ticker = await self._brokers[buy_broker].get_ticker(symbol)
            sell_ticker = await self._brokers[sell_broker].get_ticker(symbol)
            
            buy_price = buy_ticker.get("ask", 0)
            sell_price = sell_ticker.get("bid", 0)
            
            if buy_price <= 0 or sell_price <= 0:
                return {"error": "Invalid prices"}
            
            # Calculate potential profit
            profit = (sell_price - buy_price) * amount
            
            # Execute trades
            buy_order = await self._brokers[buy_broker].place_order(
                symbol, "buy", amount, price=buy_price
            )
            
            sell_order = await self._brokers[sell_broker].place_order(
                symbol, "sell", amount, price=sell_price
            )
            
            result = {
                "symbol": symbol,
                "buy_broker": buy_broker,
                "sell_broker": sell_broker,
                "amount": amount,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "potential_profit": profit,
                "buy_order": buy_order,
                "sell_order": sell_order,
                "status": "executed"
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Arbitrage execution failed: {str(e)}"}
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's trading preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user preferences
        """
        # In a real implementation, this would fetch from a database
        # For now, we'll return default preferences
        return {
            "preferred_brokers": ["Binance"],  # Default to Binance
            "max_slippage": 0.01,  # 1%
            "risk_tolerance": "moderate",
            "execution_strategy": "best_price"
        }
    
    async def execute_with_preferences(
        self, symbol: str, action: str, amount: float, user_id: str
    ) -> Dict[str, Any]:
        """
        Execute a trade respecting user preferences.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
            action: "buy" or "sell"
            amount: Amount to trade
            user_id: User identifier
            
        Returns:
            Dictionary with execution results
        """
        # Get user preferences
        preferences = await self.get_user_preferences(user_id)
        
        # Get best price according to preferences
        preferred_brokers = preferences.get("preferred_brokers", ["Binance"])
        
        best_price = None
        best_broker = None
        
        # Check preferred brokers first
        for broker_name in preferred_brokers:
            if broker_name in self._brokers:
                try:
                    ticker = await self._brokers[broker_name].\
                        get_ticker(symbol)
                    price = ticker.get(
                        "bid" if action.lower() == "sell" else "ask", 0
                    )
                    
                    if price > 0:
                        if best_price is None:
                            best_price = price
                            best_broker = broker_name
                        is_better_buy = (action.lower() == "buy" and
                            price < best_price)
                        is_better_sell = (action.lower() == "sell" and
                            price > best_price)
                        if is_better_buy or is_better_sell:
                            best_price = price
                            best_broker = broker_name
                except Exception as e:
                    logging.warning(
                        f"Failed to get price from {broker_name}: {str(e)}"
                    )
                    continue
        
        if best_broker is None:
            return {"error": "No suitable broker found"}
        
        # Execute the trade
        try:
            order = await self._brokers[best_broker].place_order(
                symbol, action, amount, price=best_price
            )
            
            return {
                "symbol": symbol,
                "action": action,
                "amount": amount,
                "price": best_price,
                "broker": best_broker,
                "order": order,
                "status": "executed"
            }
            
        except Exception as e:
            return {"error": f"Trade execution failed: {str(e)}"}

    async def handle_telegram_command(self, command: str, args: list) -> str:
        """Handle /mcp commands from Telegram."""
        if not command:
            return self._get_help()
        
        cmd = command.lower()
        if cmd == "status":
            info = self.mcp_tools.get_server_info() if self.mcp_tools else {}
            return (f"Server: {info.get('server_name', 'N/A')}, "
                    f"Tools: {info.get('total_tools', 0)}")
        elif cmd == "metrics":
            m = await self.get_learning_metrics()
            return (f"Decisions: {m['total_decisions']}, "
                    f"Pending: {m['pending_decisions']}")
        elif cmd == "kelly" and len(args) >= 3:
            result = await self.execute_tool("calculate_kelly_criterion", {
                "win_rate": float(args[0]), "avg_win": float(args[1]),
                "avg_loss": float(args[2]),
                "risk_aversion": args[3] if len(args) > 3 else "MODERATE"
            })
            return str(result.result)
        elif cmd == "decision" and args:
            d = await self.make_causal_decision(args[0].upper(), {
                "current_price": 1.0, "volume": 1.0, "volatility": 0.02,
                "news_sentiment": "neutral"
            })
            return (f"{d.decision_type.value.upper()} {d.symbol} "
                    f"(conf: {d.confidence:.1%})")
        return self._get_help()
    
    def _get_help(self):
        return ("Commands: /mcp status | metrics | "
                "kelly [wr] [win] [loss] | decision [symbol]")
