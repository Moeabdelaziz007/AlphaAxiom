# ========================================
# 🛡️ AXIOM CIRCUIT BREAKER - Resilience Layer
# ========================================
# Prevents cascading failures when external APIs are down.
# Uses Cloudflare KV to persist state across worker invocations.
#
# Logic:
#   - If failures > threshold: Open circuit (stop calling)
#   - After timeout: Half-open (try once)
#   - If success: Close circuit (reset)
# ========================================

import json
import time

class CircuitBreaker:
    def __init__(self, env, service_name: str, failure_threshold: int = 3, reset_timeout: int = 300):
        self.env = env
        self.service = service_name
        self.threshold = failure_threshold
        self.timeout = reset_timeout
        self.kv_key = f"CB_STATE_{service_name}"
        
    async def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        """
        # 1. Check Circuit State
        state = await self._get_state()
        
        if state['status'] == 'OPEN':
            if time.time() > state['retry_after']:
                # Half-Open: Allow one trial
                print(f"I️ Circuit {self.service} HALF-OPEN: Retrying...")
            else:
                # Circuit Open: Fail fast
                print(f"🚫 Circuit {self.service} OPEN: Skipped")
                return None
        
        # 2. Attempt Execution
        try:
            result = await func(*args, **kwargs)
            
            # Success: Reset if needed
            if state['failures'] > 0:
                await self._reset_circuit()
                
            return result
            
        except Exception as e:
            # Failure: Record it
            await self._record_failure(state, str(e))
            raise e

    async def _get_state(self):
        """Get current state from KV."""
        try:
            raw = await self.env.BRAIN_MEMORY.get(self.kv_key)
            if raw:
                return json.loads(raw)
        except:
            pass
            
        return {
            "status": "CLOSED",
            "failures": 0,
            "last_failure": 0,
            "retry_after": 0
        }
        
    async def _record_failure(self, state, error):
        """Update failure count and potentially open circuit."""
        failures = state['failures'] + 1
        status = "CLOSED"
        retry_after = 0
        
        if failures >= self.threshold:
            status = "OPEN"
            retry_after = time.time() + self.timeout
            print(f"💥 Circuit {self.service} TRIPPED! Open for {self.timeout}s")
            
        new_state = {
            "status": status,
            "failures": failures,
            "last_failure": time.time(),
            "retry_after": retry_after,
            "last_error": error
        }
        
        # Save to KV (1 hour TTL)
        await self.env.BRAIN_MEMORY.put(self.kv_key, json.dumps(new_state), expiration_ttl=3600)

    async def _reset_circuit(self):
        """Reset circuit to closed state."""
        await self.env.BRAIN_MEMORY.delete(self.kv_key)
        print(f"✅ Circuit {self.service} RECOVERED")

# ========================================
# 🏭 Factory
# ========================================
def get_circuit_breaker(env, service_name):
    return CircuitBreaker(env, service_name)
