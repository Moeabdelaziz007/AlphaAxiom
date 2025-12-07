"""
🆓 Cloudflare Workers AI - FREE LLM Layer for Axiom Antigravity
The ultimate backup brain - 10,000 FREE neurons per day!

RESEARCH-BASED IMPLEMENTATION:
- 10K neurons/day FREE (resets 00:00 UTC)
- Llama 3.2 1B: ~2,500 neurons/request = ~4 free requests/day
- Beta models: UNLIMITED and FREE
- No external API key needed - uses env.AI binding

MODELS AVAILABLE:
- @cf/meta/llama-3.2-1b-instruct (fastest, cheapest)
- @cf/meta/llama-3.2-3b-instruct (balanced)
- @cf/mistral/mistral-7b-instruct-v0.1 (powerful)
- @cf/meta/llama-3.1-8b-instruct (beta - FREE)

USAGE:
    ai = WorkersAI(env)
    result = await ai.chat("Analyze EURUSD trend")
    result = await ai.analyze_sentiment("Fed raises rates")
"""

import json
from js import fetch, Headers

# Available Cloudflare Workers AI models
MODELS = {
    "llama-3.2-1b": "@cf/meta/llama-3.2-1b-instruct",      # Fast, cheap
    "llama-3.2-3b": "@cf/meta/llama-3.2-3b-instruct",      # Balanced
    "llama-3.1-8b": "@cf/meta/llama-3.1-8b-instruct",      # Beta (FREE!)
    "mistral-7b": "@cf/mistral/mistral-7b-instruct-v0.1",  # Powerful
}

# REST API endpoint (fallback if binding not available)
WORKERS_AI_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"


class WorkersAI:
    """
    🆓 Cloudflare Workers AI Client
    
    FREE tier: 10,000 neurons/day
    - Llama 3.2 1B: ~4 requests/day
    - Beta models: UNLIMITED
    
    Usage:
        ai = WorkersAI(env)
        result = await ai.chat("Hello!")
    """
    
    def __init__(self, env):
        self.env = env
        # Check if we have the AI binding (preferred)
        self.has_binding = hasattr(env, 'AI')
        # Get account ID and API token for REST fallback
        self.account_id = str(getattr(env, 'CF_ACCOUNT_ID', ''))
        self.api_token = str(getattr(env, 'CF_API_TOKEN', ''))
        self.default_model = "llama-3.1-8b"  # Use beta model (FREE!)
    
    async def _invoke_via_binding(self, model: str, messages: list) -> dict:
        """Invoke model using Workers AI binding (fastest)"""
        try:
            model_id = MODELS.get(model, MODELS[self.default_model])
            
            # Format for Workers AI
            prompt = "\n".join([
                f"{m['role'].upper()}: {m['content']}" 
                for m in messages
            ])
            
            # Use the AI binding
            response = await self.env.AI.run(model_id, {
                "prompt": prompt,
                "max_tokens": 1024,
                "temperature": 0.3
            })
            
            return {
                "content": response.get("response", ""),
                "model": model_id,
                "source": "workers_ai_binding",
                "cost": 0.00
            }
        except Exception as e:
            return {"error": str(e), "content": None}
    
    async def _invoke_via_rest(self, model: str, messages: list) -> dict:
        """Invoke model using REST API (fallback)"""
        try:
            if not self.account_id or not self.api_token:
                return {"error": "CF_ACCOUNT_ID and CF_API_TOKEN required for REST API", "content": None}
            
            model_id = MODELS.get(model, MODELS[self.default_model])
            url = WORKERS_AI_URL.format(account_id=self.account_id, model=model_id)
            
            headers = Headers.new({
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }.items())
            
            # Format prompt
            prompt = "\n".join([
                f"{m['role'].upper()}: {m['content']}" 
                for m in messages
            ])
            
            response = await fetch(
                url,
                method="POST",
                headers=headers,
                body=json.dumps({
                    "prompt": prompt,
                    "max_tokens": 1024
                })
            )
            
            if response.ok:
                data = json.loads(await response.text())
                result = data.get("result", {})
                return {
                    "content": result.get("response", ""),
                    "model": model_id,
                    "source": "workers_ai_rest",
                    "cost": 0.00
                }
            else:
                error_text = await response.text()
                return {"error": f"API error: {error_text[:200]}", "content": None}
                
        except Exception as e:
            return {"error": str(e), "content": None}
    
    async def chat(self, message: str, model: str = None, system_prompt: str = None) -> dict:
        """
        Simple chat completion.
        
        Args:
            message: User message
            model: Model to use (default: llama-3.1-8b)
            system_prompt: Optional system prompt
        
        Returns:
            dict with content, model, source, cost
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        model = model or self.default_model
        
        # Try binding first, then REST
        if self.has_binding:
            return await self._invoke_via_binding(model, messages)
        else:
            return await self._invoke_via_rest(model, messages)
    
    async def analyze_sentiment(self, text: str) -> dict:
        """
        Quick sentiment analysis using Workers AI.
        
        Args:
            text: Text to analyze
        
        Returns:
            dict with sentiment, confidence
        """
        system_prompt = """You are a financial sentiment analyzer. 
Respond ONLY with JSON: {"sentiment": "BULLISH" | "BEARISH" | "NEUTRAL", "confidence": 0-100}"""
        
        result = await self.chat(
            message=f"Analyze this text: {text}",
            system_prompt=system_prompt
        )
        
        if result.get("content"):
            try:
                # Try to parse JSON from response
                content = result["content"]
                if "{" in content:
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    parsed = json.loads(json_str)
                    result["parsed"] = parsed
            except:
                pass
        
        return result
    
    async def quick_decision(self, market_data: str) -> dict:
        """
        Quick trading decision for time-sensitive situations.
        Uses the fastest/cheapest model.
        
        Args:
            market_data: Brief market context
        
        Returns:
            dict with action, confidence
        """
        system_prompt = """You are a rapid trading decision maker.
Respond ONLY with JSON: {"action": "BUY" | "SELL" | "HOLD", "confidence": 0-100, "reason": "brief reason"}"""
        
        result = await self.chat(
            message=f"Quick decision for: {market_data}",
            model="llama-3.2-1b",  # Fastest
            system_prompt=system_prompt
        )
        
        if result.get("content"):
            try:
                content = result["content"]
                if "{" in content:
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    parsed = json.loads(json_str)
                    result["parsed"] = parsed
            except:
                pass
        
        return result
    
    def get_model_info(self) -> dict:
        """Get available model information"""
        return {
            "available_models": list(MODELS.keys()),
            "has_binding": self.has_binding,
            "has_rest_credentials": bool(self.account_id and self.api_token),
            "free_tier": {
                "neurons_per_day": 10000,
                "llama_3.2_1b_requests": 4,
                "beta_models": "UNLIMITED"
            }
        }
