"""
Test script for Phase 3: AI Signal Generation
Run with: python test_ai_signals.py
"""

import asyncio
import json


async def test_ai_signal_generation():
    """Test AI signal generation commands"""
    
    print("🧠 Testing Phase 3: AI Signal Generation...")
    print("-" * 50)
    
    host = "127.0.0.1"
    port = 19284
    
    # Test 1: Check AI status
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        command = json.dumps({"command": "GET_STATUS", "payload": {}}) + "\n"
        writer.write(command.encode())
        await writer.drain()
        
        response = await reader.readline()
        result = json.loads(response.decode())
        
        print(f"✅ GET_STATUS Response:")
        if result.get('result'):
            status = result['result']
            print(f"   - Trading Active: {status.get('trading_active')}")
            print(f"   - Connected: {status.get('connected')}")
            print(f"   - Skills Loaded: {status.get('skills_loaded')}")
            print(f"   - AI Enabled: {status.get('ai_enabled')}")
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"❌ GET_STATUS failed: {e}")
        return False
    
    # Test 2: Generate Signal
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        command = json.dumps({
            "command": "GENERATE_SIGNAL",
            "payload": {"symbol": "BTC/USDT"}
        }) + "\n"
        writer.write(command.encode())
        await writer.drain()
        
        response = await reader.readline()
        result = json.loads(response.decode())
        
        print(f"\n✅ GENERATE_SIGNAL Response:")
        if result.get('result'):
            signal = result['result']
            print(f"   - Symbol: {signal.get('symbol')}")
            print(f"   - Action: {signal.get('action')}")
            print(f"   - Confidence: {signal.get('confidence', 0):.2%}")
            print(f"   - Entry Price: {signal.get('entry_price')}")
            print(f"   - Stop Loss: {signal.get('stop_loss')}")
            print(f"   - Take Profit: {signal.get('take_profit')}")
            print(f"   - Reasoning: {signal.get('reasoning', 'N/A')[:100]}...")
        elif result.get('error'):
            print(f"   ⚠️ {result['error']}")
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"❌ GENERATE_SIGNAL failed: {e}")
        return False
    
    # Test 3: Reload Skills
    try:
        reader, writer = await asyncio.open_connection(host, port)
        
        command = json.dumps({"command": "RELOAD_SKILLS", "payload": {}}) + "\n"
        writer.write(command.encode())
        await writer.drain()
        
        response = await reader.readline()
        result = json.loads(response.decode())
        
        print(f"\n✅ RELOAD_SKILLS Response:")
        if result.get('result'):
            reload_result = result['result']
            print(f"   - Status: {reload_result.get('status')}")
            print(f"   - Old Count: {reload_result.get('old_count')}")
            print(f"   - New Count: {reload_result.get('new_count')}")
        
        writer.close()
        await writer.wait_closed()
        
    except Exception as e:
        print(f"❌ RELOAD_SKILLS failed: {e}")
        return False
    
    print("\n" + "-" * 50)
    print("🎉 Phase 3 AI Signal Generation tests complete!")
    return True


if __name__ == "__main__":
    asyncio.run(test_ai_signal_generation())
