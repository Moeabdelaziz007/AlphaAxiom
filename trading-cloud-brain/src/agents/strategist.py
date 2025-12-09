# ========================================
# 🧠 AXIOM STRATEGIST AGENT - The "Thinker"
# ========================================
# Implements "Sequential Thinking" pattern.
# Runs Hourly (Heartbeat: 1h).
#
# Role:
#   - Synthesize data from Journalist (News) & Market (Price)
#   - Formulate high-level strategy (Offense vs Defense)
#   - Adjust Global System Risk Settings
# ========================================

import json
from js import fetch, Headers

class StrategistAgent:
    """
    The Strategist - High-level reasoning engine.
    Uses DeepSeek-R1 (via Groq) to simulate 'Sequential Thinking' MCP.
    """
    
    def __init__(self, env):
        self.env = env
        self.api_key = getattr(env, 'GROQ_API_KEY', '')
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "deepseek-r1-distill-llama-70b" # Powerful reasoning model
        
    async def run_mission(self):
        """
        Execute Hourly Strategy Review.
        """
        print("🧠 Strategist Mission Started...")
        
        # 1. Gather Intelligence (Market State)
        # In a real scenario, this would read from KV or D1
        # For now, we simulate the state or pass it in
        market_state = {
            "btc_price": "98000",
            "trend": "BULLISH",
            "volatility": "HIGH",
            "fear_greed": 75
        }
        
        # 2. Sequential Thinking Process
        strategy = await self._think_deep(market_state)
        
        # 3. Apply Conclusions
        if strategy:
            await self._apply_strategy(strategy)
            return strategy
            
        return None

    async def _think_deep(self, state):
        """
        Simulate Sequential Thinking MCP.
        """
        if not self.api_key:
            print("🧠 Strategist skipped: No GROQ_API_KEY")
            return None
            
        prompt = f"""
        You are the Chief Strategist of AXIOM Hedge Fund.
        
        CURRENT STATE:
        {json.dumps(state, indent=2)}
        
        TASK:
        Perform a sequential analysis to determine our trading stance for the next 4 hours.
        
        STEPS:
        1. Analyze Market Structure (Trend vs Volatility)
        2. Assess Risk Factors (External news, manipulation)
        3. Determine Stance (Aggressive, Neutral, Defensive)
        4. Recommend Actions (Leverage adjustment, Asset allocation)
        
        OUTPUT JSON:
        {{
            "thought_process": ["step 1...", "step 2..."],
            "stance": "DEFENSIVE" | "NEUTRAL" | "AGGRESSIVE",
            "recommended_leverage": integer,
            "risk_adjustment": float (0.5 to 1.5 multiplier),
            "reasoning": "brief summary"
        }}
        """
        
        try:
            payload = json.dumps({
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a strategic reasoning engine. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.6,
                "response_format": {"type": "json_object"}
            })
            
            headers = Headers.new({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }.items())
            
            response = await fetch(self.api_url, method="POST", headers=headers, body=payload)
            data = json.loads(await response.text())
            content = data['choices'][0]['message']['content']
            
            return json.loads(content)
            
        except Exception as e:
            print(f"🧠 Thinking failed: {e}")
            return None

    async def _apply_strategy(self, strategy):
        """
        Apply the strategy to the system (e.g., update KV).
        """
        print(f"🧠 New Strategy: {strategy['stance']} (Risk x{strategy['risk_adjustment']})")
        
        # Here we would update the "Global Risk Multiplier" in KV
        # await self.env.BRAIN_MEMORY.put("GLOBAL_RISK", str(strategy['risk_adjustment']))
        pass

# ========================================
# 🏭 Factory
# ========================================
def get_strategist_agent(env):
    return StrategistAgent(env)
