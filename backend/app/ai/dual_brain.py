# backend/app/ai/dual_brain.py
# ==============================================
# DUAL-CORE TRADING BRAIN (العقل ثنائي النواة)
# DeepSeek (Strategist) + Gemini (Executor)
# ==============================================

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False


class DualBrain:
    """
    العقل المزدوج للتداول:
    - DeepSeek: التحليل الاستراتيجي العميق (كل ساعة)
    - Gemini: التنفيذ السريع والدردشة
    """
    
    def __init__(self):
        self.strategy_cache_file = "strategy_cache.json"
        self.fast_brain = None
        self.deep_brain = None
        
        # إعداد Gemini (Fast Brain)
        if GEMINI_AVAILABLE:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                genai.configure(api_key=gemini_key)
                self.fast_brain = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini (Fast Brain): ONLINE")
        
        # إعداد DeepSeek (Deep Brain)
        if DEEPSEEK_AVAILABLE:
            deepseek_key = os.getenv("DEEPSEEK_API_KEY")
            if deepseek_key:
                self.deep_brain = OpenAI(
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com/v1"
                )
                print("✅ DeepSeek (Deep Brain): ONLINE")
    
    def get_status(self) -> Dict[str, Any]:
        """حالة العقل المزدوج"""
        return {
            "gemini": "ONLINE" if self.fast_brain else "OFFLINE",
            "deepseek": "ONLINE" if self.deep_brain else "OFFLINE",
            "strategy_loaded": os.path.exists(self.strategy_cache_file),
            "last_update": datetime.now().isoformat()
        }
    
    # ==============================================
    # DEEPSEEK: Deep Strategic Analysis
    # ==============================================
    
    async def generate_strategy_report(self, market_data: Dict) -> Dict:
        """
        🧠 DeepSeek: التحليل الاستراتيجي العميق
        يعمل في الخلفية كل ساعة
        """
        print("🧠 DEEPSEEK: Analyzing market patterns...")
        
        if not self.deep_brain:
            # Fallback to mock strategy
            return self._mock_strategy()
        
        prompt = f"""
        You are a quantitative trading strategist. Analyze this market data:
        
        {json.dumps(market_data, indent=2)}
        
        Perform the following analysis:
        1. Identify the current TREND (Bullish/Bearish/Neutral)
        2. Calculate key Support and Resistance levels
        3. Assess the RISK level (1-10)
        4. Determine the optimal trading BIAS for the next 24 hours
        
        Output ONLY a valid JSON object with this structure:
        {{
            "timestamp": "ISO-8601",
            "bias": "BULLISH" or "BEARISH" or "NEUTRAL",
            "risk_level": 1-10,
            "confidence": 0-100,
            "key_levels": {{
                "resistance": [list of prices],
                "support": [list of prices]
            }},
            "recommended_action": "BUY" or "SELL" or "HOLD",
            "reasoning": "Brief explanation"
        }}
        """
        
        try:
            response = self.deep_brain.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0  # دقة عالية، لا إبداع
            )
            
            strategy_text = response.choices[0].message.content
            # تنظيف الـ JSON
            if "```json" in strategy_text:
                strategy_text = strategy_text.split("```json")[1].split("```")[0]
            elif "```" in strategy_text:
                strategy_text = strategy_text.split("```")[1].split("```")[0]
            
            strategy = json.loads(strategy_text.strip())
            strategy["source"] = "DeepSeek-V3"
            strategy["generated_at"] = datetime.now().isoformat()
            
            # حفظ الاستراتيجية
            with open(self.strategy_cache_file, "w") as f:
                json.dump(strategy, f, indent=2)
            
            print(f"✅ DEEPSEEK Strategy: {strategy['bias']} (Confidence: {strategy.get('confidence', 'N/A')}%)")
            return strategy
            
        except Exception as e:
            print(f"❌ DeepSeek Error: {e}")
            return self._mock_strategy()
    
    def _mock_strategy(self) -> Dict:
        """استراتيجية افتراضية للـ Demo"""
        strategy = {
            "timestamp": datetime.now().isoformat(),
            "bias": "BULLISH",
            "risk_level": 4,
            "confidence": 72,
            "key_levels": {
                "resistance": [100000, 102000, 105000],
                "support": [95000, 93000, 90000]
            },
            "recommended_action": "BUY",
            "reasoning": "Strong momentum detected. Antigravity score above 70%.",
            "source": "Mock-Demo"
        }
        with open(self.strategy_cache_file, "w") as f:
            json.dump(strategy, f, indent=2)
        return strategy
    
    def load_strategy(self) -> Optional[Dict]:
        """تحميل الاستراتيجية المحفوظة"""
        try:
            with open(self.strategy_cache_file, "r") as f:
                return json.load(f)
        except:
            return None
    
    # ==============================================
    # GEMINI: Fast Execution & Chat
    # ==============================================
    
    async def chat_and_execute(
        self, 
        user_input: str, 
        live_price: float,
        symbol: str = "BTC/USD"
    ) -> Dict[str, Any]:
        """
        ⚡ Gemini: الرد السريع والتنفيذ
        """
        print(f"⚡ GEMINI: Processing command: '{user_input}'")
        
        # 1. قراءة استراتيجية DeepSeek
        strategy = self.load_strategy()
        strategy_brief = json.dumps(strategy, indent=2) if strategy else "No strategy available."
        
        # 2. بناء الـ Prompt
        system_prompt = f"""
        You are the SENTINEL AI Executor in the Antigravity Trading Terminal.
        
        [STRATEGIC BRIEF FROM DEEPSEEK]:
        {strategy_brief}
        
        [LIVE MARKET DATA]:
        Symbol: {symbol}
        Current Price: ${live_price:,.2f}
        
        [USER COMMAND]:
        "{user_input}"
        
        RULES:
        1. If user wants to TRADE, check alignment with DeepSeek's strategy
        2. If aligned, confirm with: action="trade_confirm", provide trade details
        3. If NOT aligned, WARN the user but allow if they insist
        4. For analysis questions, use DeepSeek's data
        5. Be concise, professional, and use trading terminology
        
        Respond in JSON format:
        {{
            "reply": "Your message to user",
            "action": "none" or "trade_confirm",
            "strategy_aligned": true/false,
            "trade": {{"symbol": "", "side": "", "qty": 0, "price": 0}} or null
        }}
        """
        
        if self.fast_brain:
            try:
                response = self.fast_brain.generate_content(system_prompt)
                result_text = response.text
                
                # تنظيف الـ JSON
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0]
                
                return json.loads(result_text.strip())
                
            except Exception as e:
                print(f"❌ Gemini Error: {e}")
        
        # Fallback to intelligent mock
        return self._mock_chat_response(user_input, live_price, strategy)
    
    def _mock_chat_response(
        self, 
        user_input: str, 
        live_price: float, 
        strategy: Optional[Dict]
    ) -> Dict:
        """رد ذكي للـ Demo"""
        q = user_input.lower()
        bias = strategy.get("bias", "NEUTRAL") if strategy else "NEUTRAL"
        
        if "buy" in q or "شراء" in q:
            aligned = bias == "BULLISH"
            return {
                "reply": f"📊 Analysis: DeepSeek recommends {bias}. {'✅ Trade ALIGNED with strategy!' if aligned else '⚠️ WARNING: Strategy is NOT bullish.'}",
                "action": "trade_confirm",
                "strategy_aligned": aligned,
                "trade": {
                    "symbol": "BTC/USD",
                    "side": "buy",
                    "qty": 0.01,
                    "price": live_price,
                    "sl": live_price * 0.98,
                    "tp": live_price * 1.05
                }
            }
        
        if "sell" in q or "بيع" in q:
            aligned = bias == "BEARISH"
            return {
                "reply": f"📊 Analysis: DeepSeek recommends {bias}. {'✅ Trade ALIGNED!' if aligned else '⚠️ Strategy is NOT bearish.'}",
                "action": "trade_confirm",
                "strategy_aligned": aligned,
                "trade": {
                    "symbol": "BTC/USD",
                    "side": "sell",
                    "qty": 0.01,
                    "price": live_price,
                    "sl": live_price * 1.02,
                    "tp": live_price * 0.95
                }
            }
        
        if "strategy" in q or "استراتيجية" in q:
            return {
                "reply": f"🧠 Current DeepSeek Strategy:\n• Bias: {bias}\n• Confidence: {strategy.get('confidence', 'N/A')}%\n• Risk Level: {strategy.get('risk_level', 'N/A')}/10\n• Action: {strategy.get('recommended_action', 'HOLD')}",
                "action": "none",
                "strategy_aligned": True,
                "trade": None
            }
        
        return {
            "reply": f"📈 Market Status:\n• Price: ${live_price:,.2f}\n• DeepSeek Bias: {bias}\n• Ask me: 'Buy BTC', 'Sell', or 'What's the strategy?'",
            "action": "none",
            "strategy_aligned": True,
            "trade": None
        }


# ==============================================
# BACKGROUND STRATEGY UPDATER
# ==============================================

async def run_strategy_updater(brain: DualBrain, interval_seconds: int = 3600):
    """
    تحديث الاستراتيجية في الخلفية كل ساعة
    """
    while True:
        print(f"\n🔄 [Strategy Update] Running DeepSeek analysis...")
        
        # بيانات السوق (في النظام الحقيقي، جلبها من API)
        mock_market_data = {
            "symbol": "BTC/USD",
            "prices_24h": [97000, 97500, 98000, 98200, 98500, 98400, 98300],
            "volume_24h": 1500000000,
            "high_24h": 99000,
            "low_24h": 96500,
            "current_price": 98500
        }
        
        await brain.generate_strategy_report(mock_market_data)
        print(f"✅ Strategy updated. Next update in {interval_seconds/60} minutes.")
        
        await asyncio.sleep(interval_seconds)


# ==============================================
# SINGLETON INSTANCE
# ==============================================

dual_brain = DualBrain()
