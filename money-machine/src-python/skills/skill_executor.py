"""
AIX Format Skill Executor - Runs trading strategies as skills
Refactored to use Gemini API for decision making
"""

import yaml
import json
import asyncio
from pathlib import Path
from typing import Dict, Optional, List, Any
import logging
import os

logger = logging.getLogger(__name__)


class SkillExecutor:
    """Executes AIX-format trading skills"""
    
    def __init__(self, engine, api_key: str = ""):
        self.engine = engine
        self.api_key = api_key
        self.model = None
        self.loaded_skills: Dict[str, Dict] = {}
        
        # Initialize Gemini if API key provided
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                # Use standard flash model for skills
                model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
                self.model = genai.GenerativeModel(model_name)
                logger.info(f"✅ SkillExecutor using Gemini model: {model_name}")
            except ImportError:
                logger.warning("Google Generative AI SDK not installed. AI skills disabled.")
        
        # Load skills from repository
        self._load_skills()
    
    def _load_skills(self):
        """Load AIX format skills from ./skills directory"""
        skills_dir = Path(__file__).parent
        
        # Load .aix files
        for skill_file in skills_dir.glob("*.aix"):
            try:
                skill = self._parse_aix_file(skill_file)
                if skill:
                    self.loaded_skills[skill['name']] = skill
                    logger.info(f"Loaded skill: {skill['name']}")
            except Exception as e:
                logger.error(f"Error loading skill {skill_file}: {e}")
        
        # Load .yaml files
        for skill_file in skills_dir.glob("*.yaml"):
            if skill_file.name == "example_skill.yaml":
                continue  # Skip example
            try:
                skill = self._parse_aix_file(skill_file)
                if skill:
                    self.loaded_skills[skill['name']] = skill
                    logger.info(f"Loaded skill: {skill['name']}")
            except Exception as e:
                logger.error(f"Error loading skill {skill_file}: {e}")
    
    def _parse_aix_file(self, filepath: Path) -> Optional[Dict]:
        """Parse AIX format YAML"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Handle YAML frontmatter format
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    frontmatter = yaml.safe_load(parts[1])
                    if frontmatter:
                        frontmatter['_raw_content'] = parts[2] if len(parts) > 2 else ""
                        return frontmatter
            
            # Plain YAML
            return yaml.safe_load(content)
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            return None
    
    async def execute_skill(self, skill_name: str, params: Dict) -> Dict:
        """Execute a skill with given parameters"""
        if skill_name not in self.loaded_skills:
            return {"error": f"Skill '{skill_name}' not found"}
        
        skill = self.loaded_skills[skill_name]
        
        try:
            # Get market context
            symbol = params.get('symbol', 'BTC/USDT')
            market_data = await self.engine.get_market_data(symbol)
            
            # If AI is available and skill has a system prompt
            if self.model and 'system_prompt' in skill:
                decision = await self._get_ai_decision(skill, market_data, params)
                return decision
            
            # Otherwise, use rule-based execution from skill
            return await self._rule_based_execution(skill, market_data, params)
        
        except Exception as e:
            logger.error(f"Skill execution error: {e}")
            return {"error": str(e)}
    
    async def _get_ai_decision(self, skill: Dict, market_data: List, params: Dict) -> Dict:
        """Get trading decision from Gemini API"""
        try:
            # Build prompt
            system_prompt = skill['system_prompt']
            
            # Add market context
            portfolio_state = {
                "balance": self.engine.portfolio.get_balance(),
                "positions": self.engine.portfolio.get_positions()
            }
            
            user_message = f"""{system_prompt}

Market Data (last 5 candles): {json.dumps(market_data[-5:] if market_data else [])}

Portfolio State: {json.dumps(portfolio_state)}

Based on the above data and your strategy rules, make a trading decision.
Respond with a strict JSON object containing:
- decision: "BUY", "SELL", or "HOLD"
- confidence: 0.0 to 1.0
- reason: brief explanation
- params: {{amount, price}} if applicable
"""
            
            # Call Gemini API
            response = await asyncio.to_thread(
                self.model.generate_content,
                user_message,
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Parse response
            response_text = response.text
            
            try:
                decision = json.loads(response_text)
                return decision
            except json.JSONDecodeError:
                # Try soft parsing
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    decision = json.loads(json_match.group())
                    return decision
            
            return {
                "decision": "HOLD",
                "confidence": 0.5,
                "reason": response_text[:100],
                "raw_response": True
            }
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"error": str(e), "decision": "HOLD"}
    
    async def _rule_based_execution(self, skill: Dict, market_data: List, params: Dict) -> Dict:
        """Execute skill using rule-based logic"""
        # Default rule-based response
        return {
            "decision": "HOLD",
            "confidence": 0.5,
            "reason": "Rule-based execution (AI not available)",
            "skill": skill.get('name', 'unknown')
        }
    
    def reload_skills(self):
        """Reload all skills from disk"""
        self.loaded_skills.clear()
        self._load_skills()
