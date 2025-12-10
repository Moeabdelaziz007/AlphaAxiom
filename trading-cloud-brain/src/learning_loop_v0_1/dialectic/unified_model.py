"""
Unified Dialectic Model for AlphaAxiom v4.0
Implements the cognitive core using GLM-4.6 with conditioned personas.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DialecticPersona:
    """Represents a cognitive persona in the dialectic process"""
    name: str
    role: str
    characteristics: List[str]
    objectives: List[str]


@dataclass
class DialecticArgument:
    """Represents an argument from a persona in the dialectic process"""
    persona: str
    argument: str
    confidence: float
    supporting_evidence: List[str] = field(default_factory=list)


@dataclass
class DialecticSynthesis:
    """Represents the synthesis of the dialectic debate"""
    core_thesis: DialecticArgument
    shadow_antithesis: DialecticArgument
    final_synthesis: str
    execution_weight: float
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedDialecticModel:
    """
    The cognitive core of AlphaAxiom v4.0 that implements a unified dialectic model
    using GLM-4.6 with conditioned personas for Core (Thesis) and Shadow (Antithesis).
    """
    
    def __init__(self, model_name: str = "glm-4.6"):
        """
        Initialize the Unified Dialectic Model.
        
        Args:
            model_name: Name of the foundation model to use (default: glm-4.6)
        """
        self.model_name = model_name
        self.personas = {
            "core": DialecticPersona(
                name="Core Agent",
                role="Thesis Generator",
                characteristics=[
                    "Aggressive alpha seeker",
                    "Optimistic trend follower",
                    "Focused on maximizing returns"
                ],
                objectives=[
                    "Identify high-conviction trade setups",
                    "Propose bold trading strategies",
                    "Maximize profit potential"
                ]
            ),
            "shadow": DialecticPersona(
                name="Shadow Agent",
                role="Antithesis Generator",
                characteristics=[
                    "Cynical risk manager",
                    "Pessimistic contrarian",
                    "Focused on capital preservation"
                ],
                objectives=[
                    "Identify flaws in Core proposals",
                    "Highlight liquidity risks",
                    "Prevent catastrophic losses"
                ]
            )
        }
        
        # Conditioning vectors for persona-specific prompting
        self.conditioning_vectors = {
            "core": "أنت مستكشف فرص تفاؤلي. تحب المخاطرة المحسوبة.",
            "shadow": "أنت ناقد متشائم. مهمتك إيجاد نقاط الفشل."
        }
    
    async def generate_dialectic(self, market_data: Dict[str, Any]) -> DialecticSynthesis:
        """
        Run the dialectic process within a single GLM-4.6 inference pass.
        
        Args:
            market_data: Comprehensive market context including price, orderbook, news, etc.
            
        Returns:
            DialecticSynthesis containing the complete dialectic process and final decision
        """
        # Construct the dialectic prompt with persona conditioning
        prompt = self._construct_dialectic_prompt(market_data)
        
        # In a real implementation, this would call the GLM-4.6 API
        # For now, we'll simulate the response
        response = await self._call_model(prompt)
        
        # Parse the structured response
        return self._parse_dialectic_response(response, market_data)
    
    def _construct_dialectic_prompt(self, market_data: Dict[str, Any]) -> str:
        """
        Construct a prompt that forces the model to engage in internal dialectic.
        
        Args:
            market_data: Market context data
            
        Returns:
            Formatted prompt string
        """
        return f"""
You are the AlphaAxiom Dialectic Engine. You will generate a trading decision by simulating a debate between two expert personas.

CONTEXT:
{json.dumps(market_data, indent=2)}

PHASE 1: CORE (The Thesis)
Analyze the provided market context to identify a high-conviction trade setup. 
You are aggressive, optimistic, and focused on maximizing Alpha.
Respond in JSON format:
{{
    "persona": "Core Agent",
    "argument": "Detailed thesis argument",
    "confidence": 0.0-1.0,
    "supporting_evidence": ["evidence1", "evidence2"]
}}

PHASE 2: SHADOW (The Antithesis)
Review the Core's proposal. You are the Risk Manager. You are cynical, pessimistic, and focused on capital preservation.
Identify every flaw, liquidity risk, and macro headwind ignored by the Core.
Respond in JSON format:
{{
    "persona": "Shadow Agent",
    "argument": "Detailed counter-argument",
    "confidence": 0.0-1.0,
    "supporting_evidence": ["risk1", "risk2"]
}}

PHASE 3: SYNTHESIS
Synthesize these views into a final recommendation with an execution weight (0.0-1.0).
Respond in JSON format:
{{
    "synthesis": "Combined recommendation",
    "execution_weight": 0.0-1.0,
    "tool_calls": [
        {{
            "function": "check_orderbook_depth",
            "parameters": {{"symbol": "BTCUSDT", "price_level": 98000}}
        }}
    ]
}}
"""
    
    async def _call_model(self, prompt: str) -> Dict[str, Any]:
        """
        Call the foundation model (GLM-4.6) with the dialectic prompt.
        
        Args:
            prompt: Formatted prompt string
            
        Returns:
            Model response as dictionary
        """
        # In a real implementation, this would call the Zhipu AI GLM-4.6 API
        # For simulation purposes, we'll return a mock response
        return {
            "phase_1": {
                "persona": "Core Agent",
                "argument": "Strong bullish momentum detected with RSI oversold bounce and increasing volume",
                "confidence": 0.85,
                "supporting_evidence": [
                    "RSI(14) = 28.5 (oversold)",
                    "Volume 150% above 20-day average",
                    "Breaking resistance at $95000"
                ]
            },
            "phase_2": {
                "persona": "Shadow Agent",
                "argument": "High risk of whipsaw at resistance level with thin orderbook above",
                "confidence": 0.75,
                "supporting_evidence": [
                    "Resistance at $95000 with only 5 BTC liquidity",
                    "Recent history of false breakouts",
                    "High funding rates suggest long liquidation risk"
                ]
            },
            "phase_3": {
                "synthesis": "Enter long position with tight stop-loss below $94000 and take-profit at $96000",
                "execution_weight": 0.65,
                "tool_calls": [
                    {
                        "function": "check_orderbook_depth",
                        "parameters": {"symbol": "BTCUSDT", "price_level": 96000}
                    }
                ]
            }
        }
    
    def _parse_dialectic_response(self, response: Dict[str, Any], market_data: Dict[str, Any]) -> DialecticSynthesis:
        """
        Parse the model response into a structured dialectic synthesis.
        
        Args:
            response: Raw model response
            market_data: Original market data for metadata
            
        Returns:
            DialecticSynthesis object
        """
        phase_1 = response.get("phase_1", {})
        phase_2 = response.get("phase_2", {})
        phase_3 = response.get("phase_3", {})
        
        core_thesis = DialecticArgument(
            persona=phase_1.get("persona", "Core Agent"),
            argument=phase_1.get("argument", ""),
            confidence=phase_1.get("confidence", 0.5),
            supporting_evidence=phase_1.get("supporting_evidence", [])
        )
        
        shadow_antithesis = DialecticArgument(
            persona=phase_2.get("persona", "Shadow Agent"),
            argument=phase_2.get("argument", ""),
            confidence=phase_2.get("confidence", 0.5),
            supporting_evidence=phase_2.get("supporting_evidence", [])
        )
        
        return DialecticSynthesis(
            core_thesis=core_thesis,
            shadow_antithesis=shadow_antithesis,
            final_synthesis=phase_3.get("synthesis", ""),
            execution_weight=phase_3.get("execution_weight", 0.5),
            tool_calls=phase_3.get("tool_calls", []),
            metadata={
                "model": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "market_context": market_data
            }
        )
    
    def _condition_prompt(self, persona: str, market_data: Dict[str, Any]) -> str:
        """
        Apply conditioning to the prompt based on the persona.
        
        Args:
            persona: Persona identifier ("core" or "shadow")
            market_data: Market context data
            
        Returns:
            Conditioned prompt string
        """
        base_prompt = f"""
{self.conditioning_vectors.get(persona, "")}

Market Context:
{json.dumps(market_data, indent=2)}

Provide your analysis focusing on your specific role and objectives.
"""
        return base_prompt