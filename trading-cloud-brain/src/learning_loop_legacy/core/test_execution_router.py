"""
Test file for ExecutionRouter functionality in CausalLearningBridge
"""

import asyncio
from learning_loop_v2.core.causal_bridge import CausalLearningBridge


async def test_execution_router():
    """Test the ExecutionRouter functionality."""
    print("Testing ExecutionRouter...")
    
    # Create an instance of CausalLearningBridge
    bridge = CausalLearningBridge()
    
    # Test getting best price
    print("\n1. Testing get_best_price...")
    try:
        result = await bridge.get_best_price("BTCUSDT", "buy")
        print(f"Best price result: {result}")
    except Exception as e:
        print(f"Error getting best price: {e}")
    
    # Test user preferences
    print("\n2. Testing get_user_preferences...")
    try:
        prefs = await bridge.get_user_preferences("test_user")
        print(f"User preferences: {prefs}")
    except Exception as e:
        print(f"Error getting user preferences: {e}")
    
    # Test execution with preferences
    print("\n3. Testing execute_with_preferences...")
    try:
        result = await bridge.execute_with_preferences(
            "BTCUSDT", "buy", 0.001, "test_user")
        print(f"Execution with preferences result: {result}")
    except Exception as e:
        print(f"Error executing with preferences: {e}")
    
    print("\nExecutionRouter tests completed.")


if __name__ == "__main__":
    asyncio.run(test_execution_router())