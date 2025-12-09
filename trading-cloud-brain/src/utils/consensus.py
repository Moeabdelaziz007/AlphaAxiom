# ========================================
# 🤝 AXIOM CONSENSUS ENGINE
# ========================================
# Requires agreement from multiple agents before critical actions.
# Avoids single-point failures or hallucinations.
#
# Logic:
#   - Aggregates "votes" from different agents.
#   - Calculates a "Confidence Score" (0-100).
#   - Enforces a threshold (e.g. 75) for executing trades.
# ========================================

class ConsensusEngine:
    def __init__(self, env):
        self.env = env
        self.votes = {}

    def add_vote(self, agent: str, signal: str, weight: int = 1):
        """
        Register a vote from an agent.
        Signal: 'BUY', 'SELL', 'NEUTRAL'
        """
        self.votes[agent] = {
            "signal": signal,
            "weight": weight
        }

    async def reached_consensus(self) -> dict:
        """
        Calculate if consensus is reached.
        Returns: { 'action': 'UY', 'confidence': 85 } or None
        """
        score_buy = 0
        score_sell = 0
        total_weight = 0
        
        for agent, data in self.votes.items():
            w = data['weight']
            total_weight += w
            
            if data['signal'] == 'BUY':
                score_buy += w
            elif data['signal'] == 'SELL':
                score_sell += w
                
        # Calculate percentages
        buy_conf = (score_buy / total_weight) * 100 if total_weight > 0 else 0
        sell_conf = (score_sell / total_weight) * 100 if total_weight > 0 else 0
        
        # Threshold: 60% agreement required
        if buy_conf >= 60:
            return {"action": "BUY", "confidence": buy_conf, "votes": self.votes}
        elif sell_conf >= 60:
            return {"action": "SELL", "confidence": sell_conf, "votes": self.votes}
            
        return {"action": "NEUTRAL", "confidence": max(buy_conf, sell_conf), "votes": self.votes}

# ========================================
# 🏭 Factory
# ========================================
def get_consensus_engine(env):
    return ConsensusEngine(env)
